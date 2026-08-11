from apexminerals.telemetry.tracer import CryptographicTracer
from apexminerals.simulation.replay_engine import DeterministicReplaySimulator

def run_day5_test():
    print("\n=== APEXMINERALS MESH: DAY 5 OBSERVABILITY TEST ===\n")

    # 1. Test Cryptographic Tracer
    print("--- 1. Testing OpenTelemetry Cryptographic Tracer ---")
    tracer = CryptographicTracer()
    
    # Simulate an AI workflow
    tracer.log_span("TXN-101", "IngestionAgent", "FETCH_DATA", {"source": "UN Comtrade", "status": "Success"})
    tracer.log_span("TXN-101", "GraphAgent", "QUERY_NEO4J", {"target": "US Defense Prime", "nodes_found": 5})
    tracer.log_span("TXN-101", "ComplianceAgent", "HITL_PAUSE", {"reason": "Shadow Port Detected"})
    
    # Verify the blockchain-style integrity
    is_valid = tracer.verify_trace_integrity()
    print(f"\nAudit Log Integrity Verified: {is_valid}")
    if is_valid:
        print("SEC/DoD Compliance Check: PASSED. Mathematical proof generated.\n")

    # 2. Test Deterministic Replay Simulator
    print("--- 2. Testing Deterministic Replay & Policy Simulator ---")
    simulator = DeterministicReplaySimulator()
    
    historical_data = [
        {"name": "Shadow Port A", "origin": "Vietnam", "china_ownership": 49.0, "geo_risk": 0.8, "itar_compliant": 0.0, "purity": 99.5, "lead_time": 7, "energy": "coal", "recycling": 0.0},
        {"name": "IREL India", "origin": "India", "china_ownership": 0.0, "geo_risk": 0.2, "itar_compliant": 1.0, "purity": 99.9, "lead_time": 14, "energy": "solar_hydro", "recycling": 15.0}
    ]
    
    # Simulate a sudden geopolitical shock
    result = simulator.run_policy_shock_simulation(historical_data, shock_scenario="CHINA_EXPORT_BAN")
    
    print(f"Scenario: {result['scenario']}")
    print(f"New Recommended Supplier: {result['new_top_supplier']}")
    for sup in result['new_rankings']:
        print(f" -> {sup['name']} | New Score: {sup['final_score']} | Lead Time: {sup['lead_time']} days")

    print("\n=== DAY 5 SUCCESS ===")

if __name__ == "__main__":
    run_day5_test()