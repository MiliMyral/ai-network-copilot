# detection/detecteur.py
# Module de détection FINAL — règles + ML + identification des causes

import joblib
import pandas as pd
import sqlite3
import os
from rules import (
    detecter_anomalie_par_regles,
    identifier_cause,
    DESCRIPTIONS_CAUSES,
    CONSEILS_CAUSES,
    SEUILS
)

import os
# Chemin absolu vers le modèle — fonctionne depuis n'importe quel dossier
DOSSIER_DETECTION = os.path.dirname(os.path.abspath(__file__))
CHEMIN_MODELE     = os.path.join(DOSSIER_DETECTION, "model.pkl")

def charger_modele():
    """Charge le modèle ML"""
    if not os.path.exists(CHEMIN_MODELE):
        raise FileNotFoundError(
            "Modèle non trouvé ! Lance d'abord ml_model.py"
        )
    return joblib.load(CHEMIN_MODELE)

def detecter(latency, error_rate, traffic, modele=None):
    """
    Détection complète : règles + ML + identification cause
    """
    if modele is None:
        modele = charger_modele()
    
    methodes_declenchees = []
    
    # Couche 1 — Règles métier
    regle_anomalie = detecter_anomalie_par_regles(
        latency, error_rate, traffic
    )
    if regle_anomalie:
        methodes_declenchees.append("règles")
    
    # Couche 2 — Machine Learning
    X = pd.DataFrame(
        [[latency, error_rate, traffic]],
        columns=["latency", "error_rate", "traffic"]
    )
    prediction_ml = modele.predict(X)[0]
    score_ml      = modele.score_samples(X)[0]
    
    if prediction_ml == -1:
        methodes_declenchees.append("ML")
    
    # Résultat final
    est_anomalie = len(methodes_declenchees) > 0
    
    # Identifier la cause si anomalie
    if est_anomalie:
        cause       = identifier_cause(latency, error_rate, traffic)
        description = DESCRIPTIONS_CAUSES.get(cause, cause)
        conseil     = CONSEILS_CAUSES.get(cause, "Diagnostic manuel requis")
        
        # Construire les raisons
        raisons = []
        if latency >= SEUILS["timeout"]:
            raisons.append(
                f"Timeout ({latency} ms) — machine inaccessible"
            )
        elif latency > SEUILS["latency"]:
            raisons.append(
                f"Latence élevée ({latency} ms > {SEUILS['latency']} ms)"
            )
        if error_rate > SEUILS["error_rate"]:
            raisons.append(
                f"Taux d'erreurs élevé ({error_rate}% > {SEUILS['error_rate']}%)"
            )
        if traffic >= SEUILS["traffic_sat"]:
            raisons.append(
                f"Trafic saturé ({traffic} Mbps > {SEUILS['traffic_sat']}%)"
            )
    else:
        cause       = "normal"
        description = "Aucune anomalie"
        conseil     = "Aucune action requise"
        raisons     = ["Toutes les métriques sont normales"]
    
    # Score de confiance
    score_confiance = round(min(100, max(0, (-score_ml) * 100)), 1)
    
    return {
        "is_anomaly"      : est_anomalie,
        "cause"           : cause,
        "description"     : description,
        "conseil"         : conseil,
        "methode"         : " + ".join(set(methodes_declenchees)) if methodes_declenchees else "aucune",
        "raisons"         : raisons,
        "score_confiance" : score_confiance
    }

def detecter_lot(limit=100):
    """
    Détecte les anomalies sur les dernières mesures
    Utilisée par l'API de Personne B
    """
    connexion = sqlite3.connect("../data/network.db")
    df = pd.read_sql(f"""
        SELECT id, ts, host, latency, error_rate, traffic
        FROM network_metrics
        ORDER BY ts DESC
        LIMIT {limit}
    """, connexion)
    connexion.close()
    
    modele    = charger_modele()
    resultats = []
    
    for _, ligne in df.iterrows():
        resultat = detecter(
            ligne["latency"],
            ligne["error_rate"],
            ligne["traffic"],
            modele
        )
        resultats.append({
            "id"             : int(ligne["id"]),
            "ts"             : ligne["ts"],
            "host"           : ligne["host"],
            "latency"        : ligne["latency"],
            "error_rate"     : ligne["error_rate"],
            "traffic"        : ligne["traffic"],
            "is_anomaly"     : resultat["is_anomaly"],
            "cause"          : resultat["cause"],
            "description"    : resultat["description"],
            "conseil"        : resultat["conseil"],
            "methode"        : resultat["methode"],
            "raisons"        : resultat["raisons"],
            "score_confiance": resultat["score_confiance"]
        })
    
    return resultats

# Test du module
if __name__ == "__main__":
    print("=" * 70)
    print(" TEST DU MODULE DE DÉTECTION FINAL AVEC CAUSES")
    print("=" * 70)
    
    exemples = [
        {"latency": 25.0,  "error_rate": 0.5,  "traffic": 45.0, "nom": "Normal"},
        {"latency": 999.0, "error_rate": 98.0, "traffic": 0.0,  "nom": "Machine inaccessible"},
        {"latency": 190.0, "error_rate": 4.0,  "traffic": 97.0, "nom": "Congestion"},
        {"latency": 120.0, "error_rate": 35.0, "traffic": 16.0, "nom": "Perte de paquets"},
        {"latency": 450.0, "error_rate": 80.0, "traffic": 3.0,  "nom": "Panne WAN"},
        {"latency": 95.0,  "error_rate": 4.5,  "traffic": 60.0, "nom": "Cas limite ML"},
    ]
    
    print("\n TESTS MANUELS :")
    print("-" * 70)
    
    for ex in exemples:
        r = detecter(ex["latency"], ex["error_rate"], ex["traffic"])
        statut = "🔴 ANOMALIE" if r["is_anomaly"] else "🟢 Normal"
        
        print(f"\n{ex['nom']} :")
        print(f"   Latence: {ex['latency']} ms | "
              f"Erreurs: {ex['error_rate']}% | "
              f"Trafic: {ex['traffic']} Mbps")
        print(f"   Résultat        : {statut}")
        if r["is_anomaly"]:
            print(f"   Cause probable  : {r['description']}")
            print(f"   Conseil         : {r['conseil']}")
            print(f"   Méthode         : {r['methode']}")
            print(f"   Confiance       : {r['score_confiance']}%")
    
    print("\n\nTEST SUR LES 5 DERNIÈRES MESURES :")
    print("-" * 70)
    
    resultats = detecter_lot(limit=5)
    for r in resultats:
        statut = "🔴" if r["is_anomaly"] else "🟢"
        print(f"\n{statut} {r['host']:12} | "
              f"Latence: {r['latency']:7} ms | "
              f"Erreurs: {r['error_rate']:6}%")
        if r["is_anomaly"]:
            print(f"   → Cause    : {r['description']}")
            print(f"   → Conseil  : {r['conseil']}")