# collector/simulator_v2.py
# Simulateur amélioré avec :
# - Plusieurs hôtes simulés
# - Plusieurs types d'anomalies
# - Anomalies progressives

import random
import sqlite3
import datetime
import time
from database import creer_base_de_donnees

# Les équipements réseau qu'on simule
HOTES = [
    "R1",           # Routeur principal 2911
    "SW1",          # Switch 2960-24TT branche gauche
    "WEB_SERVER"    # Serveur web branche gauche
]

# Les seuils qui définissent une anomalie
SEUILS = {
    "latency"   : 100,  # ms
    "error_rate": 5,    # %
}

# Variable globale pour suivre l'état de chaque hôte
# False = normal, True = en cours d'anomalie
etat_hotes = {hote: False for hote in HOTES}

# Compteur de progression d'anomalie par hôte
progression_anomalie = {hote: 0 for hote in HOTES}

def generer_metrique_hote(hote):
    """
    Génère une métrique pour UN hôte spécifique
    Tient compte de l'état actuel de l'hôte
    """
    global etat_hotes, progression_anomalie
    
    # 5% de chance de démarrer une nouvelle anomalie
    if not etat_hotes[hote] and random.random() < 0.05:
        etat_hotes[hote] = True
        progression_anomalie[hote] = 0
        print(f"    Début d'anomalie sur {hote} !")
    
    if etat_hotes[hote]:
        # On est en anomalie → on fait progresser
        progression_anomalie[hote] += 1
        
        # Choisir le type d'anomalie selon l'hôte
        if hote == "routeur-principal":
            # Type 1 : pic de latence progressif
            latence     = random.uniform(50, 80) * progression_anomalie[hote]
            trafic      = random.uniform(80, 100)  # trafic élevé
            taux_erreur = random.uniform(0, 2)
            
        elif hote == "serveur-web":
            # Type 2 : taux d'erreurs élevé
            latence     = random.uniform(20, 50)
            trafic      = random.uniform(0, 100)
            taux_erreur = random.uniform(10, 20)  # beaucoup d'erreurs
            
        else:
            # Type 3 : anomalie mixte
            latence     = random.uniform(80, 150)
            trafic      = random.uniform(0, 100)
            taux_erreur = random.uniform(5, 15)
        
        # Limiter la latence à 300ms maximum
        latence = min(latence, 300)
        is_anomaly = 1
        
        # Après 3 mesures d'anomalie → retour à la normale
        if progression_anomalie[hote] >= 3:
            etat_hotes[hote] = False
            progression_anomalie[hote] = 0
            print(f"   Retour à la normale sur {hote}")
    
    else:
        # Situation normale
        latence     = random.uniform(5, 40)
        trafic      = random.uniform(0, 100)
        taux_erreur = random.uniform(0, 1)
        is_anomaly  = 0
    
    return {
        "ts"        : datetime.datetime.now().isoformat(),
        "host"      : hote,
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

def afficher_metrique(metrique):
    """
    Affiche une métrique dans le terminal
    """
    statut = "🔴 ANOMALIE" if metrique["is_anomaly"] else "🟢 Normal  "
    print(f"   {statut} | "
          f"Host: {metrique['host']:20} | "
          f"Latence: {metrique['latency']:6} ms | "
          f"Erreurs: {metrique['error_rate']:5} % | "
          f"Trafic: {metrique['traffic']:6} Mbps")

# Programme principal
if __name__ == "__main__":
    creer_base_de_donnees()
    
    print(" Simulateur V2 démarré !")
    print("=" * 70)
    print("Appuie sur Ctrl+C pour arrêter\n")
    
    compteur = 0
    
    while True:
        compteur += 1
        print(f"--- Cycle #{compteur} - {datetime.datetime.now().strftime('%H:%M:%S')} ---")
        
        # On génère et sauvegarde une métrique pour CHAQUE hôte
        for hote in HOTES:
            metrique = generer_metrique_hote(hote)
            afficher_metrique(metrique)
            sauvegarder(metrique)
        
        print(f" {len(HOTES)} métriques sauvegardées\n")
        time.sleep(5)