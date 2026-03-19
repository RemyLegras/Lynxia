import os
import random
import cv2
import numpy as np
from PIL import Image
from pdf2image import convert_from_path

def apply_data_augmentation(input_path, output_path):
    """
    Applique du bruit, une rotation aléatoire et un flou gaussien pour 
    simuler un document mal scanné ou pris au smartphone.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Fichier introuvable: {input_path}")
        
    ext = os.path.splitext(input_path)[1].lower()
    
    # 1. Charger l'image ou convertir le PDF
    if ext == '.pdf':
        try:
            pages = convert_from_path(input_path, dpi=200)
            if not pages:
                raise ValueError("PDF vide")
            # On prend la première page pour l'OCR
            image = np.array(pages[0].convert('RGB'))
            # Convert RGB to BGR for OpenCV
            image = image[:, :, ::-1].copy() 
        except Exception as e:
            print(f"Erreur pdf2image: {e}, fallback: copie brute")
            import shutil
            shutil.copy2(input_path, output_path)
            # return the modified path with .png if we didn't fail
            return output_path
    else:
        image = cv2.imread(input_path)
        if image is None:
            raise ValueError(f"Impossible de lire l'image {input_path}")
            
    # 2. Rotation aléatoire (2 à 15 degrés pour simuler un scan de travers)
    sign = random.choice([-1, 1])
    angle = random.uniform(2, 15) * sign
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    image = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    
    # 3. Flou gaussien aléatoire
    blur_kernel = random.choice([3, 5])
    image = cv2.GaussianBlur(image, (blur_kernel, blur_kernel), 0)
    
    # 4. Bruit (Scan grain)
    noise = np.random.normal(0, 15, image.shape).astype(np.uint8)
    image = cv2.add(image, noise)

    # 5. Déformation perspective (Smartphone scan)
    if random.random() < 0.5:
        (h, w) = image.shape[:2]
        # Points initiaux
        pts1 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
        
        # Décalages aléatoires (5% à 15% de la taille)
        m_x = w * random.uniform(0.05, 0.15)
        m_y = h * random.uniform(0.05, 0.15)
        
        # Points de destination (Simule l'inclinaison)
        pts2 = np.float32([
            [0 + random.uniform(0, m_x), 0 + random.uniform(0, m_y)],
            [w - random.uniform(0, m_x), 0 + random.uniform(0, m_y)],
            [0, h - random.uniform(0, m_y)],
            [w, h - random.uniform(0, m_y)]
        ])
        
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        # On peut rajouter une bordure blanche pour remplir les zones vides créées par la perspective
        image = cv2.warpPerspective(image, matrix, (w, h), borderValue=(255, 255, 255))
    
    # Sauvegarder
    if ext == '.pdf':
        output_path = os.path.splitext(output_path)[0] + ".png"
        
    cv2.imwrite(output_path, image)
    return output_path
