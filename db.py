import sqlite3

def creer_base_donnees():
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
       
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_utilisateur TEXT UNIQUE,
            email TEXT UNIQUE,
            mot_de_passe TEXT,
            descripteur_facial BLOB,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()

