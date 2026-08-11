import os
from apexminerals.data.ingestion import DataIngestionEngine
from apexminerals.data.gsi_copilot import GeologicalCopilot
from apexminerals.graph.neo4j_schema import SupplyChainGraph
from apexminerals.mcp.server import MCPServer

def create_dummy_pdf():
    """Creates a dummy PDF for testing the GSI Copilot."""
    from reportlab.pdfgen import canvas
    os.makedirs("data", exist_ok=True)
    pdf_path = "data/Ambadongar_Survey.pdf"
    c = canvas.Canvas(pdf_path)
    c.drawString(100, 750, "Geological Survey of India - Ambadongar Carbonatite Complex")
    c.drawString(100, 730, "Location: Chota Udepur, Gujarat.")
    c.drawString(100, 710, "Estimated Reserves: 105 Million Tonnes.")
    c.drawString(100, 690, "Primary Elements: Neodymium, Praseodymium, Lanthanum.")
    c.save()
    return pdf_path

def run_day2_test():
    print("\n=== APEXMINERALS MESH: DAY 2 TEST RUN ===\n")

    # 1. Test Data Ingestion
    print("--- 1. Testing UN Comtrade Data Ingestion ---")
    ingestion = DataIngestionEngine()
    trade_data = ingestion.fetch_rare_earth_trade_data()
    print(f"Fetched {len(trade_data)} trade records.\n")

    # 2. Test Neo4j Graph Database
    print("--- 2. Testing Neo4j Supply Chain Graph ---")
    try:
        graph = SupplyChainGraph()
        graph.initialize_schema()
        # Ingest the data we just fetched
        for record in trade_data:
            graph.ingest_trade_route(
                source=record["alt_supplier"], 
                target="US Defense Prime", 
                material="HS2805 Rare Earths", 
                quantity=record["qty"]
            )
        print("Successfully built graph nodes and relationships in Neo4j!\n")
    except Exception as e:
        print(f"Neo4j Error: {e}. Is Docker running?\n")

    # 3. Test MCP Server (GraphRAG)
    print("--- 3. Testing MCP Server (JSON-RPC) ---")
    mcp = MCPServer()
    rpc_request = '{"jsonrpc": "2.0", "method": "mcp_query_graph", "params": {"entity_name": "US Defense Prime"}, "id": 1}'
    mcp_response = mcp.handle_request(rpc_request)
    print(f"MCP GraphRAG Response: {mcp_response}\n")

    # 4. Test GSI Geological Copilot (Local Ollama)
    print("--- 4. Testing GSI Geological Copilot (Ollama llama3.1:8b) ---")
    try:
        import reportlab # Required just for making the dummy PDF
    except ImportError:
        import subprocess
        subprocess.run(["pip", "install", "reportlab"])
        
    pdf_path = create_dummy_pdf()
    copilot = GeologicalCopilot()
    raw_text = copilot.extract_text_from_pdf(pdf_path)
    print("Extracting structured JSON from PDF using local LLM...")
    json_data = copilot.parse_assay_data(raw_text)
    print(f"Extracted Geological Data: {json_data}\n")

    print("=== DAY 2 SUCCESS ===")

if __name__ == "__main__":
    run_day2_test()