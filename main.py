import sqlite3
import cv2
import numpy as np
import streamlit as st
from auth import enregistrer_utilisateur, authentification_par_facial, authentifier_utilisateur
from db import creer_base_donnees
from utils import preprocess_image_for_face_recognition, create_directory_if_not_exists


# Fonction pour initialiser la session
def init_session():
    if "connected" not in st.session_state:
        st.session_state["connected"] = False
    if "user" not in st.session_state:
        st.session_state["user"] = None

def interface_inscription():
    st.title("Inscription")
    nom_utilisateur = st.text_input("Nom d'utilisateur")
    email = st.text_input("Email")
    mot_de_passe = st.text_input("Mot de passe", type="password")
    image_upload = st.file_uploader("Téléversez une image pour l'authentification faciale", type=["jpg", "png"])
    
    if st.button("S'inscrire"):
        if not nom_utilisateur.strip():
            st.error("Le champ 'Nom d'utilisateur' est vide.")
        elif not email.strip():
            st.error("Le champ 'Email' est vide.")
        elif not mot_de_passe.strip():
            st.error("Le champ 'Mot de passe' est vide.")
        elif not image_upload:
            st.error("Veuillez téléverser une image.")
        else:
            try:
                image = cv2.imdecode(np.frombuffer(image_upload.read(), np.uint8), cv2.IMREAD_COLOR)
                if image is None:
                    st.error("Impossible de lire l'image téléversée.")
                    return
                
                enregistrer_utilisateur(nom_utilisateur, email, mot_de_passe, image)
                st.success("Inscription réussie ! Vous pouvez maintenant vous connecter.")
            except Exception as e:
                st.error(f"Erreur lors de l'inscription : {e}")

def interface_connexion():
    if "connected" in st.session_state and st.session_state["connected"]:
        st.success(f"Vous êtes déjà connecté en tant que {st.session_state['user']}.")
        if st.button("Se déconnecter"):
            del st.session_state["connected"]
            del st.session_state["user"]
            st.experimental_rerun()
        return

    st.title("Connexion")
    email = st.text_input("Email")
    mot_de_passe = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        if email and mot_de_passe:
            if not authentifier_utilisateur(email, mot_de_passe):
                st.error("Email ou mot de passe incorrect.")
                return

            st.success("Email et mot de passe vérifiés.")
            st.info("Veuillez vous placer devant la caméra pour vérification faciale.")

            try:
                capture = cv2.VideoCapture(0)
                if not capture.isOpened():
                    st.error("Impossible d'accéder à la caméra.")
                    return

                ret, frame = capture.read()
                capture.release()

                if not ret:
                    st.error("Erreur lors de la capture d'image.")
                    return
                
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                utilisateur = authentification_par_facial(rgb_frame)
                if utilisateur and utilisateur == email:
                    st.session_state["connected"] = True
                    st.session_state["user"] = email
                    st.success(f"Connexion réussie ! Bienvenue {utilisateur}.")
                    st.experimental_rerun()
                else:
                    st.error("Reconnaissance faciale échouée ou utilisateur non correspondant.")
            except Exception as e:
                st.error(f"Erreur lors de la reconnaissance faciale : {e}")
        else:
            st.error("Veuillez fournir un email et un mot de passe.")

def interface_bienvenue():
    if not st.session_state["connected"]:
        st.warning("Veuillez vous connecter pour accéder au contenu.")
        return
    
    st.title(f"Bienvenue, {st.session_state['user']}!")
    st.write("Vous êtes connecté à l'application d'authentification du Projet 1.")
    st.write("Cette page est accessible uniquement aux utilisateurs authentifiés.")
    
    # Afficher des informations sur l'utilisateur connecté
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT nom_utilisateur, date_creation FROM utilisateurs WHERE email = ?", 
                      (st.session_state["user"],))
        user_info = cursor.fetchone()
        conn.close()
        
        if user_info:
            st.subheader("Informations utilisateur")
            st.write(f"Nom d'utilisateur: {user_info[0]}")
            st.write(f"Compte créé le: {user_info[1]}")
    except Exception as e:
        st.error(f"Erreur lors de la récupération des informations utilisateur: {e}")

def inspecter_utilisateurs():
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT nom_utilisateur, email, descripteur_facial FROM utilisateurs")
        utilisateurs = cursor.fetchall()
        print(f"Nombre d'utilisateurs: {len(utilisateurs)}")
        for utilisateur in utilisateurs:
            print(f"Nom: {utilisateur[0]}, Email: {utilisateur[1]}, Descripteur: {len(utilisateur[2]) if utilisateur[2] else 'Non défini'}")
        conn.close()
    except Exception as e:
        print(f"Erreur lors de l'inspection des utilisateurs: {e}")

if __name__ == "__main__":
    # Initialisation de la base de données
    creer_base_donnees()
    
    # Création du répertoire uploads
    create_directory_if_not_exists("./uploads")
    
    # Inspection des utilisateurs pour debug
    print("Inspecter les utilisateurs enregistrés :")
    inspecter_utilisateurs()

    # Interface Streamlit
    init_session()
    st.sidebar.title("Navigation")
    choix = st.sidebar.radio("Choisissez une option", ["Inscription", "Connexion", "Accueil"])
    
    if choix == "Inscription":
        interface_inscription()
    elif choix == "Connexion":
        interface_connexion()
    elif choix == "Accueil":
        interface_bienvenue()