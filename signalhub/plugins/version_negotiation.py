"""Version negotiation — recusa plugin incompatível com Core/contrato."""

from __future__ import annotations

import re
from typing import Iterable

from signalhub import __version__ as CORE_VERSION
from signalhub.core.models.signal import SIGNAL_CONTRACT_VERSION

_SEMVER = re.compile(
    r"^v?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"
    r"(?:[-+][0-9A-Za-z.-]+)?$"
)


def parse_semver(value: str) -> tuple[int, int, int] | None:
    m = _SEMVER.match((value or "").strip())
    if not m:
        return None
    return int(m.group("major")), int(m.group("minor")), int(m.group("patch"))


def _cmp(a: tuple[int, int, int], b: tuple[int, int, int]) -> int:
    return (a > b) - (a < b)


def satisfies_constraint(version: str, constraint: str) -> bool:
    """Suporta: ``>=x.y.z``, ``<=``, ``>``, ``<``, ``==``, ``x.y.z``, vírgulas AND."""
    ver = parse_semver(version)
    if ver is None:
        return False
    raw = (constraint or "").strip()
    if not raw:
        return True
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    for part in parts:
        if not _satisfies_one(ver, part):
            return False
    return True


def _satisfies_one(ver: tuple[int, int, int], expr: str) -> bool:
    expr = expr.strip()
    for op in (">=", "<=", "==", ">", "<"):
        if expr.startswith(op):
            target = parse_semver(expr[len(op) :].strip())
            if target is None:
                return False
            c = _cmp(ver, target)
            if op == ">=":
                return c >= 0
            if op == "<=":
                return c <= 0
            if op == "==":
                return c == 0
            if op == ">":
                return c > 0
            if op == "<":
                return c < 0
    # bare semver = exact
    target = parse_semver(expr)
    if target is None:
        return False
    return _cmp(ver, target) == 0


def contract_compatible(plugin_contract: str, core_contract: str = SIGNAL_CONTRACT_VERSION) -> bool:
    """Mesma major = compatível (1.x com 1.y)."""
    a = parse_semver(plugin_contract)
    b = parse_semver(core_contract)
    if a is None or b is None:
        return False
    return a[0] == b[0]


def negotiate_plugin_versions(
    *,
    signalhub_version: str,
    contract_version: str,
    core_version: str = CORE_VERSION,
    core_contract: str = SIGNAL_CONTRACT_VERSION,
) -> list[str]:
    """Retorna lista de erros; vazia = pode carregar."""
    issues: list[str] = []
    if not satisfies_constraint(core_version, signalhub_version or ">=0.0.0"):
        issues.append(
            f"version negotiation: Core {core_version} não satisfaz "
            f"signalhub_version={signalhub_version!r} — plugin não carregado"
        )
    cv = (contract_version or core_contract).strip() or core_contract
    if not contract_compatible(cv, core_contract):
        issues.append(
            f"version negotiation: contract_version={cv!r} incompatível com "
            f"Core contract {core_contract} — plugin não carregado"
        )
    return issues


def provider_version_fields(
    *,
    plugin_version: str,
    contract_version: str,
    core_version: str = CORE_VERSION,
) -> dict[str, str]:
    return {
        "contract_version": contract_version or SIGNAL_CONTRACT_VERSION,
        "core_version": core_version,
        "plugin_version": plugin_version,
    }


def summarize_negotiation(issues: Iterable[str]) -> dict[str, object]:
    errs = list(issues)
    return {"ok": not errs, "issues": errs}
