import json
from typing import Dict, Any
from apexminerals.graph.neo4j_schema import SupplyChainGraph

class MCPServer:
    """
    Implements the Model Context Protocol (MCP) via JSON-RPC.
    Isolates the LLM from direct database access.
    """
    def __init__(self):
        self.graph_db = SupplyChainGraph()

    def handle_request(self, rpc_request: str) -> str:
        """Parses JSON-RPC request and routes to the correct tool."""
        try:
            req = json.loads(rpc_request)
            method = req.get("method")
            params = req.get("params", {})
            req_id = req.get("id", 1)

            if method == "mcp_query_graph":
                result = self.graph_db.trace_origin(params.get("entity_name"))
                return self._format_response(req_id, result)
            
            elif method == "mcp_check_sanctions":
                # Mock sanction check for Day 2
                entity = params.get("entity_name")
                is_sanctioned = entity in ["Shadow Port A", "Sanctioned Corp"]
                return self._format_response(req_id, {"sanctioned": is_sanctioned})
            
            else:
                return self._format_error(req_id, -32601, f"Method '{method}' not found.")
                
        except json.JSONDecodeError:
            return self._format_error(None, -32700, "Parse error")

    def _format_response(self, req_id: Any, result: Any) -> str:
        return json.dumps({"jsonrpc": "2.0", "result": result, "id": req_id})

    def _format_error(self, req_id: Any, code: int, message: str) -> str:
        return json.dumps({"jsonrpc": "2.0", "error": {"code": code, "message": message}, "id": req_id})