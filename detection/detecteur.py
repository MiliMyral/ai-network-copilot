# detection/detecteur.py
# Module de détection FINAL combinant règles + ML
# Ce fichier est la livraison principale pour Personne B

import joblib
import pandas as pd
import sqlite3
import os

# Chemins
CHEMIN_MODELE = "../detection/model.pkl"

# Seuils des règles métier
SEUILS = {
    "latency"    : 100,  # ms
    "error_rate" : 5     # %
}

def charger_modele():
    """
    Charge le modèle ML depuis le fichier sauvegardé
    """
    if not os.path.exists(CHEMIN_MODELE):
        raise FileNotFoundError(
            "Modèle non trouvé ! Lance d'abord ml_model.py"
        )
    return joblib.load(CHEMIN_MODELE)

def detecter(latency, error_rate, traffic, modele=None):
    """
    Fonction principale de détection — combine règles + ML
    
    Paramètres :
        latency    : latence en ms
        error_rate : taux d'erreurs en %
        traffic    : trafic en Mbps
        modele     : modèle ML (chargé automatiquement si None)
    
    Retourne un dictionnaire avec :
        is_anomaly    : True/False
        methode       : quelle méthode a détecté l'anomalie
        raisons       : liste des raisons de l'alerte
        score_confiance : niveau de confiance (0 à 100%)
    """
    # Charger le modèle si pas fourni
    if modele is None:
        modele = charger_modele()
    
    raisons = []
    methodes_declenchees = []
    
    # ---- Couche 1 : Règles métier ----
    if latency > SEUILS["latency"]:
        raisons.append(
            f"Latence élevée ({latency} ms > {SEUILS['latency']} ms)"
        )
        methodes_declenchees.append("règles")
    
    if error_rate > SEUILS["error_rate"]:
        raisons.append(
            f"Taux d'erreurs élevé ({error_rate}% > {SEUILS['error_rate']}%)"
        )
        methodes_declenchees.append("règles")
    
    # ---- Couche 2 : Machine Learning ----
    X = pd.DataFrame(
        [[latency, error_rate, traffic]],
        columns=["latency", "error_rate", "traffic"]
    )
    prediction_ml = modele.predict(X)[0]
    score_ml      = modele.score_samples(X)[0]
    
    if prediction_ml == -1:  # -1 = anomalie pour Isolation Forest
        if "règles" not in methodes_declenchees:
            raisons.append("Comportement inhabituel détecté par ML")
        methodes_declenchees.append("ML")
    
    # ---- Résultat final ----
    est_anomalie = len(methodes_declenchees) > 0
    
    # Score de confiance basé sur le score ML
    # Plus le score est négatif, plus c'est une anomalie
    score_confiance = round(min(100, max(0, (-score_ml) * 100)), 1)
    
    return {
        "is_anomaly"      : est_anomalie,
        "methode"         : " + ".join(set(methodes_declenchees)) if methodes_declenchees else "aucune",
        "raisons"         : raisons if raisons else ["Aucune anomalie détectée"],
        "score_confiance" : score_confiance
    }

def detecter_lot(limit=100):
    """
    Détecte les anomalies sur les dernières mesures de la base
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
    
    modele = charger_modele()
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
            "methode"        : resultat["methode"],
            "raisons"        : resultat["raisons"],
            "score_confiance": resultat["score_confiance"]
        })
    
    return resultats

# Programme principal — test du module complet
if __name__ == "__main__":
    print("=" * 60)
    print(" TEST DU MODULE DE DÉTECTION FINAL")
    print("=" * 60)
    
    # Test sur des exemples manuels
    exemples = [
        {"latency": 25.0,  "error_rate": 0.5,  "traffic": 45.0, "nom": "Cas normal"},
        {"latency": 150.0, "error_rate": 12.0, "traffic": 90.0, "nom": "Anomalie double"},
        {"latency": 95.0,  "error_rate": 4.5,  "traffic": 60.0, "nom": "Cas limite (ML seulement)"},
        {"latency": 30.0,  "error_rate": 8.0,  "traffic": 20.0, "nom": "Erreurs élevées (règles)"},
    ]
    
    print("\n TESTS MANUELS :")
    print("-" * 60)
    
    for ex in exemples:
        resultat = detecter(ex["latency"], ex["error_rate"], ex["traffic"])
        statut = "🔴 ANOMALIE" if resultat["is_anomaly"] else "🟢 Normal"
        
        print(f"\n{ex['nom']} :")
        print(f"   Latence: {ex['latency']} ms | Erreurs: {ex['error_rate']}% | Trafic: {ex['traffic']} Mbps")
        print(f"   Résultat        : {statut}")
        print(f"   Méthode         : {resultat['methode']}")
        print(f"   Score confiance : {resultat['score_confiance']}%")
        for raison in resultat["raisons"]:
            print(f"   → {raison}")
    
    # Test sur les vraies données
    print("\n\n  TEST SUR LES 10 DERNIÈRES MESURES DE LA BASE :")
    print("-" * 60)
    
    resultats = detecter_lot(limit=10)
    
    for r in resultats:
        statut = "🔴" if r["is_anomaly"] else "🟢"
        print(f"{statut} {r['host']:12} | "
              f"Latence: {r['latency']:6} ms | "
              f"Erreurs: {r['error_rate']:5}% | "
              f"Méthode: {r['methode']}")