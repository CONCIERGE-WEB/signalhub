"""Unit tests — Prospecção | Tiago A. Rocha (categorias + quality gate)."""

from __future__ import annotations

import sys
from pathlib import Path

PLUGINS = Path(__file__).resolve().parents[2]
if str(PLUGINS) not in sys.path:
    sys.path.insert(0, str(PLUGINS))

from scout_kiryano.adapter import profile_to_raw_hit  # noqa: E402
from scout_kiryano.categories import (  # noqa: E402
    CATEGORIAS_OFICIAIS,
    classify_intent,
    canonical_categoria,
)
from scout_kiryano.quality_gate import evaluate  # noqa: E402


def test_nine_official_categories():
    assert len(CATEGORIAS_OFICIAIS) == 9
    assert canonical_categoria("plano_saude") == "plano_seguro_negativa"
    assert canonical_categoria("divorcio_uniao") == "divorcio"
    assert canonical_categoria("produto_defeito") == "produto_defeito_atraso"


def test_classify_voo_and_fraude():
    cat, kw = classify_intent("Meu voo cancelado pela LATAM e mala extraviada")
    assert cat == "voo_bagagem"
    assert kw
    cat2, _ = classify_intent("Cai no golpe do pix e cartão clonado")
    assert cat2 == "fraude_bancaria"


def test_reject_empty():
    gate = evaluate(None)
    assert gate["status"] == "rejected_empty"
    assert profile_to_raw_hit(None) is None


def test_reject_b2b_github_and_advogado():
    profile = {
        "username": "lima-advogados",
        "full_name": "Lima Advogados Associados",
        "bio": "Escritório de advocacia OAB — direito do consumidor",
        "email": "contato@limaadvos.com.br",
        "phone": "",
        "website": "https://limaadvos.com.br/",
        "platform": "github",
        "profile_url": "https://github.com/lima-advogados",
        "follower_count": 2,
    }
    gate = evaluate(profile)
    assert gate["status"] == "rejected_b2b"
    assert profile_to_raw_hit(profile) is None


def test_reject_family_privacy_menor():
    profile = {
        "username": "mae_xyz",
        "full_name": "Maria",
        "bio": "Preciso de revisão de pensão. Meu filho João Pedro Silva está com 8 anos.",
        "email": "maria@exemplo-consumidor.com",
        "phone": "",
        "website": "https://exemplo-consumidor.com/contato",
        "platform": "youtube",
        "profile_url": "https://www.youtube.com/@mae_xyz",
        "follower_count": 100,
    }
    gate = evaluate(profile)
    assert gate["status"] == "rejected_privacy"
    assert gate["categoria_id"] == "pensao_alimenticia"


def test_accept_b2c_voo_youtube():
    profile = {
        "username": "passageiro_cdc",
        "full_name": "Relato passageiro",
        "bio": "Voo cancelado e mala extraviada na LATAM — sem reembolso.",
        "email": "",
        "phone": "",
        "website": "https://meusite-consumidor.example/reclame",
        "platform": "youtube",
        "profile_url": "https://www.youtube.com/@passageiro_cdc",
        "follower_count": 200,
    }
    gate = evaluate(profile)
    assert gate["status"] == "accepted"
    assert gate["categoria_id"] == "voo_bagagem"
    hit = profile_to_raw_hit(profile)
    assert hit is not None
    assert hit.category == "voo_bagagem"
    assert hit.raw["email"] == ""
    assert hit.raw["categoria_label"] == "Voo e Bagagem"


def test_reject_no_category():
    profile = {
        "username": "hobby",
        "full_name": "Hobby Channel",
        "bio": "Receitas de bolo e jardinagem no fim de semana.",
        "email": "hobby@site.example",
        "website": "https://site.example",
        "platform": "youtube",
        "profile_url": "https://www.youtube.com/@hobby",
        "follower_count": 50,
    }
    gate = evaluate(profile)
    assert gate["status"] == "rejected_no_category"


def test_provider_idle_without_live(monkeypatch):
    from scout_kiryano.provider import ScoutKiryanoProvider
    from signalhub.core.contracts.provider import ProviderQuery

    monkeypatch.delenv("SIGNALHUB_SCOUT_KIRYANO_LIVE", raising=False)
    p = ScoutKiryanoProvider()
    assert "Prospecção" in p.provider_name
    hits = p.search(ProviderQuery(capability_id="discover_signals", terms=["x"]))
    assert hits == ()
