"""CLI — Core ops + Developer Platform (create / validate / doctor)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="signalhub",
        description=(
            "SignalHub — signal-processing framework (deterministic Core). "
            "Extend via plugins; do not modify Core."
        ),
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_caps = sub.add_parser("capabilities", help="List capabilities")
    p_caps.add_argument("--json", action="store_true")

    p_run = sub.add_parser("run", help="Execute a capability")
    p_run.add_argument("capability_id")
    p_run.add_argument("--args", default="{}", help="JSON arguments")

    sub.add_parser("mcp", help="Run MCP stdio server")
    sub.add_parser("admin-snapshot", help="Dump admin snapshot JSON")

    # Developer Platform
    p_create = sub.add_parser("create", help="Scaffold a plugin component")
    p_create.add_argument(
        "kind",
        choices=["provider", "capability", "adapter", "consumer", "ruleset"],
    )
    p_create.add_argument("name")
    p_create.add_argument("--root", default="plugins", help="Output directory")
    p_create.add_argument("--author", default="community")

    p_val = sub.add_parser("validate", help="Validate a plugin directory")
    p_val.add_argument("plugin", nargs="?", default=".", help="Path to plugin or 'plugin'")
    p_val.add_argument("--path", default=None, help="Explicit plugin path")

    p_test = sub.add_parser("test", help="Test a provider plugin (contract)")
    p_test.add_argument("target", choices=["provider", "plugin"])
    p_test.add_argument("path", help="Plugin directory")

    p_doctor = sub.add_parser("doctor", help="Environment + plugins health")
    p_doctor.add_argument(
        "--full",
        action="store_true",
        help="Validate contract, providers, adapters, capabilities, storage, plugins, MCP, REST, Telegram",
    )
    sub.add_parser("contract-check", help="RFC-0001 contract check (core + plugins)")
    sub.add_parser("health", help="Separated health checks (JSON)")

    p_plugins = sub.add_parser("plugins", help="List discovered plugins")
    p_plugins.add_argument("--json", action="store_true")

    sub.add_parser("mission-control", help="Lab status board (JSON)")

    p_lab = sub.add_parser("lab", help="Laboratory: generate / export / replay synthetic signals")
    lab_sub = p_lab.add_subparsers(dest="lab_cmd", required=True)
    p_gen = lab_sub.add_parser("generate", help="Generate Test Signal via debug provider")
    p_gen.add_argument("--mode", default="valid", help="valid|invalid|high_score|...")
    p_gen.add_argument("--limit", type=int, default=1)
    p_exp = lab_sub.add_parser("export", help="Export stored signals to JSON")
    p_exp.add_argument("path", nargs="?", default="lab-signals.json")
    p_exp.add_argument("--limit", type=int, default=100)
    p_rep = lab_sub.add_parser("replay", help="Replay signals JSON through Core pipeline")
    p_rep.add_argument("path", help="JSON file from lab export")

    args = parser.parse_args(argv)

    if args.cmd == "capabilities":
        from signalhub.bootstrap import build_container

        caps = build_container().capabilities.list_capabilities()
        if args.json:
            print(
                json.dumps(
                    [{"id": c.id, "tool": c.tool_name, "name": c.name} for c in caps],
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            for c in caps:
                print(f"{c.id}\t{c.tool_name}\t{c.name}")
        return 0

    if args.cmd == "run":
        from signalhub.bootstrap import build_orchestrator

        payload = json.loads(args.args)
        result = build_orchestrator().execute_capability(args.capability_id, payload)
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0 if not result.status.startswith("error") else 1

    if args.cmd == "mcp":
        from signalhub.apps.mcp.server import run_stdio_server

        run_stdio_server()
        return 0

    if args.cmd == "admin-snapshot":
        from signalhub.admin_snapshot import build_admin_snapshot
        from signalhub.bootstrap import build_container

        print(json.dumps(build_admin_snapshot(build_container()), ensure_ascii=False))
        return 0

    if args.cmd == "create":
        from signalhub.sdk.scaffold import create_component

        path = create_component(
            args.kind,
            args.name,
            root=Path(args.root),
            author=args.author,
        )
        print(f"created {path}")
        print("next: implement search()/execute() — keep Core untouched")
        return 0

    if args.cmd == "validate":
        from signalhub.sdk.devtools import validate_plugin

        plugin_path = Path(args.path) if args.path else Path(args.plugin)
        if plugin_path.name == "plugin" and not (plugin_path / "plugin.yaml").exists():
            plugin_path = Path(args.plugin)
        report = validate_plugin(plugin_path.resolve())
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["ok"] else 1

    if args.cmd == "test":
        from signalhub.sdk.devtools import validate_plugin

        report = validate_plugin(Path(args.path).resolve())
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["ok"] else 1

    if args.cmd == "doctor":
        from signalhub.sdk.devtools import doctor

        report = doctor(full=bool(getattr(args, "full", False)))
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["ok"] else 1

    if args.cmd == "health":
        from signalhub.bootstrap import build_container
        from signalhub.platform.health import run_all_health_checks

        report = run_all_health_checks(build_container(load_plugins=True))
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["ok"] else 1

    if args.cmd == "contract-check":
        from signalhub.sdk.devtools import contract_check

        report = contract_check()
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["ok"] else 1

    if args.cmd == "plugins":
        from signalhub.plugins import PluginLoader

        report = PluginLoader().load_all()
        rows = [
            {
                "name": p.manifest.name,
                "version": p.manifest.version,
                "ok": p.ok,
                "errors": p.errors,
            }
            for p in report.loaded
        ]
        if args.json:
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        else:
            if not rows:
                print("(nenhum plugin encontrado)")
            for r in rows:
                flag = "OK" if r["ok"] else "FAIL"
                print(f"{flag}\t{r['name']}\tv{r['version']}")
                for e in r["errors"]:
                    print(f"  - {e}")
        return 0 if all(r["ok"] for r in rows) else 1

    if args.cmd == "mission-control":
        from signalhub.lab import mission_control_status

        report = mission_control_status()
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report.get("core", {}).get("ok") else 1

    if args.cmd == "lab":
        from signalhub.lab import (
            export_to_path,
            generate_synthetic,
            replay_from_path,
        )

        if args.lab_cmd == "generate":
            report = generate_synthetic(mode=args.mode, limit=args.limit)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0 if report.get("ok") else 1
        if args.lab_cmd == "export":
            report = export_to_path(Path(args.path), limit=args.limit)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0 if report.get("ok") else 1
        if args.lab_cmd == "replay":
            report = replay_from_path(Path(args.path))
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0 if report.get("ok") else 1
        return 2

    return 2


if __name__ == "__main__":
    sys.exit(main())
