from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any

# Import our Core Modules
from apexminerals.security.token_vault import TokenVault
from apexminerals.mcp.server import MCPServer
from apexminerals.simulation.replay_engine import DeterministicReplaySimulator
from apexminerals.telemetry.tracer import CryptographicTracer

app = FastAPI(title="ApexMinerals Mesh API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize singletons
vault = TokenVault()
mcp = MCPServer()
simulator = DeterministicReplaySimulator()
tracer = CryptographicTracer()

class PromptRequest(BaseModel):
    text: str

class SimulationRequest(BaseModel):
    scenario: str

@app.get("/")
def read_root():
    return {"status": "ApexMinerals Backend is Active"}

@app.post("/api/clean-room/redact")
def redact_prompt(req: PromptRequest):
    redacted_text, token_map = vault.redact_and_tokenize(req.text)
    tracer.log_span("TXN-UI", "SecurityAgent", "REDACT_PROMPT", {"tokens_generated": len(token_map)})
    return {"original": req.text, "redacted": redacted_text, "token_map": token_map}

@app.get("/api/graph/trace/{entity_name}")
def trace_supply_chain(entity_name: str):
    rpc_request = f'{{"jsonrpc": "2.0", "method": "mcp_query_graph", "params": {{"entity_name": "{entity_name}"}}, "id": 1}}'
    response = mcp.handle_request(rpc_request)
    tracer.log_span("TXN-UI", "GraphAgent", "QUERY_NEO4J", {"entity": entity_name})
    return {"trace": response}

@app.post("/api/simulate")
def run_simulation(req: SimulationRequest):
    """Runs the XGBoost Ranking Engine against a Policy Shock."""
    historical_data = [
        {"name": "Shadow Port A", "origin": "Vietnam", "china_ownership": 49.0, "geo_risk": 0.8, "itar_compliant": 0.0, "purity": 99.5, "lead_time": 7, "energy": "coal", "recycling": 0.0},
        {"name": "IREL India", "origin": "India", "china_ownership": 0.0, "geo_risk": 0.2, "itar_compliant": 1.0, "purity": 99.9, "lead_time": 14, "energy": "solar_hydro", "recycling": 15.0},
        {"name": "Lynas Rare Earths", "origin": "Australia", "china_ownership": 0.0, "geo_risk": 0.1, "itar_compliant": 1.0, "purity": 99.9, "lead_time": 21, "energy": "grid_mixed", "recycling": 5.0}
    ]
    
    result = simulator.run_policy_shock_simulation(historical_data, shock_scenario=req.scenario)
    tracer.log_span("SIM-UI", "SimulatorAgent", "POLICY_SHOCK", {"scenario": req.scenario})
    
    return {
        "result": result,
        "latest_trace": tracer.trace_log[-1]
    }