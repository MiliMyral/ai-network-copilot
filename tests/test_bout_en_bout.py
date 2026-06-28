# tests/test_bout_en_bout.py
# Test complet de la chaîne : collecte → stockage → détection → API

import sys
import os
import sqlite3
import datetime

# Ajouter les chemins nécessaires
DOSSIER_PROJET = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(DOSSIER_PROJET, "collector"))
sys.path.append(os.path.join(DOSSIER_PROJET, "detection"))
sys.path.append(os.path.join(DOSSIER_PROJET, "api"))

from database import creer_base_de_donnees
from simulator_v3 import generer_metrique_normale, generer_metrique_panne, CAUSES_PANNES
from detecteur import detecter, detecter_lot
from detection_bridge import get_alerts_with_causes, get_metrics_with_detection

# Chemin base de données
CHEMIN_DB = os.path.join(DOSSIER_PROJET, "data", "network.db")

def compter_lignes():
    """Compte le nombre de lignes dans la base"""
    conn = sqlite3.connect(CHEMIN_DB)
    curseur = conn.cursor()
    curseur.execute("SELECT COUNT(*) FROM network_metrics")
    total = curseur.fetchone()[0]
    conn.close()
    return total

def inserer_mesure(hote, metrique):
    """Insère une mesure dans la base"""
    conn = sqlite3.connect(CHEMIN_DB)
    curseur = conn.cursor()
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
    conn.commit()
    conn.close()

def test_1_base_de_donnees():
    """Test 1 : La base de données est accessible"""
    print("\n TEST 1 — Base de données")
    print("-" * 50)
    
    try:
        total = compter_lignes()
        print(f"   ✅ Base accessible : {total} mesures existantes")
        return True
    except Exception as e:
        print(f"   ❌ Erreur : {e}")
        return False

def test_2_simulateur():
    """Test 2 : Le simulateur génère des données correctes"""
    print("\n TEST 2 — Simulateur")
    print("-" * 50)
    
    try:
        # Test mesure normale
        m_normale = generer_metrique_normale()
        assert 5 <= m_normale["latency"] <= 40, "Latence normale hors plage"
        assert 0 <= m_normale["error_rate"] <= 1, "Erreur normale hors plage"
        assert m_normale["is_anomaly"] == 0, "Devrait être normal"
        print(f"   ✅ Mesure normale générée : "
              f"latence={m_normale['latency']}ms, "
              f"erreurs={m_normale['error_rate']}%")
        
        # Test mesure anormale
        m_panne = generer_metrique_panne("panne_wan")
        assert m_panne["is_anomaly"] == 1, "Devrait être anomalie"
        print(f"   ✅ Mesure anomalie générée : "
              f"latence={m_panne['latency']}ms, "
              f"erreurs={m_panne['error_rate']}%")
        
        return True
    except Exception as e:
        print(f"   ❌ Erreur : {e}")
        return False

def test_3_ecriture_lecture():
    """Test 3 : Écriture et lecture dans la base"""
    print("\n📋 TEST 3 — Écriture → Lecture")
    print("-" * 50)
    
    try:
        # Compter avant
        avant = compter_lignes()
        
        # Insérer 3 mesures de test
        for hote in ["R1", "SW1", "WEB_SERVER"]:
            metrique = generer_metrique_normale()
            inserer_mesure(hote, metrique)
        
        # Compter après
        apres = compter_lignes()
        nouvelles = apres - avant
        
        assert nouvelles == 3, f"Attendu 3 nouvelles lignes, obtenu {nouvelles}"
        print(f"   ✅ {nouvelles} mesures écrites et lues correctement")
        print(f"   ✅ Total base : {avant} → {apres}")
        
        return True
    except Exception as e:
        print(f"   ❌ Erreur : {e}")
        return False

def test_4_detection_normale():
    """Test 4 : Détection sur mesure normale"""
    print("\n TEST 4 — Détection mesure normale")
    print("-" * 50)
    
    try:
        resultat = detecter(25.0, 0.5, 45.0)
        
        assert resultat["is_anomaly"] == False, "Ne devrait pas être anomalie"
        assert resultat["cause"] == "normal", "Cause devrait être normal"
        
        print(f"   ✅ Mesure normale → is_anomaly: {resultat['is_anomaly']}")
        print(f"   ✅ Cause : {resultat['cause']}")
        
        return True
    except Exception as e:
        print(f"   ❌ Erreur : {e}")
        return False

