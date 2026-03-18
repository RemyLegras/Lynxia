import os
import json
from analyzer import OCRAnalyzer

INPUT_DIR = "files/"  
OUTPUT_JSON = "resultat_analyse_myleasy.json"

def main():
    if not os.path.exists(INPUT_DIR):
        os.makedirs(INPUT_DIR)
        print(f" Dossier '{INPUT_DIR}' créé.")
        return

    analyzer = OCRAnalyzer()
    
    supported_ext = ('.pdf', '.png', '.jpg', '.jpeg')
    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(supported_ext)]
    
    if not files:
        print(" Aucun fichier à analyser.")
        return

    report = []
    print(f"🚀 Analyse de {len(files)} documents (Mode Conservation Activé)...")

    for idx, filename in enumerate(files):
        filepath = os.path.join(INPUT_DIR, filename)
        element_id = idx + 1
        
        try:
            print(f"⏳ [{idx+1}/{len(files)}] Traitement : {filename}")
            
            result_data = analyzer.analyze(filepath, filename, element_id)
            report.append(result_data)
            
            with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=4, ensure_ascii=False)
                
            print(f" Terminé : {result_data['document_type']}")

        except Exception as e:
            print(f" Erreur sur {filename} : {str(e)}")

    print(f"\n✨ Terminé ! Tes fichiers sont toujours dans '{INPUT_DIR}'.")
    print(f" JSON généré : {OUTPUT_JSON}")

if __name__ == "__main__":
    main()