# collector/database.py
# Ce fichier crée notre base de données SQLite et la table metrics

# collector/database.py
import sqlite3

def creer_base_de_donnees():
    """
    Crée la base de données et la table network_metrics
    selon le schéma défini avec Personne B
    """
    connexion = sqlite3.connect("../data/network.db")
    curseur = connexion.cursor()
    
    curseur.execute("""
        CREATE TABLE IF NOT EXISTS network_metrics (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            ts         TIMESTAMP NOT NULL,
            host       TEXT NOT NULL,
            latency    REAL,
            error_rate REAL,
            traffic    REAL,
            is_anomaly BOOLEAN
        )
    """)
    
    connexion.commit()
    connexion.close()
    print("Base de données prête !")

if __name__ == "__main__":
    creer_base_de_donnees()