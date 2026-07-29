"""
9 categorias oficiais B2C — alinhadas ao formulário Lex Rocha (pipeline).

IDs canônicos = src/lib/pipeline-confiavel/categorias.ts (CATEGORIAS_COM_BANCO_MVP).
Aliases de copy (plano_saude, divorcio_uniao, …) resolvem para o ID oficial.
"""

from __future__ import annotations

from typing import Mapping

# Ordem oficial do formulário (Consumo 1–6 + Família 7–9).
CATEGORIAS_OFICIAIS: tuple[str, ...] = (
    "voo_bagagem",
    "negativacao_indevida",
    "cobranca_indevida",
    "fraude_bancaria",
    "plano_seguro_negativa",
    "produto_defeito_atraso",
    "pensao_alimenticia",
    "guarda_filhos",
    "divorcio",
)

CATEGORIA_LABELS: dict[str, str] = {
    "voo_bagagem": "Voo e Bagagem",
    "negativacao_indevida": "Negativação Indevida",
    "cobranca_indevida": "Cobrança Indevida",
    "fraude_bancaria": "Fraudes Bancárias e Golpes",
    "plano_seguro_negativa": "Plano de Saúde",
    "produto_defeito_atraso": "Produto com Defeito",
    "pensao_alimenticia": "Pensão Alimentícia",
    "guarda_filhos": "Guarda e Convivência",
    "divorcio": "Divórcio e União Estável",
}

CATEGORIA_ALIASES: dict[str, str] = {
    "plano_saude": "plano_seguro_negativa",
    "produto_defeito": "produto_defeito_atraso",
    "divorcio_uniao": "divorcio",
    "fraude_conta_digital": "fraude_bancaria",
}

FAMILIA_CATEGORIAS: frozenset[str] = frozenset(
    {"pensao_alimenticia", "guarda_filhos", "divorcio"}
)

# Dicionário de intenção de dor (saída = ID canônico).
INTENT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "voo_bagagem": (
        "voo cancelado",
        "atraso voo",
        "atraso de voo",
        "mala extraviada",
        "bagagem extraviada",
        "overbooking",
        "latam",
        "gol linhas",
        "azul linhas",
        "companhia aerea",
        "companhia aérea",
        "voo atrasado",
    ),
    "negativacao_indevida": (
        "nome spc",
        "nome serasa",
        "negativado sem dever",
        "inclusao indevida",
        "inclusão indevida",
        "negativacao indevida",
        "negativação indevida",
        "spc serasa",
    ),
    "cobranca_indevida": (
        "cobranca que nao reconheco",
        "cobrança que não reconheço",
        "cobrando apos cancelar",
        "cobrando após cancelar",
        "fatura indevida",
        "cobranca indevida",
        "cobrança indevida",
    ),
    "fraude_bancaria": (
        "golpe do pix",
        "cartao clonado",
        "cartão clonado",
        "invasao de conta",
        "invasão de conta",
        "falso funcionario",
        "falso funcionário",
        "falso whatsapp",
        "golpe pix",
        "fraude bancaria",
        "fraude bancária",
    ),
    "plano_seguro_negativa": (
        "negativa de cobertura",
        "demora procedimento",
        "negativa cirurgia",
        "reajuste abusivo",
        "plano de saude",
        "plano de saúde",
        "negativa plano",
    ),
    "produto_defeito_atraso": (
        "produto com defeito",
        "vicio oculto",
        "vício oculto",
        "atraso na entrega",
        "reembolso negado",
        "produto nao entregue",
        "produto não entregue",
    ),
    "pensao_alimenticia": (
        "revisao de pensao",
        "revisão de pensão",
        "exoneracao pensao",
        "exoneração pensão",
        "nao pagou pensao",
        "não pagou pensão",
        "pensao alimenticia",
        "pensão alimentícia",
    ),
    "guarda_filhos": (
        "guarda compartilhada",
        "alienacao parental",
        "alienação parental",
        "regulamentacao de visitas",
        "regulamentação de visitas",
        "guarda de filhos",
        "convivencia filhos",
        "convivência filhos",
    ),
    "divorcio": (
        "partilha de bens",
        "dissolucao de uniao estavel",
        "dissolução de união estável",
        "divorcio litigioso",
        "divórcio litigioso",
        "divorcio",
        "divórcio",
        "uniao estavel",
        "união estável",
    ),
}


def canonical_categoria(value: str | None) -> str | None:
    raw = (value or "").strip().lower()
    if not raw:
        return None
    aliased = CATEGORIA_ALIASES.get(raw, raw)
    return aliased if aliased in CATEGORIA_LABELS else None


def label_categoria(categoria_id: str | None) -> str:
    cid = canonical_categoria(categoria_id) or (categoria_id or "")
    return CATEGORIA_LABELS.get(cid, cid or "—")


def classify_intent(text: str) -> tuple[str | None, list[str]]:
    """
    Classifica texto público nas 9 categorias.
    Retorna (categoria_id|None, matched_keywords). Sem inventar categoria.
    """
    blob = _normalize(text)
    if not blob:
        return None, []
    best_id: str | None = None
    best_hits: list[str] = []
    for cat_id, keywords in INTENT_KEYWORDS.items():
        hits = [kw for kw in keywords if _normalize(kw) in blob]
        if len(hits) > len(best_hits):
            best_id = cat_id
            best_hits = hits
    return best_id, best_hits


def classify_profile(profile: Mapping[str, object]) -> tuple[str | None, list[str]]:
    parts = [
        str(profile.get("bio") or ""),
        str(profile.get("full_name") or ""),
        str(profile.get("title") or ""),
        str(profile.get("snippet") or ""),
        " ".join(str(x) for x in (profile.get("links") or []) if isinstance(x, str)),
    ]
    return classify_intent(" ".join(parts))


def _normalize(text: str) -> str:
    t = (text or "").lower()
    repl = (
        ("á", "a"),
        ("à", "a"),
        ("ã", "a"),
        ("â", "a"),
        ("é", "e"),
        ("ê", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ô", "o"),
        ("õ", "o"),
        ("ú", "u"),
        ("ç", "c"),
    )
    for a, b in repl:
        t = t.replace(a, b)
    return t
