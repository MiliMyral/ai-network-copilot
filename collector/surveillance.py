# collector/surveillance.py
# Surveillance réseau en temps réel
# Lance le simulateur ET la détection en même temps

import sys
import time
import threading
import datetime
import sqlite3
import os

# Ajouter les bons chemins
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "detection"))

from simulator_v3 import (
    HOTES, CAUSES_PANNES,
    generer_metrique_normale,
    generer_metrique_panne,
    sauvegarder
)
from detecteur import detecter, charger_modele

# État des pannes par hôte
etat_hotes = {
    hote: {"en_panne": False, "cause": None, "cycles": 0}
    for hote in HOTES
}

# Charger le modèle une seule fois au démarrage
modele = charger_modele()

# Compteur global
compteur = 0

def collecter_et_detecter():
    """
    Génère UNE mesure pour chaque hôte
    et détecte immédiatement les anomalies
    """
    global compteur, etat_hotes
    
    compteur += 1
    heure = datetime.datetime.now().strftime("%H:%M:%S")
    
    print(f"\n{'=' * 70}")
    print(f"  Cycle #{compteur} — {heure}")
    print(f"{'=' * 70}")
    
    for hote in HOTES:
        etat = etat_hotes[hote]
        
        # Décider si une panne démarre
        import random
        if not etat["en_panne"] and random.random() < 0.05:
            cause = random.choice(list(CAUSES_PANNES.keys()))
            etat["en_panne"] = True
            etat["cause"]    = cause
            etat["cycles"]   = 0
        
        # Générer la métrique
        if etat["en_panne"]:
            etat["cycles"] += 1
            metrique = generer_metrique_panne(etat["cause"])
            
            if etat["cycles"] >= random.randint(3, 5):
                etat["en_panne"] = False
                etat["cause"]    = None
                etat["cycles"]   = 0
        else:
            metrique = generer_metrique_normale()
        
        # Sauvegarder dans la base
        sauvegarder(metrique, hote)
        
        # Détecter IMMÉDIATEMENT
        resultat = detecter(
            metrique["latency"],
            metrique["error_rate"],
            metrique["traffic"],
            modele
        )
        
        # Afficher le résultat
        if resultat["is_anomaly"]:
            print(f"\n🔴 ANOMALIE | {hote:12} | "
                  f"Latence: {metrique['latency']:7} ms | "
                  f"Erreurs: {metrique['error_rate']:6} % | "
                  f"Trafic: {metrique['traffic']:6} Mbps")
            print(f"    Cause    : {resultat['description']}")
            print(f"    Conseil  : {resultat['conseil']}")
            print(f"    Méthode  : {resultat['methode']}")
            print(f"    Confiance: {resultat['score_confiance']}%")
        else:
            print(f"🟢 Normal   | {hote:12} | "
                  f"Latence: {metrique['latency']:7} ms | "
                  f"Erreurs: {metrique['error_rate']:6} % | "
                  f"Trafic: {metrique['traffic']:6} Mbps")

def afficher_statistiques():
    """
    Affiche des statistiques toutes les 10 mesures
    """
    if compteur % 10 == 0:
        connexion = sqlite3.connect(
            os.path.join(os.path.dirname(__file__), "..", "data", "network.db")
        )
        curseur = connexion.cursor()
        
        curseur.execute("""
            SELECT 
                COUNT(*)           as total,
                SUM(is_anomaly)    as anomalies,
                AVG(latency)       as lat_moy,
                MAX(latency)       as lat_max
            FROM network_metrics
            WHERE ts >= datetime('now', '-10 minutes')
        """)
        stats = curseur.fetchone()
        connexion.close()
        
        if stats[0] > 0:
            print(f"\n{'─' * 70}")
            print(f" STATS (10 dernières minutes) :")
            print(f"   Mesures    : {stats[0]}")
            print(f"   Anomalies  : {stats[1]} "
                  f"({round(stats[1]/stats[0]*100, 1)}%)")
            print(f"   Lat moyenne: {round(stats[2], 2)} ms")
            print(f"   Lat max    : {round(stats[3], 2)} ms")
            print(f"{'─' * 70}")

# Programme principal
if __name__ == "__main__":
    print(" Surveillance réseau en temps réel démarrée !")
    print("📡 Simulateur V3 + Détection ML combinés")
    print("Appuie sur Ctrl+C pour arrêter\n")
    
    try:
        while True:
            collecter_et_detecter()
            afficher_statistiques()
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n Surveillance arrêtée.")
        print(f"   Total cycles effectués : {compteur}")
        print(f"   Total mesures générées : {compteur * len(HOTES)}")