from apexminerals.agents.a2a_protocol import A2AMessageEnvelope, A2ARouter
from apexminerals.agents.supervisor import MultiAgentSupervisor
from apexminerals.governance.hitl_pause import HITLGovernor
from apexminerals.resilience.circuit_breaker import APICircuitBreaker
from apexminerals.agents.fsm_engine import DeterministicFSMEngine

def mock_primary_api():
    raise ConnectionError("503 Service Unavailable")

def mock_backup_api():
    return "Backup API Response: Success"

def run_day4_test():
    print("\n=== APEXMINERALS MESH: DAY 4 GOVERNANCE TEST ===\n")

    # 1. Test A2A Protocol & Supervisor
    print("--- 1. Testing A2A Protocol & Anti-Amplification Supervisor ---")
    supervisor = MultiAgentSupervisor(minimum_confidence=0.85)
    
    envelope_good = A2AMessageEnvelope(
        sender_agent_id="OriginTracingAgent",
        recipient_agent_id="ComplianceAgent",
        intent_capability="VERIFY_ITAR",
        payload_data={"supplier": "IREL India"},
        confidence_score=0.95
    )
    
    envelope_bad = A2AMessageEnvelope(
        sender_agent_id="OriginTracingAgent",
        recipient_agent_id="ComplianceAgent",
        intent_capability="VERIFY_ITAR",
        payload_data={"supplier": "Unknown Entity"},
        confidence_score=0.60
    )

    if supervisor.evaluate_handoff(envelope_good):
        print(f"Good Handoff: {A2ARouter.dispatch(envelope_good)}")
    if not supervisor.evaluate_handoff(envelope_bad):
        print("Bad Handoff successfully blocked.\n")

    # 2. Test API Circuit Breaker
    print("--- 2. Testing API Circuit Breaker ---")
    breaker = APICircuitBreaker(failure_threshold=1)
    result = breaker.execute(mock_primary_api, mock_backup_api)
    print(f"Circuit Breaker Result: {result}\n")

    # 3. Test Stateful FSM & HITL Pause
    print("--- 3. Testing FSM Engine & HITL Async Suspension ---")
    mock_dag = {
        "VERIFY_ORIGIN": {"action_type": "GRAPH_ORIGIN_TRACE", "next_allowed": ["CHECK_TRANSSHIPMENT"]},
        "CHECK_TRANSSHIPMENT": {"action_type": "ANOMALY_DETECTION", "next_allowed": ["COMPLETED"]},
        "COMPLETED": {"action_type": "DRAFT_PO", "next_allowed": []}
    }
    
    fsm = DeterministicFSMEngine(mock_dag)
    exec_id = "TXN-998877"
    
    # Run FSM (Will pause at ANOMALY_DETECTION)
    fsm.execute_workflow(exec_id, "VERIFY_ORIGIN")
    
    # Simulate Human clicking "Approve Reroute" in the UI/Slack
    print("--- Human Manager clicks 'Approve Reroute' ---")
    governor = HITLGovernor()
    restored_memory = governor.hydrate_and_resume(exec_id, "APPROVED")
    
    # Inject restored memory and resume FSM
    fsm.memory = restored_memory
    fsm.execute_workflow(exec_id, "CHECK_TRANSSHIPMENT")

    print("\n=== DAY 4 SUCCESS ===")

if __name__ == "__main__":
    run_day4_test()