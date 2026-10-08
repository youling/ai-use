"""Reproducible actual Textual SVG evidence using public synthetic metadata only.

Run: python agent-runtime/setup/scripts/capture_v2.py --output-dir PATH
No native probe, credentials, Host apply or network is used by this script.
"""
from __future__ import annotations
import argparse
import asyncio
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_setup.tui import SetupApp


class EvidenceEngine:
    """Synthetic visual renderer seam; never substitutes for adapter acceptance."""
    def probe(self):
        return {"platform": "windows", "python_verified": True, "python_version": "3.14.8", "wsl_app_version": "3.0.1", "wslc_capability": {"state": "PASS"}, "volumes": [{"fs": "NTFS", "free_bytes": 80 * 2**30}]}

    def plan(self, probe, **kwargs):
        names = [("工作区", "workspace", "workspaces"), ("配置", "config", "config"), ("缓存", "cache", "cache"), ("临时文件", "temp", "attempts")]
        roots = {key: {"path": "C:/Example/AgentRuntime/" + leaf} for _, key, leaf in names}
        rows = [{"name": key, "label": label, "path": roots[key]["path"], "media": "NVMe SSD", "free": "80 GiB", "reason": "New scoped root on selected volume"} for label, key, _ in names]
        rows += [{"name": "exchange", "label": "Exchange", "path": "C:/Example/AgentRuntime/exchange", "media": "NVMe SSD", "free": "80 GiB", "reason": "Bound exchange attempt"}, {"name": "host_agent", "label": "HOST_AGENT.md", "path": "C:/Example/Documents/HOST_AGENT.md", "media": "NTFS", "free": "80 GiB", "reason": "Known Folder discovery; existing hash checked"}]
        return {"status": "READY", "fingerprint": "synthetic-only", "host_authorized": False, "roots": roots, "placement_rows": rows}

    def discover_credentials(self):
        return {"github": {"state": "REUSE_NOT_SUPPORTED", "provider": "GitHub", "next_action": "HOST_GITHUB_DEVICE_LOGIN", "repo": "", "permissions": "尚未批准", "reason_code": "HOST_CUSTODIAN_CONNECTION_REQUIRED"}, "model": {"state": "NEEDS_CONNECTION", "provider": "未选择", "next_action": "HOST_PROVIDER_LOGIN", "reason_code": "HOST_CUSTODIAN_CONNECTION_REQUIRED"}}


async def capture(directory: Path):
    records = []
    for size in [(80, 24), (120, 40)]:
        app = SetupApp(EvidenceEngine())
        async with app.run_test(size=size) as pilot:
            app.probe_data = app.engine.probe()
            app.plan_data = app.engine.plan(app.probe_data, overrides={}, github={}, model={}, durable={})
            app.credentials = app.engine.discover_credentials()
            for step, name in enumerate(["check", "placement", "accounts", "review", "results"]):
                app.step = step
                if step == 4:
                    app.result = {"capabilities": {"local_install": {"state": "PASS"}, "github": {"state": "NOT_AUTHORIZED"}, "model": {"state": "NOT_AUTHORIZED"}, "fresh_recovery": {"state": "NOT_AUTHORIZED"}}}
                await app.render_step()
                await pilot.pause(0.3)
                svg = app.export_screenshot(title=f"SYNTHETIC ONLY · Setup V2 · {name} · {size[0]}x{size[1]}")
                svg = "\n".join(line.rstrip() for line in svg.splitlines()) + "\n"
                assert "D:/coding" not in svg and "gg828" not in svg and "ghp_" not in svg
                filename = f"v2-{name}-{size[0]}x{size[1]}.svg"
                (directory / filename).write_text(svg, encoding="utf-8", newline="\n")
                records.append({"file": filename, "sha256": hashlib.sha256(svg.encode()).hexdigest(), "size": list(size), "scenario": name})
    for record in records:
        assert hashlib.sha256((directory / record["file"]).read_bytes()).hexdigest() == record["sha256"]
    (directory / "manifest.json").write_text(json.dumps({"evidence": "actual Textual render / synthetic engine only / no Host acceptance", "screenshots": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    asyncio.run(capture(args.output_dir))
