# detection/rules.py
# Détection d'anomalies par règles métier simples (seuils)

# Les seuils définis à partir de notre analyse exploratoire (Jour 1)
SEUILS = {
    "latency"    : 100,   # ms — au-delà = anomalie
    "error_rate" : 5      # %  — au-delà = anomalie
}

def detecter_anomalie_par_regles(latency, error_rate):
    """
    Vérifie si une mesure est une anomalie selon nos règles de seuils.
    Retourne True si anomalie, False si normal.
    
    Une mesure est considérée comme anomalie si AU MOINS UNE
    des conditions est dépassée (latence OU taux d'erreurs).
    """
    anomalie_latence = latency > SEUILS["latency"]
    anomalie_erreur  = error_rate > SEUILS["error_rate"]
    
    return anomalie_latence or anomalie_erreur

def detail_detection(latency, error_rate):
    """
    Version détaillée qui explique POURQUOI c'est une anomalie.
    Utile pour le dashboard plus tard (afficher la raison de l'alerte).
    """
    raisons = []
    
    if latency > SEUILS["latency"]:
        raisons.append(f"Latence élevée ({latency} ms > {SEUILS['latency']} ms)")
    
    if error_rate > SEUILS["error_rate"]:
        raisons.append(f"Taux d'erreurs élevé ({error_rate}% > {SEUILS['error_rate']}%)")
    
    est_anomalie = len(raisons) > 0
    
    return {
        "is_anomaly": est_anomalie,
        "raisons"   : raisons if raisons else ["Aucune anomalie détectée"]
    }

# Test rapide si on exécute ce fichier directement
if __name__ == "__main__":
    print("=" * 60)
    print("  TESTS DES RÈGLES DE DÉTECTION")
    print("=" * 60)
    
    # Cas de test
    cas_test = [
        {"latency": 25.4,  "error_rate": 0.5,  "nom": "Cas normal"},
        {"latency": 150.0, "error_rate": 1.0,  "nom": "Latence élevée seule"},
        {"latency": 30.0,  "error_rate": 8.0,  "nom": "Erreurs élevées seules"},
        {"latency": 200.0, "error_rate": 15.0, "nom": "Anomalie double"},
        {"latency": 99.0,  "error_rate": 4.9,  "nom": "Juste sous les seuils"},
    ]
    
    for cas in cas_test:
        resultat = detail_detection(cas["latency"], cas["error_rate"])
        statut = "🔴 ANOMALIE" if resultat["is_anomaly"] else "🟢 Normal"
        
        print(f"\n{cas['nom']} :")
        print(f"   Latence: {cas['latency']} ms | Erreurs: {cas['error_rate']} %")
        print(f"   Résultat: {statut}")
        for raison in resultat["raisons"]:
            print(f"   → {raison}")