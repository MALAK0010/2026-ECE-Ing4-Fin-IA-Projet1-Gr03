from utils import generate_synthetic_transactions, export_transactions_to_csv
from fraud_detector import FraudDetector

def test_run():
    print("🚀 Génération de données synthétiques avec fraudes injectées...")
    # On génère 1000 transactions avec 3 cycles de blanchiment et 2 schémas de smurfing
    txs = generate_synthetic_transactions(num_transactions=1000)
    
    # On initialise le détecteur
    detector = FraudDetector()
    detector.load_transactions(txs)
    detector.build_graph()
    
    print("🔍 Analyse des flux en cours...")
    results = detector.detect_all()
    
    # On affiche le rapport final
    print(detector.generate_report(results))

if __name__ == "__main__":
    test_run()