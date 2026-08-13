import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """
    Generates downloadable HTML/PDF Executive Test Execution Reports
    complete with step logs, duration telemetry, and self-healing audit details.
    """

    @staticmethod
    def generate_html_report(run_record: Dict[str, Any]) -> str:
        run_id = run_record.get("id") or run_record.get("run_id")
        status = run_record.get("status", "unknown").upper()
        duration = run_record.get("duration_ms", 0)
        total_steps = run_record.get("total_steps", 0)
        steps_passed = run_record.get("steps_passed", 0)
        steps_healed = run_record.get("steps_healed", 0)
        steps_failed = run_record.get("steps_failed", 0)
        step_logs = run_record.get("step_logs") or []
        healing_events = run_record.get("self_healing_events") or []

        status_color = "#10b981" if status == "PASSED" else ("#f59e0b" if status == "HEALED" else "#f43f5e")

        logs_rows = ""
        for log in step_logs:
            s_num = log.get("step_number")
            action = log.get("action")
            desc = log.get("target_description")
            sel = log.get("selector_used") or "auto"
            st = log.get("status")
            dur = log.get("execution_time_ms")
            logs_rows += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #334155; font-family: monospace;">#{s_num}</td>
                <td style="padding: 10px; border-bottom: 1px solid #334155;"><strong>{action}</strong></td>
                <td style="padding: 10px; border-bottom: 1px solid #334155;">{desc}</td>
                <td style="padding: 10px; border-bottom: 1px solid #334155; font-family: monospace; color: #94a3b8;">{sel}</td>
                <td style="padding: 10px; border-bottom: 1px solid #334155; font-weight: bold; color: {'#10b981' if st=='passed' else ('#f59e0b' if st=='healed' else '#f43f5e')}">{st.upper()}</td>
                <td style="padding: 10px; border-bottom: 1px solid #334155; font-family: monospace;">{dur}ms</td>
            </tr>
            """

        healing_rows = ""
        for h in healing_events:
            healing_rows += f"""
            <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 12px; border-radius: 8px; margin-top: 8px;">
                <div style="font-weight: bold; color: #f59e0b;">Step #{h.get('step_number')} Auto-Healed</div>
                <div style="font-family: monospace; color: #f43f5e; margin-top: 4px;">Failed Selector: {h.get('original_selector')}</div>
                <div style="font-family: monospace; color: #10b981; margin-top: 2px;">Healed Selector: {h.get('healed_selector')}</div>
                <div style="color: #cbd5e1; font-size: 12px; margin-top: 4px;">Reasoning: {h.get('reasoning')}</div>
            </div>
            """

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>AutoHealQA Test Execution Report - {run_id}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            margin: 0;
            padding: 30px;
        }}
        .card {{
            background: #1e293b;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            border: 1px solid #334155;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #334155;
            padding-bottom: 16px;
            margin-bottom: 20px;
        }}
        .badge {{
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 14px;
            background-color: {status_color}22;
            color: {status_color};
            border: 1px solid {status_color};
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }}
        @media print {{
            .no-print {{ display: none !important; }}
            body {{ background: white !important; color: black !important; padding: 0 !important; }}
            .card {{ background: white !important; border: 1px solid #cbd5e1 !important; color: black !important; }}
            th {{ background: #f1f5f9 !important; color: black !important; }}
            td {{ color: black !important; border-bottom: 1px solid #e2e8f0 !important; }}
        }}
        .metric {{
            background: #0f172a;
            padding: 16px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #334155;
        }}
        .metric-val {{
            font-size: 24px;
            font-weight: bold;
            font-family: monospace;
            margin-top: 4px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}
        th {{
            background: #0f172a;
            padding: 12px 10px;
            text-align: left;
            border-bottom: 2px solid #334155;
            color: #94a3b8;
            text-transform: uppercase;
            font-size: 11px;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <div>
                <h1 style="margin: 0; font-size: 24px;">AutoHealQA Executive Test Report</h1>
                <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 13px;">Run ID: {run_id} | Generated by AutoHeal Engine</p>
            </div>
            <div style="display: flex; gap: 12px; align-items: center;">
                <button onclick="window.print()" class="no-print" style="padding: 8px 16px; background: #6366f1; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;">
                    🖨️ Download / Save as PDF
                </button>
                <div class="badge">{status}</div>
            </div>
        </div>

        <div class="grid">
            <div class="metric">
                <div style="font-size: 11px; color: #94a3b8;">Total Steps</div>
                <div class="metric-val" style="color: #ffffff;">{total_steps}</div>
            </div>
            <div class="metric">
                <div style="font-size: 11px; color: #10b981;">Steps Passed</div>
                <div class="metric-val" style="color: #10b981;">{steps_passed}</div>
            </div>
            <div class="metric">
                <div style="font-size: 11px; color: #f59e0b;">Auto-Healed Steps</div>
                <div class="metric-val" style="color: #f59e0b;">{steps_healed}</div>
            </div>
            <div class="metric">
                <div style="font-size: 11px; color: #f43f5e;">Steps Failed</div>
                <div class="metric-val" style="color: #f43f5e;">{steps_failed}</div>
            </div>
        </div>

        <h2 style="font-size: 16px; margin-bottom: 12px;">Step Execution Log</h2>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Action</th>
                    <th>Target Description</th>
                    <th>Selector Used</th>
                    <th>Status</th>
                    <th>Duration</th>
                </tr>
            </thead>
            <tbody>
                {logs_rows}
            </tbody>
        </table>

        {f'<h2 style="font-size: 16px; margin-top: 24px; margin-bottom: 12px; color: #f59e0b;">Self-Healing Event Audit</h2>{healing_rows}' if healing_events else ''}
    </div>
</body>
</html>
"""
        return html_content


pdf_report_generator = PDFReportGenerator()
