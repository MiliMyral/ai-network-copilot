# collector/simulator.py
# Ce fichier simule des données réseau réalistes
# Il génère des métriques normales et des anomalies

import random
import sqlite3
import datetime
import time
from database import creer_base_de_donnees

def generer_metrique():
    """
    Génère UNE ligne de données réseau
    Retourne soit une situation normale, soit une anomalie
    """
    # 5% de chance d'anomalie
    est_anomalie = random.random() < 0.05
    
    if est_anomalie:
        # Situation anormale
        latence     = random.uniform(80, 200)
        trafic      = random.uniform(0, 100)
        taux_erreur = random.uniform(5, 20)
        is_anomaly  = 1
        print("🔴 ANOMALIE générée !")
    else:
        # Situation normale
        latence     = random.uniform(5, 40)
        trafic      = random.uniform(0, 100)
        taux_erreur = random.uniform(0, 1)
        is_anomaly  = 0
        print("🟢 Situation normale")
    
    return {
        "ts"        : datetime.datetime.now().isoformat(),
        "host"      : "simulateur",
        "latency"   : round(latence, 2),
        "traffic"   : round(trafic, 2),
        "error_rate": round(taux_erreur, 2),
        "is_anomaly": is_anomaly
    }

def sauvegarder(metrique):
    """
    Sauvegarde une métrique dans la base de données
    """
    connexion = sqlite3.connect("../data/network.db")
    curseur   = connexion.cursor()
    
    curseur.execute("""
        INSERT INTO network_metrics 
        (ts, host, latency, error_rate, traffic, is_anomaly)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        metrique["ts"],
        metrique["host"],
        metrique["latency"],
        metrique["error_rate"],
        metrique["traffic"],
        metrique["is_anomaly"]
    ))
    
    connexion.commit()
    connexion.close()

# Programme principal
if __name__ == "__main__":
    # On crée la base de données si elle n'existe pas
    creer_base_de_donnees()
    
    print(" Simulateur démarré !")
    print("Appuie sur Ctrl+C pour arrêter\n")
    
    compteur = 0
    
    while True:
        compteur += 1
        print(f"--- Mesure #{compteur} ---")
        
        # On génère une métrique
        metrique = generer_metrique()
        
        # On affiche les valeurs
        print(f"   Timestamp  : {metrique['ts']}")
        print(f"   Host       : {metrique['host']}")
        print(f"   Latence    : {metrique['latency']} ms")
        print(f"   Trafic     : {metrique['traffic']} Mbps")
        print(f"   Erreurs    : {metrique['error_rate']} %")
        print(f"   Anomalie   : {'OUI 🔴' if metrique['is_anomaly'] else 'NON ✅'}")
        
        # On sauvegarde
        sauvegarder(metrique)
        print(" Sauvegardé !\n")
        
        # On attend 5 secondes
        time.sleep(5)