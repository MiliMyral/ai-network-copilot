# test_import.py
# Vérifie que le module de détection est bien importable
# depuis n'importe quel dossier du projet

import sys
sys.path.append("detection")  # ajoute le dossier detection au chemin

from detecteur import detecter, detecter_lot

print(" Import réussi !")
print("\nTest de la fonction detecter() :")

# Test 1 — cas normal
r1 = detecter(25.0, 0.5, 45.0)
print(f"\nCas normal → is_anomaly: {r1['is_anomaly']}")

# Test 2 — anomalie
r2 = detecter(999.0, 98.0, 0.0)
print(f"Machine inaccessible → is_anomaly: {r2['is_anomaly']}")
print(f"Cause : {r2['description']}")
print(f"Conseil : {r2['conseil']}")

print("\n Module prêt à être utilisé par l'API !")