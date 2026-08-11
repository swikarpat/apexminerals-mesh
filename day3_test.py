from apexminerals.ml.ranking_engine import SupplierRankingEngine
from apexminerals.ml.drift_detector import DataDriftDetector

def run_day3_test():
    print("\n=== APEXMINERALS MESH: DAY 3 ML ENGINE TEST ===\n")

    # 1. Test the TaskRabbit-Style Ranking Engine
    print("--- 1. Testing Multi-Factor Supplier Ranking (XGBoost) ---")
    ranker = SupplierRankingEngine()
    
    # Mock data representing the nodes in our graph
    suppliers = [
        {
            "name": "Shadow Port A", "origin": "Vietnam", "china_ownership": 49.0,
            "geo_risk": 0.8, "itar_compliant": 0.0, "purity": 99.5, "lead_time": 7,
            "energy": "coal", "recycling": 0.0
        },
        {
            "name": "IREL India", "origin": "India", "china_ownership": 0.0,
            "geo_risk": 0.2, "itar_compliant": 1.0, "purity": 99.9, "lead_time": 14,
            "energy": "solar_hydro", "recycling": 15.0
        },
        {
            "name": "Lynas Rare Earths", "origin": "Australia", "china_ownership": 0.0,
            "geo_risk": 0.1, "itar_compliant": 1.0, "purity": 99.9, "lead_time": 21,
            "energy": "grid_mixed", "recycling": 5.0
        }
    ]
    
    print("Intent Profile: US DEFENSE (Zero tolerance for shadow trade)")
    defense_ranking = ranker.rank_suppliers(suppliers, intent_profile="defense")
    for i, sup in enumerate(defense_ranking):
        print(f"{i+1}. {sup['name']} | Score: {sup['final_score']}/100 | ESG: {sup['esg_score']} | Shadow Risk: {sup['shadow_risk']}")

    # 2. Test the Data Drift Detector
    print("\n--- 2. Testing Geopolitical Data Drift Detector ---")
    detector = DataDriftDetector()
    
    # Scenario: China normally exports ~5000 MT of Antimony. Suddenly drops to 200 MT (Export Ban).
    historical_antimony_exports = [5100, 4900, 5050, 4950, 5000, 4800]
    current_export_volume = 200 
    
    print(f"Historical Export Volumes (MT): {historical_antimony_exports}")
    print(f"Current Month Volume (MT): {current_export_volume}")
    
    drift_result = detector.detect_volume_anomaly(historical_antimony_exports, current_export_volume)
    print(f"Drift Alert: {drift_result['drift_detected']} | Severity: {drift_result['severity']} | {drift_result['message']}\n")

    print("=== DAY 3 SUCCESS ===")

if __name__ == "__main__":
    run_day3_test()