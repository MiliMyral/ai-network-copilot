# collector/simulator.py
# Ce fichier simule des données réseau réalistes
# Il génère des métriques normales et des anomalies

import random      # pour générer des nombres aléatoires
import sqlite3     # pour la base de données
import datetime    # pour l'heure actuelle
import time        # pour attendre 5 secondes

def generer_metrique():
    """
    Génère UNE ligne de données réseau
    Retourne soit une situation normale, soit une anomalie
    """
    
    # random.random() génère un nombre entre 0 et 1
    # Si ce nombre est inférieur à 0.05 = 5% de chance
    est_anomalie = random.random() < 0.05
    
    if est_anomalie:
        # Situation anormale : valeurs élevées
        latence     = random.uniform(80, 200)   # entre 80 et 200 ms
        trafic      = random.uniform(0, 100)    # normal
        taux_erreur = random.uniform(5, 20)     # entre 5 et 20 %
        is_anomaly  = 1
        print("🔴 ANOMALIE générée !")
    else:
        # Situation normale : valeurs basses
        latence     = random.uniform(5, 40)     # entre 5 et 40 ms
        trafic      = random.uniform(0, 100)    # entre 0 et 100 Mbps
        taux_erreur = random.uniform(0, 1)      # entre 0 et 1 %
        is_anomaly  = 0
        print("🟢 Situation normale")
    
    return {
        "timestamp"  : datetime.datetime.now().isoformat(),
        "latency"    : round(latence, 2),
        "traffic"    : round(trafic, 2),
        "error_rate" : round(taux_erreur, 2),
        "is_anomaly" : is_anomaly
    }

def sauvegarder(metrique):
    """
    Sauvegarde une métrique dans la base de données
    """
    connexion = sqlite3.connect("../data/network.db")
    curseur   = connexion.cursor()
    
    curseur.execute("""
        INSERT INTO metrics (timestamp, latency, traffic, error_rate, is_anomaly)
        VALUES (?, ?, ?, ?, ?)
    """, (
        metrique["timestamp"],
        metrique["latency"],
        metrique["traffic"],
        metrique["error_rate"],
        metrique["is_anomaly"]
    ))
    
    connexion.commit()
    connexion.close()

# Programme principal
if __name__ == "__main__":
    print(" Simulateur démarré !")
    print("Appuie sur Ctrl+C pour arrêter\n")
    
    compteur = 0  # pour compter le nombre de mesures
    
    while True:
        compteur += 1
        print(f"--- Mesure #{compteur} ---")
        
        # On génère une métrique
        metrique = generer_metrique()
        
        # On affiche les valeurs
        print(f"   Timestamp  : {metrique['timestamp']}")
        print(f"   Latence    : {metrique['latency']} ms")
        print(f"   Trafic     : {metrique['traffic']} Mbps")
        print(f"   Erreurs    : {metrique['error_rate']} %")
        print(f"   Anomalie   : {'OUI' if metrique['is_anomaly'] else 'NON'}")
        
        # On sauvegarde
        sauvegarder(metrique)
        print(" Sauvegardé !\n")
        
        # On attend 5 secondes
        time.sleep(5)