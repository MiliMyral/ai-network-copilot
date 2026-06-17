# collector/ping_collector.py
# Ce fichier envoie des pings et sauvegarde la latence

import ping3          # pour envoyer des pings
import sqlite3        # pour la base de données
import datetime       # pour l'heure actuelle
import time           # pour attendre 5 secondes
from database import creer_base_de_donnees  # notre fichier database.py

# Les adresses IP qu'on va pinguer
CIBLES = [
    "8.8.8.8",    # Google DNS
    "1.1.1.1",    # Cloudflare DNS
]

def collecter_ping():
    """
    Envoie un ping à chaque cible et retourne les résultats
    """
    resultats = []
    
    for ip in CIBLES:
        # On envoie le ping (timeout=2 = on attend max 2 secondes)
        latence = ping3.ping(ip, timeout=2)
        
        # Si pas de réponse, latence = -1
        if latence is None:
            latence = -1
        else:
            # On convertit en millisecondes
            latence = latence * 1000
            
        # On note l'heure actuelle
        maintenant = datetime.datetime.now().isoformat()
        
        resultats.append({
            "timestamp": maintenant,
            "host": ip,
            "latency": round(latence, 2)
        })
        
        print(f" Ping vers {ip} : {round(latence, 2)} ms")
    
    return resultats

def sauvegarder(resultats):
    """
    Sauvegarde les résultats dans la base de données
    """
    connexion = sqlite3.connect("../data/network.db")
    curseur = connexion.cursor()
    
    for r in resultats:
        curseur.execute("""
            INSERT INTO metrics (timestamp, latency, traffic, error_rate, is_anomaly)
            VALUES (?, ?, ?, ?, ?)
        """, (
            r["timestamp"],
            r["latency"],
            0,    # trafic = 0 car ping ne mesure pas ça
            0,    # erreurs = 0 car ping ne mesure pas ça
            0     # pas d'anomalie détectée pour l'instant
        ))
    
    connexion.commit()
    connexion.close()
    print(" Données sauvegardées !\n")

# Programme principal
if __name__ == "__main__":
    # On crée la base de données si elle n'existe pas
    creer_base_de_donnees()
    
    print(" Collecteur ping démarré...")
    print("Appuie sur Ctrl+C pour arrêter\n")
    
    # Boucle infinie : on collecte toutes les 5 secondes
    while True:
        resultats = collecter_ping()
        sauvegarder(resultats)
        print(" Prochaine collecte dans 5 secondes...\n")
        time.sleep(5)  # on attend 5 secondes