def test_5_detection_anomalies():
    """Test 5 : Détection sur différentes anomalies"""
    print("\n TEST 5 — Détection anomalies")
    print("-" * 50)
    
    cas_tests = [
        {"latency": 999.0, "error_rate": 98.0, "traffic": 0.0,
         "cause_attendue": "machine_inaccessible_ou_cable",
         "nom": "Machine inaccessible"},
        {"latency": 450.0, "error_rate": 80.0, "traffic": 3.0,
         "cause_attendue": "panne_wan",
         "nom": "Panne WAN"},
        {"latency": 120.0, "error_rate": 35.0, "traffic": 16.0,
         "cause_attendue": "perte_paquets",
         "nom": "Perte de paquets"},
    ]
    
    succes = 0
    for cas in cas_tests:
        try:
            resultat = detecter(
                cas["latency"],
                cas["error_rate"],
                cas["traffic"]
            )
            assert resultat["is_anomaly"] == True
            assert resultat["cause"] == cas["cause_attendue"]
            print(f"   ✅ {cas['nom']} → {resultat['description']}")
            succes += 1
        except Exception as e:
            print(f"   ❌ {cas['nom']} → Erreur : {e}")
    
    return succes == len(cas_tests)

def test_6_pont_api():
    """Test 6 : Le pont API retourne des données correctes"""
    print("\n TEST 6 — Pont API")
    print("-" * 50)
    
    try:
        # Test métriques
        metrics = get_metrics_with_detection(limit=10)
        assert len(metrics) > 0, "Pas de métriques retournées"
        assert "is_anomaly" in metrics[0], "Champ is_anomaly manquant"
        assert "description" in metrics[0], "Champ description manquant"
        assert "conseil" in metrics[0], "Champ conseil manquant"
        print(f"   ✅ get_metrics_with_detection() → {len(metrics)} métriques")
        
        # Test alertes
        alertes = get_alerts_with_causes(limit=10)
        print(f"   ✅ get_alerts_with_causes() → {len(alertes)} alertes")
        if len(alertes) > 0:
            print(f"      Exemple : {alertes[0]['host']} → "
                  f"{alertes[0]['reason']}")
        
        return True
    except Exception as e:
        print(f"   ❌ Erreur : {e}")
        return False

def test_7_chaine_complete():
    """Test 7 : Test de la chaîne complète"""
    print("\n TEST 7 — Chaîne complète")
    print("-" * 50)
    
    try:
        avant = compter_lignes()
        
        # Injecter une anomalie connue
        anomalie = generer_metrique_panne("panne_wan")
        inserer_mesure("R1", anomalie)
        
        apres = compter_lignes()
        assert apres == avant + 1, "Mesure non insérée"
        
        # Vérifier que le détecteur la trouve
        resultats = detecter_lot(limit=5)
        
        anomalie_trouvee = any(
            r["is_anomaly"] and r["host"] == "R1"
            for r in resultats
        )
        
        assert anomalie_trouvee, "Anomalie non détectée dans les dernières mesures"
        
        print("   ✅ Anomalie injectée → stockée → détectée")
        print("   ✅ Chaîne complète fonctionnelle !")
        
        return True
    except Exception as e:
        print(f"   ❌ Erreur : {e}")
        return False

# Programme principal
if __name__ == "__main__":
    print("=" * 60)
    print(" TESTS DE BOUT EN BOUT — AI Network Copilot")
    print("=" * 60)
    print(f"Date : {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Lancer tous les tests
    tests = [
        test_1_base_de_donnees,
        test_2_simulateur,
        test_3_ecriture_lecture,
        test_4_detection_normale,
        test_5_detection_anomalies,
        test_6_pont_api,
        test_7_chaine_complete,
    ]
    
    resultats = []
    for test in tests:
        resultats.append(test())
    
    # Bilan final
    succes  = sum(resultats)
    echecs  = len(resultats) - succes
    
    print("\n" + "=" * 60)
    print(" BILAN FINAL")
    print("=" * 60)
    print(f"   Tests réussis  : {succes}/{len(resultats)}")
    print(f"   Tests échoués  : {echecs}/{len(resultats)}")
    
    if echecs == 0:
        print("\n TOUS LES TESTS SONT PASSÉS !")
        print("   La chaîne complète est fonctionnelle !")
    else:
        print("\n Certains tests ont échoué.")
        print("   Vérifier les erreurs ci-dessus.")