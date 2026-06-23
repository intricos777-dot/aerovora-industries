import json
import sys
import os
from datetime import datetime, timezone

POLSIA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, POLSIA_DIR)

from polsia.agents.base import BaseAgent


class LogisticsAgent(BaseAgent):
    name = "logistics"
    description = "Manages shipping, receiving, inventory, and supplier orders"
    system_prompt = "You are Log-Orch, the Logistics Orchestrator AI at Aerovora Industries. You manage shipping, receiving, inventory levels, and supplier coordination."

    def execute(self, context=""):
        api_base = "http://127.0.0.1:8777"
        output = []

        # 1. Check for orders ready to ship
        ready = self._api_get(f"{api_base}/api/production")
        if ready and len(ready) > 5:
            ready = json.loads(ready)

        if ready:
            ready_units = [u for u in ready if isinstance(u, dict) and u.get("status") == "ready_to_ship"]
            if ready_units:
                output.append(f"Units ready to ship: {len(ready_units)}")

        # 2. Check low stock for auto-reorder
        low = self._api_get(f"{api_base}/api/inventory?low_stock=true")
        if low and len(low) > 5:
            low = json.loads(low)

        if low:
            for item in low:
                if isinstance(item, dict):
                    output.append(
                        f"REORDER: {item.get('component')} ({item.get('sku')}) — "
                        f"qty {item.get('quantity')}, min {item.get('min_stock')}, "
                        f"lead {item.get('lead_time_days')}d"
                    )

        # 3. Check supplier orders
        suppliers = self._api_get(f"{api_base}/api/suppliers?status=pending")
        if suppliers and len(suppliers) > 5:
            suppliers = json.loads(suppliers)

        if suppliers:
            output.append(f"Pending supplier orders: {len(suppliers)}")

        # 4. Get system status
        status = self._api_get(f"{api_base}/api/status")
        if status and len(status) > 5:
            status = json.loads(status)

        prompt = (
            f"Logistics Status:\n{chr(10).join(output) if output else 'All clear'}\n\n"
            f"System: {json.dumps(status)[:500] if status else 'N/A'}\n"
            f"Current time: {datetime.now(timezone.utc).isoformat()}\n\n"
            f"Identify any shipping bottlenecks, suggest reorder actions, "
            f"and recommend dispatch priorities."
        )

        llm_result = self.llm.structured_call(
            system_prompt=self.system_prompt,
            user_prompt=prompt,
        )

        return {
            "summary": llm_result.get("raw", str(llm_result))[:500],
            "ready_to_ship": len([u for u in ready if isinstance(u, dict) and u.get("status") == "ready_to_ship"]) if ready else 0,
            "low_stock_items": len(low) if low else 0,
            "pending_pos": len(suppliers) if suppliers else 0,
        }

    def _api_get(self, url):
        try:
            import urllib.request
            resp = urllib.request.urlopen(url, timeout=5)
            return resp.read().decode()
        except Exception:
            return None
