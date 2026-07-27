"""RFC-0001 + platform tests."""
from __future__ import annotations

import json

from signalhub.apps.mcp.server import McpServer
from signalhub.bootstrap import build_container, build_orchestrator
from signalhub.core.contracts.pipeline import PipelineContext
from signalhub.core.models import Provenance, Signal, SignalType
from signalhub.core.models.common import EntityId
from signalhub.core.models.signal import SIGNAL_CONTRACT_VERSION, SignalStatus
from signalhub.core.pipeline.runner import PipelineRunner
from signalhub.core.pipeline.stages import (
    DeduplicatorStage,
    RuleAndScoreStage,
    SignalNormalizerStage,
    SignalValidatorStage,
)
from signalhub.notifications import TelegramNotificationAdapter
from signalhub.scoring import ScoreEngine
from signalhub.security.policy import SecurityPolicy
from signalhub.validation import SignalValidator


def _valid_signal(**kwargs) -> Signal:
    base = dict(
        id=EntityId("t:1"),
        provider="manual",
        title="Preciso de advogado",
        source="reddit",
        summary="pedido de ajuda",
        url="https://example.com/x",
        provenance=Provenance(provider_id="manual", source_url="https://example.com/x"),
        status=SignalStatus.DISCOVERED,
        version="1",
        contract_version=SIGNAL_CONTRACT_VERSION,
    )
    base.update(kwargs)
    return Signal(**base)


def test_contract_version_constant():
    assert SIGNAL_CONTRACT_VERSION == "1.0.0"


def test_validator_rejects_bad_url():
    v = SignalValidator()
    bad = _valid_signal(url="ftp://nope")
    assert not v.validate(bad).ok


def test_validator_accepts_discovered():
    v = SignalValidator()
    assert v.validate(_valid_signal()).ok


def test_pipeline_order_validator_normalizer():
    ctx = PipelineContext(capability_id="t", signals=[_valid_signal()])
    out = PipelineRunner(
        [SignalValidatorStage(), SignalNormalizerStage(), DeduplicatorStage()]
    ).run(ctx)
    assert len(out.signals) == 1
    assert out.signals[0].status == SignalStatus.DEDUPLICATED
    stages = [h.stage for h in out.signals[0].history]
    assert stages.index("signal_validator") < stages.index("signal_normalizer")
    assert stages.index("signal_normalizer") < stages.index("deduplicator")


def test_validator_rejects_missing_provider():
    ctx = PipelineContext(
        capability_id="t",
        signals=[_valid_signal(provider="")],
    )
    out = PipelineRunner([SignalValidatorStage()]).run(ctx)
    assert out.signals == []
    assert out.attributes.get("validator_rejected") == 1


def test_canonical_to_dict_fields():
    s = _valid_signal()
    d = s.to_dict()
    for key in (
        "id",
        "provider",
        "source",
        "category",
        "title",
        "summary",
        "url",
        "occurred_at",
        "collected_at",
        "score",
        "priority",
        "confidence",
        "rules_applied",
        "history",
        "metadata",
        "provenance",
        "status",
        "version",
        "contract_version",
    ):
        assert key in d


def test_analyze_signal_rfc_explanations():
    orch = build_orchestrator()
    result = orch.execute_capability(
        "analyze_signal",
        {
            "title": "voo cancelado — preciso de ajuda",
            "summary": "reclamação",
            "source": "reddit",
            "url": "https://reddit.com/r/x/1",
        },
    )
    assert result.status == "ok"
    item = result.items[0]
    assert item["contract_version"] == "1.0.0"
    assert item["provider"] == "manual"
    assert item["score"] is not None
    assert any("keyword:" in r or "origem:" in r or "recência:" in r for r in item["rules_applied"])
    assert item["status"] in ("scored", "consumed", "classified", "normalized")


def test_telegram_shows_rules_checkmarks():
    scored = ScoreEngine().score(_valid_signal(title="voo cancelado preciso de ajuda"))
    note = TelegramNotificationAdapter(min_score=0.0).from_signal(scored)
    assert note is not None
    text = note.format_text()
    assert "✔" in text
    assert "Regras:" in text
    assert "Prioridade:" in text


def test_discover_signals_empty():
    r = build_orchestrator().execute_capability("discover_signals", {"terms": ["x"]})
    assert r.status == "ok_vazio"
    assert r.meta.get("ai") is False


def test_mcp_canonical_only():
    server = McpServer()
    listed = server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    names = {t["name"] for t in listed["result"]["tools"]}
    assert "discover_signals" in names
    called = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "analyze_signal",
                "arguments": {
                    "title": "advogado",
                    "url": "https://example.com/a",
                    "source": "reddit",
                },
            },
        }
    )
    payload = json.loads(called["result"]["content"][0]["text"])
    assert "provider" in payload["items"][0]
    assert "metadata" in payload["items"][0]


def test_policy_blocks():
    orch = build_orchestrator(
        policy=SecurityPolicy(disabled_capabilities={"discover_signals"})
    )
    assert orch.execute_capability("discover_signals", {"terms": ["x"]}).status == "blocked_policy"


def test_admin_snapshot_identity():
    from signalhub.admin_snapshot import build_admin_snapshot

    snap = build_admin_snapshot(build_container())
    assert snap["identity"]["primary_object"] == "Signal"
    assert snap["feature_flags"]["ai_in_core"] is False


def test_provider_normalize_rfc():
    from signalhub.core.contracts.provider import RawHit
    from signalhub.providers.google.provider import GoogleProvider

    signals = GoogleProvider().normalize(
        [RawHit(external_id="1", title="t", url="https://ex.com", raw={"html": "<b>"})]
    )
    assert signals[0].provider == "google"
    assert "html" in signals[0].metadata
    assert signals[0].status.value == "discovered" or str(signals[0].status) == "discovered"
    assert "html" in signals[0].to_dict()["metadata"]
