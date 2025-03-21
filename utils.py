import cv2
import numpy as np
import os

def create_directory_if_not_exists(directory_path):
    """Crée un répertoire"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    return directory_path

def preprocess_image_for_face_recognition(image):
    
    if image is None:
        raise ValueError("Image invalide")
    
    # Vérifier le type d'image (BGR de OpenCV ou autre)
    if len(image.shape) == 3 and image.shape[2] == 3:
        # Convertir BGR en RGB si l'image vient de OpenCV
        if isinstance(image, np.ndarray):
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Redimensionner si l'image est trop grande
    max_size = 800
    height, width = image.shape[:2]
    if height > max_size or width > max_size:
        scale = max_size / max(height, width)
        image = cv2.resize(image, (int(width * scale), int(height * scale)))
    
    return image