import os
import re
import cv2
import pytesseract
from pdf2image import convert_from_path

from .processors.bilan import BilanProcessor
from .processors.facture import FactureProcessor
from .processors.devis import DevisProcessor
from .processors.attestation import AttestationProcessor
from .utils.cleaner import AmountCleaner
from .classifier import MLClassifier

def _load_doctr():
    try:
        from doctr.io import DocumentFile
        from doctr.models import ocr_predictor
        return DocumentFile, ocr_predictor
    except ImportError:
        return None, None

class OCRAnalyzer:
    """
    Multi-engine OCR Analyzer.
    - "tesseract" (default): Fast, lightweight.
    - "doctr": High-accuracy Deep Learning OCR.
    """
    def __init__(self, engine: str = "tesseract"):
        self.engine = engine.lower()
        self.classifier = MLClassifier()
        self.processors = [
            BilanProcessor(),
            FactureProcessor(),
            DevisProcessor(),
            AttestationProcessor()
        ]

        self._doctr_model = None
        if self.engine == "doctr":
            DocumentFile, ocr_predictor = _load_doctr()
            if ocr_predictor is not None:
                self._doctr_model = ocr_predictor(pretrained=True)
                self._DocumentFile = DocumentFile
                from loguru import logger
                logger.info("DocTR model loaded.")
            else:
                from loguru import logger
                logger.warning("DocTR not available, falling back to Tesseract.")
                self.engine = "tesseract"

    def _extract_text_tesseract(self, filepath: str, filename: str) -> str:
        full_text = ""
        if filename.lower().endswith('.pdf'):
            pages = convert_from_path(filepath, dpi=200)
            for page in pages:
                full_text += pytesseract.image_to_string(page, lang="fra") + "\n"
        else:
            img = cv2.imread(filepath)
            full_text = pytesseract.image_to_string(img, lang="fra")
        return full_text

    def _extract_text_doctr(self, filepath: str, filename: str) -> str:
        if self._doctr_model is None:
            return self._extract_text_tesseract(filepath, filename)

        if filename.lower().endswith('.pdf'):
            doc = self._DocumentFile.from_pdf(filepath)
        else:
            doc = self._DocumentFile.from_images(filepath)

        result = self._doctr_model(doc)
        pages_text = []
        for page in result.pages:
            for block in page.blocks:
                for line in block.lines:
                    pages_text.append(" ".join(word.value for word in line.words))
        return "\n".join(pages_text)

    def analyze(self, filepath, filename, element_id):
        from loguru import logger
        full_text = ""
        try:
            if self.engine == "doctr":
                full_text = self._extract_text_doctr(filepath, filename)
            else:
                full_text = self._extract_text_tesseract(filepath, filename)
        except Exception as e:
            logger.error(f"OCR Error: {e}")
            return {"element_id": element_id, "statut": "erreur", "description": "Format non supporté"}

        text_up = full_text.upper()
        clean_tech_text = re.sub(r'[\s\-\.]', '', text_up)
        predicted_type = self.classifier.predict(full_text)

        data = None
        for processor in self.processors:
            proc_name = processor.__class__.__name__.lower().replace("processor", "")
            if predicted_type == proc_name:
                data = processor.process(None, text_up)
                break

        if data is None or (data.get("document_type", "autre") == "autre" and data.get("montant_ttc", 0) == 0):
            all_prices = [AmountCleaner.clean(a) for a in re.findall(r'(\d+[.,]\d{2})', text_up) if len(a.replace(',','').replace('.','')) <= 7]
            val_max = max(all_prices) if all_prices else 0.0
            data = {"document_type": predicted_type if predicted_type != "autre" else "autre", "montant_ttc": val_max}

        result_dict = {
            "element_id": element_id,
            "document_type": data.get("document_type", "autre"),
            "siret": re.search(r'\d{14}', clean_tech_text).group(0) if re.search(r'\d{14}', clean_tech_text) else "N/A",
            "statut": "valide" if data.get("document_type") != "autre" else "anomalie",
            "description": filename,
            "raw_text": full_text,
            "ocr_engine": self.engine
        }

        # Simplified extra fields update
        doc_type = data.get("document_type")
        if doc_type == "facture":
            result_dict.update({"montant_ht": data.get("montant_ht", 0.0), "montant_ttc": data.get("montant_ttc", 0.0)})
        
        return result_dict