# collector/simulator_v3.py
# Simulateur enrichi avec 13 causes réelles de pannes réseau

import random
import sqlite3
import datetime
import time
from database import creer_base_de_donnees

# Les 3 hôtes de notre réseau (branche gauche du schéma Cisco)
HOTES = ["R1", "SW1", "WEB_SERVER"]

# Les 13 causes de pannes avec leurs symptômes réels
CAUSES_PANNES = {
    "latence_elevee": {
        "description" : "Latence réseau élevée",
        "latency"     : (150, 300),
        "traffic"     : (0, 100),
        "error_rate"  : (0, 2),
        "conseil"     : "Vérifier la charge réseau avec ping et tracert"
    },
    "congestion": {
        "description" : "Congestion / trafic réseau important",
        "latency"     : (100, 200),
        "traffic"     : (90, 100),
        "error_rate"  : (2, 5),
        "conseil"     : "Identifier les flux avec forte consommation, appliquer QoS"
    },
    "machine_inaccessible": {
        "description" : "Machine inaccessible ou éteinte",
        "latency"     : (999, 1000),  # timeout simulé
        "traffic"     : (0, 0),
        "error_rate"  : (95, 100),
        "conseil"     : "Vérifier si la machine est allumée, tester ping et arp -a"
    },
    "perte_paquets": {
        "description" : "Perte de paquets",
        "latency"     : (50, 150),
        "traffic"     : (10, 60),
        "error_rate"  : (20, 50),
        "conseil"     : "Tester avec ping -n 100, vérifier les câbles réseau"
    },
    "defaillance_equipement": {
        "description" : "Défaillance routeur ou switch",
        "latency"     : (200, 500),
        "traffic"     : (0, 10),
        "error_rate"  : (50, 100),
        "conseil"     : "Vérifier les logs équipement, redémarrer si nécessaire"
    },
    "cable_debranche": {
        "description" : "Câble réseau débranché ou endommagé",
        "latency"     : (999, 1000),  # timeout simulé
        "traffic"     : (0, 0),
        "error_rate"  : (95, 100),
        "conseil"     : "Vérifier physiquement le câble, tester avec ipconfig"
    },
    "probleme_ip": {
        "description" : "Problème de configuration IP ou passerelle",
        "latency"     : (200, 400),
        "traffic"     : (5, 30),
        "error_rate"  : (30, 60),
        "conseil"     : "Vérifier avec ipconfig /all, corriger la passerelle"
    },
    "panne_dns": {
        "description" : "Panne ou mauvaise configuration DNS",
        "latency"     : (300, 500),
        "traffic"     : (10, 50),
        "error_rate"  : (10, 30),
        "conseil"     : "Tester avec nslookup, vider cache DNS (ipconfig /flushdns)"
    },
    "saturation_bande_passante": {
        "description" : "Saturation de la bande passante",
        "latency"     : (100, 250),
        "traffic"     : (95, 100),
        "error_rate"  : (5, 15),
        "conseil"     : "Identifier les gros consommateurs, appliquer QoS"
    },
    "interface_desactivee": {
        "description" : "Interface réseau désactivée ou défectueuse",
        "latency"     : (999, 1000),  # timeout simulé
        "traffic"     : (0, 0),
        "error_rate"  : (95, 100),
        "conseil"     : "Réactiver avec netsh interface set interface enable"
    },
    "parefeu_bloquant": {
        "description" : "Pare-feu bloquant les communications",
        "latency"     : (100, 200),
        "traffic"     : (5, 40),
        "error_rate"  : (40, 80),
        "conseil"     : "Tester avec telnet sur le port concerné, vérifier les règles pare-feu"
    },
    "panne_wan": {
        "description" : "Défaillance du lien WAN / connexion Internet",
        "latency"     : (400, 1000),
        "traffic"     : (0, 5),
        "error_rate"  : (70, 100),
        "conseil"     : "Tester ping 8.8.8.8, contacter le fournisseur d'accès"
    },
    "cpu_ram_sature": {
        "description" : "Forte utilisation CPU/RAM sur le serveur",
        "latency"     : (200, 400),
        "traffic"     : (20, 60),
        "error_rate"  : (10, 20),
        "conseil"     : "Vérifier avec tasklist (Windows) ou top (Linux)"
    }
}

