import hashlib
import cv2
import numpy as np
import face_recognition
import sqlite3
from utils import preprocess_image_for_face_recognition

def hash_mot_de_passe(password):
    """Hache un mot de passe avec SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def enregistrer_utilisateur(nom_utilisateur, email, mot_de_passe, image):
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # Prétraitement de l'image pour la reconnaissance faciale
        image = preprocess_image_for_face_recognition(image)
        
        # Détection des visages et extraction des encodages
        faces = face_recognition.face_locations(image)
        if not faces:
            raise ValueError("Aucun visage détecté dans l'image")
        
        encodage_facial = face_recognition.face_encodings(image, [faces[0]])[0]
        mot_de_passe_hash = hash_mot_de_passe(mot_de_passe)
       
        # Vérification si l'email existe déjà
        cursor.execute("SELECT id FROM utilisateurs WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            raise ValueError("Cet email est déjà utilisé")
            
        # Insertion dans la base de données
        cursor.execute('''INSERT INTO utilisateurs (nom_utilisateur, email, mot_de_passe, descripteur_facial)
                          VALUES (?, ?, ?, ?)
                       ''', (nom_utilisateur, email, mot_de_passe_hash, encodage_facial.tobytes()))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        if 'conn' in locals() and conn:
            conn.close()
        raise e

def authentifier_utilisateur(email, mot_de_passe):
    """Authentifie un utilisateur avec email et mot de passe"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    mot_de_passe_hash = hash_mot_de_passe(mot_de_passe)
    cursor.execute("SELECT * FROM utilisateurs WHERE email = ? AND mot_de_passe = ?", (email, mot_de_passe_hash))
    utilisateur = cursor.fetchone()
    conn.close()
    return utilisateur is not None

def authentification_par_facial(image):
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
       
        # Prétraitement de l'image
        image = preprocess_image_for_face_recognition(image)
        
        # Extraction des encodages faciaux
        faces = face_recognition.face_locations(image)
        if not faces:
            return None  # Aucun visage détecté
        
        encodage_facial = face_recognition.face_encodings(image, [faces[0]])[0]
        
        # Récupération de tous les descripteurs faciaux
        cursor.execute('SELECT descripteur_facial, email FROM utilisateurs')
        utilisateurs = cursor.fetchall()
        conn.close()
        
        # Comparaison avec chaque utilisateur
        for descripteur_binaire, email in utilisateurs:
            descripteur = np.frombuffer(descripteur_binaire, dtype=np.float64)
            # Tolérance plus stricte pour plus de sécurité
            match = face_recognition.compare_faces([descripteur], encodage_facial, tolerance=0.7)
            if match[0]:
                return email
        
        return None  
    except Exception as e:
        print(f"Erreur lors de l'authentification faciale: {e}")
        if 'conn' in locals() and conn:
            conn.close()
        return None