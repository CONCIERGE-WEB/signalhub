"""Smoke — contrato Scout scaffold (sem inventar leads)."""
from __future__ import annotations

from engine.providers import ScoutLeadProvider, get_provider
from engine.providers.base import LeadSink, ProviderQuery


def test_scout_run_vazio_explicito():
    p = get_provider("scout")
    assert isinstance(p, ScoutLeadProvider)
    out = p.run(
        ProviderQuery(vertical="legaltech", terms=("advogado",), geo="SP", limit=10),
        sink=LeadSink.POSTGRES,
    )
    assert out["count"] == 0
    assert out["status"] == "ok_vazio"


def test_provider_desconhecido():
    try:
        get_provider("nao_existe")
        assert False, "deveria falhar"
    except KeyError:
        pass
