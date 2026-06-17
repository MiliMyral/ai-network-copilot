# collector/database.py
# Ce fichier crée notre base de données SQLite et la table metrics

import sqlite3  # sqlite3 est déjà inclus dans Python, pas besoin de l'installer

def creer_base_de_donnees():
    """
    Cette fonction crée la base de données et la table metrics
    si elles n'existent pas encore
    """
    # On se connecte à la base de données
    # Si le fichier n'existe pas, SQLite le crée automatiquement
    connexion = sqlite3.connect("../data/network.db")
    
    # On crée un "curseur" pour exécuter des commandes SQL
    curseur = connexion.cursor()
    
    # On crée la table metrics avec nos 5 colonnes
    # IF NOT EXISTS = seulement si elle n'existe pas déjà
    curseur.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            timestamp  TEXT,
            latency    REAL,
            traffic    REAL,
            error_rate REAL,
            is_anomaly INTEGER
        )
    """)
    
    # On sauvegarde les changements
    connexion.commit()
    
    # On ferme la connexion
    connexion.close()
    
    print(" Base de données prête !")

# Si on lance ce fichier directement, on crée la base
if __name__ == "__main__":
    creer_base_de_donnees()