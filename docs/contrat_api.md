# Contrat d'API — Module de Détection
## AI Network Copilot — Semaine 3

**Auteur : Personne A (Data/ML)**
**Destinataire : Personne B (Backend/Dashboard)**
**Date : 23/06/2026**

---

## Comment importer le module

```python
import sys
sys.path.append("detection")
from detecteur import detecter, detecter_lot
```

---

## Fonction 1 — detecter()

### Description
Analyse UNE mesure réseau et retourne le résultat de détection.

### Paramètres d'entrée

| Paramètre | Type | Description | Exemple |
|-----------|------|-------------|---------|
| latency | float | Latence en ms | 25.4 |
| error_rate | float | Taux d'erreurs en % | 0.5 |
| traffic | float | Trafic en Mbps | 45.2 |

### Retour

```python
{
    "is_anomaly"      : False,        # bool
    "cause"           : "normal",     # str
    "description"     : "Aucune anomalie détectée", # str
    "conseil"         : "Aucune action requise",    # str
    "methode"         : "aucune",     # str
    "raisons"         : [...],        # list
    "score_confiance" : 42.5          # float
}
```

### Valeurs possibles de "cause"

| Cause | Description |
|-------|-------------|
| normal | Aucune anomalie |
| machine_inaccessible_ou_cable | Machine inaccessible ou câble débranché |
| interface_desactivee | Interface réseau désactivée |
| panne_wan | Défaillance lien WAN |
| defaillance_equipement | Défaillance routeur ou switch |
| parefeu_bloquant | Pare-feu bloquant |
| perte_paquets | Perte de paquets |
| saturation_bande_passante | Saturation bande passante |
| congestion | Congestion réseau |
| panne_dns | Panne DNS |
| probleme_ip | Problème IP ou passerelle |
| cpu_ram_sature | CPU/RAM saturé |
| latence_elevee | Latence élevée |
| erreurs_elevees | Taux d'erreurs élevé |

---

## Fonction 2 — detecter_lot()

### Description
Analyse les N dernières mesures de la base de données.
Utilisée pour alimenter le dashboard en temps réel.

### Paramètres d'entrée

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| limit | int | 100 | Nombre de mesures à analyser |

### Retour
Liste de dictionnaires, un par mesure :

```python
[
    {
        "id"             : 1,
        "ts"             : "2026-06-23T10:30:00",
        "host"           : "R1",
        "latency"        : 25.4,
        "error_rate"     : 0.5,
        "traffic"        : 45.2,
        "is_anomaly"     : False,
        "cause"          : "normal",
        "description"    : "Aucune anomalie détectée",
        "conseil"        : "Aucune action requise",
        "methode"        : "aucune",
        "raisons"        : ["Toutes les métriques sont normales"],
        "score_confiance": 42.5
    },
    ...
]
```

---

## Exemple d'utilisation dans l'API

```python
# Dans api/main.py
import sys
sys.path.append("detection")
from detecteur import detecter, detecter_lot

@app.get("/alerts")
def get_alerts():
    resultats = detecter_lot(limit=100)
    alertes   = [r for r in resultats if r["is_anomaly"]]
    return {"alerts": alertes}

@app.get("/metrics/latest")
def get_metrics():
    resultats = detecter_lot(limit=20)
    return {"metrics": resultats}
```

---

## Notes importantes

- Le modèle ML est dans `detection/model.pkl`
- La base de données est dans `data/network.db`
- Les chemins sont automatiquement gérés — pas besoin de les configurer
- Précision du modèle : 99.97% sur 20 088 mesures