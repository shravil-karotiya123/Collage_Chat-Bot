"""
Server-Rendered Local Operator Console Dashboard Generator.
"""

from typing import Any, Dict
from src.operator.operator_service import OperatorService


class DashboardService:
    """
    Renders a modern, offline-capable HTML/CSS Operator Console dashboard.
    Exposes zero external CDN dependencies.
    """

    def __init__(self, operator_service: OperatorService) -> None:
        self.operator_service = operator_service

    def render_dashboard_html(self) -> str:
        """Render complete HTML page for GET /operator/dashboard."""
        sys_status = self.operator_service.system_service.get_system_status()
        mem_status = self.operator_service.system_service.get_memory_diagnostics()
        models = self.operator_service.get_models_overview()
        metrics = self.operator_service.metrics_collector.get_metrics()
        sec_status = self.operator_service.security_service.get_security_status()
        tasks = self.operator_service.get_tasks_summary()[:10]
        audit_events = self.operator_service.audit_logger.get_events(limit=10)

        vram = mem_status.get("vram", {})
        ram = mem_status.get("ram", {})

        tasks_rows = "".join([
            f"<tr><td><code>{t['task_id']}</code></td><td>{t['intent']}</td>"
            f"<td><span class='badge badge-{t['agent_status'].lower()}'>{t['agent_status']}</span></td>"
            f"<td>{t['risk_level']}</td><td>{t['created_at']}</td></tr>"
            for t in tasks
        ]) or "<tr><td colspan='5' class='empty'>No active tasks recorded</td></tr>"

        audit_rows = "".join([
            f"<tr><td>{e['timestamp']}</td><td><strong>{e['event_type']}</strong></td>"
            f"<td><code>{e.get('task_id') or e['request_id']}</code></td><td>{e['status']}</td></tr>"
            for e in audit_events
        ]) or "<tr><td colspan='4' class='empty'>No audit events recorded</td></tr>"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MRPL AI Workbench — Operator Console</title>
    <style>
        :root {{
            --bg: #0f172a;
            --card-bg: #1e293b;
            --border: #334155;
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --primary: #38bdf8;
            --success: #22c55e;
            --warning: #f59e0b;
            --danger: #ef4444;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, -apple-system, sans-serif; }}
        body {{ background: var(--bg); color: var(--text); padding: 20px; line-height: 1.5; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; padding-bottom: 20px; border-bottom: 1px solid var(--border); margin-bottom: 24px; }}
        .header h1 {{ font-size: 1.5rem; font-weight: 700; color: var(--primary); }}
        .subtitle {{ font-size: 0.875rem; color: var(--text-muted); }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-bottom: 24px; }}
        .card {{ background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 18px; }}
        .card-title {{ font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin-bottom: 12px; font-weight: 600; }}
        .stat {{ font-size: 1.75rem; font-weight: 700; color: var(--primary); }}
        .stat-sub {{ font-size: 0.8rem; color: var(--text-muted); margin-top: 4px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 0.875rem; }}
        th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--border); }}
        th {{ background: #0f172a; color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase; }}
        code {{ font-family: monospace; background: #090d16; padding: 2px 6px; border-radius: 4px; font-size: 0.8rem; color: #7dd3fc; }}
        .badge {{ padding: 3px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }}
        .badge-completed {{ background: rgba(34, 197, 94, 0.2); color: var(--success); }}
        .badge-waiting_for_approval {{ background: rgba(245, 158, 11, 0.2); color: var(--warning); }}
        .badge-executing {{ background: rgba(56, 189, 248, 0.2); color: var(--primary); }}
        .badge-failed {{ background: rgba(239, 68, 68, 0.2); color: var(--danger); }}
        .empty {{ text-align: center; color: var(--text-muted); padding: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>MRPL AI WORKBENCH</h1>
            <div class="subtitle">Operator Console & Sovereign Subsystem Governance</div>
        </div>
        <div style="text-align: right;">
            <span class="badge badge-completed">SYSTEM ONLINE</span>
            <div class="subtitle" style="margin-top: 4px;">Version {sys_status['workbench_version']} | Uptime {sys_status['uptime_seconds']}s</div>
        </div>
    </div>

    <div class="grid">
        <div class="card">
            <div class="card-title">Memory & Hardware (VRAM/RAM)</div>
            <div class="stat">{ram['used_ram_mb']} / {ram['configured_budget_mb']} MB RAM</div>
            <div class="stat-sub">GPU VRAM Budget: {vram['configured_budget_mb']} MB (GPU: {vram['device_name']})</div>
        </div>
        <div class="card">
            <div class="card-title">Active LLM Models</div>
            <div class="stat">{models['configured_models']['qwen']}</div>
            <div class="stat-sub">DeepSeek: {models['configured_models']['deepseek']} | Vision: {models['configured_models']['vision']}</div>
        </div>
        <div class="card">
            <div class="card-title">Total Requests & Agent Tasks</div>
            <div class="stat">{metrics.get('http_requests_total', 0)} reqs</div>
            <div class="stat-sub">Agent Tasks: {metrics.get('agent_tasks_completed_total', 0)} completed / {metrics.get('agent_tasks_failed_total', 0)} failed</div>
        </div>
        <div class="card">
            <div class="card-title">Security & Governance</div>
            <div class="stat">Auth: {"ENABLED" if sec_status['authentication_enabled'] else "DISABLED"}</div>
            <div class="stat-sub">Blocked Tools: {sec_status['blocked_tools_count']} | Security Events: {sec_status['security_violations_count']}</div>
        </div>
    </div>

    <div class="grid" style="grid-template-columns: 1fr 1fr;">
        <div class="card">
            <div class="card-title">Recent Agent Workflows</div>
            <table>
                <thead>
                    <tr><th>Task ID</th><th>Intent</th><th>Status</th><th>Risk</th><th>Created</th></tr>
                </thead>
                <tbody>{tasks_rows}</tbody>
            </table>
        </div>
        <div class="card">
            <div class="card-title">Security & Audit Trajectory</div>
            <table>
                <thead>
                    <tr><th>Time</th><th>Event Type</th><th>ID</th><th>Status</th></tr>
                </thead>
                <tbody>{audit_rows}</tbody>
            </table>
        </div>
    </div>
</body>
</html>"""
        return html