# État actuel de chaque hôte
etat_hotes = {hote: {"en_panne": False, "cause": None, "cycles": 0} for hote in HOTES}

def generer_metrique_normale():
    """Génère une mesure réseau normale"""
    return {
        "latency"    : round(random.uniform(5, 40), 2),
        "traffic"    : round(random.uniform(0, 100), 2),
        "error_rate" : round(random.uniform(0, 1), 2),
        "is_anomaly" : 0,
        "cause"      : "normal"
    }

def generer_metrique_panne(cause_nom):
    """Génère une mesure réseau selon une cause de panne réelle"""
    cause = CAUSES_PANNES[cause_nom]
    return {
        "latency"    : round(random.uniform(*cause["latency"]), 2),
        "traffic"    : round(random.uniform(*cause["traffic"]), 2),
        "error_rate" : round(random.uniform(*cause["error_rate"]), 2),
        "is_anomaly" : 1,
        "cause"      : cause_nom
    }

def sauvegarder(metrique, hote):
    """Sauvegarde une métrique dans la base de données"""
    connexion = sqlite3.connect("../data/network.db")
    curseur   = connexion.cursor()
    
    curseur.execute("""
        INSERT INTO network_metrics
        (ts, host, latency, error_rate, traffic, is_anomaly)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        datetime.datetime.now().isoformat(),
        hote,
        metrique["latency"],
        metrique["error_rate"],
        metrique["traffic"],
        metrique["is_anomaly"]
    ))
    
    connexion.commit()
    connexion.close()

def afficher_metrique(hote, metrique):
    """Affiche une métrique dans le terminal"""
    if metrique["is_anomaly"]:
        cause_info = CAUSES_PANNES.get(metrique["cause"], {})
        description = cause_info.get("description", metrique["cause"])
        conseil = cause_info.get("conseil", "")
        print(f"   🔴 ANOMALIE | {hote:12} | "
              f"Latence: {metrique['latency']:7} ms | "
              f"Erreurs: {metrique['error_rate']:6} % | "
              f"Trafic: {metrique['traffic']:6} Mbps")
        print(f"      Cause   : {description}")
        print(f"      Conseil : {conseil}")
    else:
        print(f"   🟢 Normal   | {hote:12} | "
              f"Latence: {metrique['latency']:7} ms | "
              f"Erreurs: {metrique['error_rate']:6} % | "
              f"Trafic: {metrique['traffic']:6} Mbps")

# Programme principal
if __name__ == "__main__":
    creer_base_de_donnees()
    
    print(" Simulateur V3 démarré — 13 causes de pannes réelles !")
    print("=" * 70)
    print("Appuie sur Ctrl+C pour arrêter\n")
    
    compteur = 0
    
    while True:
        compteur += 1
        print(f"\n--- Cycle #{compteur} - "
              f"{datetime.datetime.now().strftime('%H:%M:%S')} ---")
        
        for hote in HOTES:
            etat = etat_hotes[hote]
            
            # Décider si une nouvelle panne démarre (5% de chance)
            if not etat["en_panne"] and random.random() < 0.05:
                # Choisir une cause aléatoire parmi les 13
                cause = random.choice(list(CAUSES_PANNES.keys()))
                etat["en_panne"] = True
                etat["cause"]    = cause
                etat["cycles"]   = 0
                print(f"\n     NOUVELLE PANNE sur {hote} !")
                print(f"      Cause : {CAUSES_PANNES[cause]['description']}")
            
            if etat["en_panne"]:
                etat["cycles"] += 1
                metrique = generer_metrique_panne(etat["cause"])
                
                # La panne dure entre 3 et 5 cycles
                if etat["cycles"] >= random.randint(3, 5):
                    etat["en_panne"] = False
                    etat["cause"]    = None
                    etat["cycles"]   = 0
                    print(f"\n    Retour à la normale sur {hote}")
            else:
                metrique = generer_metrique_normale()
            
            afficher_metrique(hote, metrique)
            sauvegarder(metrique, hote)
        
        print(f"\n    {len(HOTES)} métriques sauvegardées")
        time.sleep(5)