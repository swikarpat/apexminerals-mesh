from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any

# Import our existing Day 1 & Day 2 modules
from apexminerals.security.token_vault import TokenVault
from apexminerals.mcp.server import MCPServer

app = FastAPI(title="ApexMinerals Mesh API", version="1.0.0")

# Allow Next.js frontend to communicate with this backend
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

class PromptRequest(BaseModel):
    text: str

@app.get("/")
def read_root():
    return {"status": "ApexMinerals Backend is Active"}

@app.post("/api/clean-room/redact")
def redact_prompt(req: PromptRequest):
    """Passes text through the Zero-Trust Token Vault."""
    redacted_text, token_map = vault.redact_and_tokenize(req.text)
    return {"original": req.text, "redacted": redacted_text, "token_map": token_map}

@app.get("/api/graph/trace/{entity_name}")
def trace_supply_chain(entity_name: str):
    """Queries the Neo4j Graph via MCP."""
    rpc_request = f'{{"jsonrpc": "2.0", "method": "mcp_query_graph", "params": {{"entity_name": "{entity_name}"}}, "id": 1}}'
    response = mcp.handle_request(rpc_request)
    return {"trace": response}

# Run with: uvicorn apexminerals.api.main:app --reload