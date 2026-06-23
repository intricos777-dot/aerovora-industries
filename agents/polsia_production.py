import json
import os
import subprocess
import sys
from datetime import datetime, timezone

POLSIA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, POLSIA_DIR)

from polsia.agents.base import BaseAgent


class ProductionAgent(BaseAgent):
    name = "production"
    description = "Manages the AeroFab-1 production pipeline — order processing, station advancement, QC"
    system_prompt = "You are Prod-Orch, the Production Orchestrator AI at Aerovora Industries. Your job is to keep the AV-1 Apis drone assembly line running at 85%+ utilization."

    def execute(self, context=""):
        api_base = "http://127.0.0.1:8777"
        output = []

        # 1. Check for new orders needing production
        orders = self._api_get(f"{api_base}/api/orders?status=payment_confirmed")
        if orders and len(orders) > 5:
            orders = json.loads(orders)

        if orders:
            output.append(f"Found {len(orders)} orders in production queue")

        # 2. Check units on the line and advance them
        units = self._api_get(f"{api_base}/api/production")
        if units and len(units) > 5:
            units = json.loads(units)

        if units:
            for unit in units:
                if isinstance(unit, dict) and unit.get("status") == "queued":
                    output.append(f"Unit {unit.get('serial', '?')} at station {unit.get('station', 0)} — queued")

        # 3. Check inventory levels
        inv = self._api_get(f"{api_base}/api/inventory?low_stock=true")
        if inv and len(inv) > 5:
            inv = json.loads(inv)

        if inv:
            low_items = [i.get("component", "?") for i in inv if isinstance(i, dict)]
            output.append(f"Low stock: {', '.join(low_items)}")

        # 4. Ask LLM for production analysis
        prompt = (
        f"Production Status:\n{chr(10).join(output) if output else 'No active production'}\n\n"
        f"Current time: {datetime.now(timezone.utc).isoformat()}\n"
        f"Target OEE: 78% | Target utilization: 85%\n\n"
        f"Identify bottlenecks, suggest prioritization, and list any reorder alerts needed."
        )

        llm_result = self.llm.structured_call(
            system_prompt=self.system_prompt,
            user_prompt=prompt,
        )
        return {
            "summary": llm_result.get("raw", str(llm_result))[:500],
            "orders_found": len(orders) if orders else 0,
            "units_in_production": len(units) if units else 0,
            "low_stock_alerts": len(inv) if inv else 0,
        }

    def _api_get(self, url):
        try:
            import urllib.request
            resp = urllib.request.urlopen(url, timeout=5)
            return resp.read().decode()
        except Exception as e:
            return f"API error: {e}"
