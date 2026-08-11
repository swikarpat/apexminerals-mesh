import sqlite3
import json
from typing import Dict, Any
from apexminerals.config.settings import settings

class HITLGovernor:
    def __init__(self):
        self.db_path = settings.DATA_DIR / "hitl_state.sqlite"
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS suspended_executions (
                    execution_id TEXT PRIMARY KEY,
                    state_memory TEXT,
                    status TEXT
                )
            """)
            conn.commit()

    def suspend_execution(self, execution_id: str, current_memory: Dict[str, Any], alert_message: str):
        """Hard-pauses the FSM and saves state to disk."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO suspended_executions (execution_id, state_memory, status) VALUES (?, ?, ?)",
                (execution_id, json.dumps(current_memory), "PAUSED_PENDING_HUMAN")
            )
            conn.commit()
        
        # Simulate sending a Slack/Teams webhook to the Defense Procurement Officer
        print(f"\n🚨 [SLACK WEBHOOK FIRED] To: Procurement Manager")
        print(f"🚨 ALERT: {alert_message}")
        print(f"🚨 Execution {execution_id} suspended. Awaiting human approval...\n")

    def hydrate_and_resume(self, execution_id: str, human_decision: str) -> Dict[str, Any]:
        """Loads state back into memory after human clicks 'Approve' or 'Reject'."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT state_memory FROM suspended_executions WHERE execution_id = ?", (execution_id,))
            row = cursor.fetchone()
            
            if row:
                memory = json.loads(row[0])
                memory["human_override"] = human_decision
                
                cursor.execute("UPDATE suspended_executions SET status = ? WHERE execution_id = ?", ("RESUMED", execution_id))
                conn.commit()
                return memory
            else:
                raise ValueError("Execution ID not found.")