from apexminerals.security.token_vault import TokenVault
from apexminerals.security.semantic_cache import SemanticCache
from apexminerals.hardware.vram_router import HardwareRouter
from apexminerals.compiler.agentscript import AgentDSLCompiler

def run_day1_test():
    print("\n=== APEXMINERALS MESH: DAY 1 TEST RUN ===\n")

    # 1. Test Token Vault (Zero-Trust Clean Room)
    print("--- 1. Testing Token Vault ---")
    vault = TokenVault()
    raw_prompt = "Analyze the pending procurement of 15 MT of NdFeB alloy from Supplier #REF-8839 for $450,000."
    redacted_prompt, token_map = vault.redact_and_tokenize(raw_prompt)
    print(f"Original: {raw_prompt}")
    print(f"Redacted (Sent to LLM): {redacted_prompt}")
    print(f"Rehydrated (Back to User): {vault.rehydrate(redacted_prompt)}\n")

    # 2. Test Semantic Cache
    print("--- 2. Testing Semantic Cache ---")
    cache = SemanticCache()
    cache.add_to_cache(redacted_prompt, "Supplier approved. Zero ITAR violations.")
    cached_result = cache.check_cache(redacted_prompt)
    print(f"Cache Hit Result: {cached_result}\n")

    # 3. Test AgentScript Compiler & AST Profiler
    print("--- 3. Testing AgentScript Compiler ---")
    yaml_spec = """
    agent:
      agent_name: "ITAR_AuditAgent"
      version: "1.0.0"
      entry_state: "VERIFY_ORIGIN"
      allowed_tools: ["mcp_neo4j_graph", "mcp_sanctions_check"]
      max_token_budget: 5000
      steps:
        - state: "VERIFY_ORIGIN"
          allowed_transitions: ["CHECK_TRANSSHIPMENT"]
          action: "GRAPH_ORIGIN_TRACE"
        - state: "CHECK_TRANSSHIPMENT"
          allowed_transitions: ["COMPLETED"]
          action: "ANOMALY_DETECTION"
    """
    compiler = AgentDSLCompiler()
    fsm = compiler.compile_yaml_to_fsm(yaml_spec)
    complexity_score = compiler.profile_complexity(fsm)
    print(f"Compiled FSM States: {list(fsm['compiled_dag'].keys())}")
    print(f"AST Complexity Score: {complexity_score}\n")

    # 4. Test Hardware Router
    print("--- 4. Testing Hardware Router ---")
    router = HardwareRouter()
    assigned_model = router.route_model(complexity_score)
    print(f"Current Unified Memory Usage: {router.get_system_memory_usage()}%")
    print(f"Assigned Execution Model: {assigned_model}\n")
    print("=== DAY 1 SUCCESS ===")

if __name__ == "__main__":
    run_day1_test()