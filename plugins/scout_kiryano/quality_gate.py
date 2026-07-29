"""
Quality gate — Prospecção | Tiago A. Rocha (scout_kiryano).

BrandBook: zero dados fictícios.
- Contato mínimo auditado
- 9 categorias oficiais B2C
- Banimento B2B (advogado/escritório/OAB/github/dev…)
- Família: descartar menção a nomes de menores / dados sensíveis
"""

from __future__ import annotations

import re
from typing import Any, Mapping

from scout_kiryano.categories import (
    FAMILIA_CATEGORIAS,
    classify_profile,
    label_categoria,
)

_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
_EMAIL_BLACKLIST = (
    "example.com",
    "test.com",
    "email.com",
    "youremail.com",
    "sentry.io",
    "noreply",
    "no-reply",
)

# Banimento B2B / ruído técnico — B2C consumidor apenas.
_B2B_TERMS: tuple[str, ...] = (
    "advogado",
    "advogada",
    "advocacia",
    "escritorio",
    "escritório",
    " oab",
    "oab/",
    "oab ",
    "github",
    "repositorio",
    "repositório",
    "repository",
    " codigo",
    " código",
    "codigo-fonte",
    "dev ",
    " developer",
    "fullstack",
    "full-stack",
    "software engineer",
    "lima advogados",
    "associados advocacia",
)

# Heurística conservadora: menor identificado por nome completo + contexto familiar.
_MENOR_SENSIVEL = re.compile(
    r"(?i)\b("
    r"meu filho|minha filha|filho menor|filha menor|"
    r"menor de idade|crianca de|criança de|"
    r"meu neto|minha neta"
    r")\b.{0,40}\b([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+){1,3})\b"
)

_CPF_EXPOSTO = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")


def _valid_email(value: str) -> bool:
    email = (value or "").strip().lower()
    if not email or not _EMAIL_RE.match(email):
        return False
    return not any(b in email for b in _EMAIL_BLACKLIST)


def _valid_phone(value: str) -> bool:
    digits = re.sub(r"\D", "", value or "")
    return len(digits) >= 10


def _blob(profile: Mapping[str, Any]) -> str:
    parts = [
        str(profile.get("bio") or ""),
        str(profile.get("full_name") or ""),
        str(profile.get("username") or ""),
        str(profile.get("company") or ""),
        str(profile.get("website") or ""),
        str(profile.get("platform") or ""),
        str(profile.get("profile_url") or ""),
        str(profile.get("snippet") or ""),
    ]
    return " ".join(parts).lower()


def is_b2b_noise(profile: Mapping[str, Any]) -> tuple[bool, list[str]]:
    """Descarta perfil/texto B2B (advocacia, OAB, github, dev…)."""
    blob = _blob(profile)
    platform = str(profile.get("platform") or "").lower()
    hits: list[str] = []
    if platform == "github":
        hits.append("platform:github")
    for term in _B2B_TERMS:
        if term.lower() in blob:
            hits.append(term.strip())
    # dedupe preserving order
    seen: set[str] = set()
    uniq = []
    for h in hits:
        if h not in seen:
            seen.add(h)
            uniq.append(h)
    return bool(uniq), uniq


def family_privacy_violation(text: str, categoria_id: str | None) -> tuple[bool, list[str]]:
    """Para Família: bloquear nomes de menores / CPF exposto em texto público."""
    if not categoria_id or categoria_id not in FAMILIA_CATEGORIAS:
        return False, []
    reasons: list[str] = []
    if _MENOR_SENSIVEL.search(text or ""):
        reasons.append("menor_nome_exposto")
    if _CPF_EXPOSTO.search(text or ""):
        reasons.append("cpf_exposto")
    return bool(reasons), reasons


def relevance_score(profile: Mapping[str, Any]) -> int:
    """0–100 from real public fields only. Never invents missing data."""
    score = 0
    if (profile.get("profile_url") or "").strip():
        score += 20
    if (profile.get("full_name") or "").strip():
        score += 10
    bio = (profile.get("bio") or "").strip()
    if len(bio) >= 20:
        score += 15
    elif bio:
        score += 5
    if _valid_email(str(profile.get("email") or "")):
        score += 30
    if _valid_phone(str(profile.get("phone") or "")):
        score += 20
    website = (profile.get("website") or "").strip()
    if website.startswith("http"):
        score += 15
    followers = int(profile.get("follower_count") or 0)
    if followers >= 1000:
        score += 10
    elif followers >= 100:
        score += 5
    socials = profile.get("socials") or {}
    if isinstance(socials, dict) and socials:
        score += min(10, 2 * len(socials))
    cat, kw = classify_profile(profile)
    if cat and kw:
        score += min(20, 5 * len(kw))
    return min(100, score)


def bio_ok(profile: Mapping[str, Any]) -> bool:
    return len(str(profile.get("bio") or "").strip()) >= 20


def evaluate(profile: Mapping[str, Any] | None) -> dict[str, Any]:
    """
    status:
      accepted | rejected_incomplete | rejected_empty |
      rejected_b2b | rejected_privacy | rejected_no_category
    """
    if not profile:
        return {
            "status": "rejected_empty",
            "score": 0,
            "contact_ok": False,
            "categoria_id": None,
            "categoria_label": None,
            "matched_keywords": [],
            "reasons": ["no_profile"],
            "profile": None,
        }

    b2b, b2b_hits = is_b2b_noise(profile)
    if b2b:
        return {
            "status": "rejected_b2b",
            "score": 0,
            "contact_ok": False,
            "categoria_id": None,
            "categoria_label": None,
            "matched_keywords": [],
            "reasons": ["b2b_noise", *b2b_hits[:6]],
            "profile": dict(profile),
        }

    cat_id, matched = classify_profile(profile)
    blob = " ".join(
        [
            str(profile.get("bio") or ""),
            str(profile.get("full_name") or ""),
            str(profile.get("snippet") or ""),
        ]
    )
    privacy_hit, privacy_reasons = family_privacy_violation(blob, cat_id)
    if privacy_hit:
        return {
            "status": "rejected_privacy",
            "score": 0,
            "contact_ok": False,
            "categoria_id": cat_id,
            "categoria_label": label_categoria(cat_id),
            "matched_keywords": matched,
            "reasons": privacy_reasons,
            "profile": dict(profile),
        }

    email = str(profile.get("email") or "").strip()
    phone = str(profile.get("phone") or "").strip()
    website = str(profile.get("website") or "").strip()
    url = str(profile.get("profile_url") or "").strip()

    contact_ok = (
        _valid_email(email)
        or _valid_phone(phone)
        or (website.startswith("http") and len(website) > 8)
    )
    score = relevance_score(profile)
    reasons: list[str] = []

    if not cat_id:
        reasons.append("no_official_category")
    if not url:
        reasons.append("missing_profile_url")
    if not contact_ok:
        reasons.append("missing_valid_contact")
    if score < 25:
        reasons.append("low_relevance_score")

    if not cat_id:
        status = "rejected_no_category"
    elif contact_ok and score >= 25 and url and cat_id:
        status = "accepted"
        reasons = ["ok"]
    elif not contact_ok and score >= 40 and url and cat_id and (
        profile.get("full_name") or bio_ok(profile)
    ):
        reasons.append("public_profile_without_contact")
        status = "rejected_incomplete"
    else:
        status = "rejected_incomplete"

    enriched = dict(profile)
    enriched["categoria_id"] = cat_id
    enriched["categoria_label"] = label_categoria(cat_id) if cat_id else None
    enriched["matched_keywords"] = matched

    return {
        "status": status,
        "score": score,
        "contact_ok": contact_ok,
        "categoria_id": cat_id,
        "categoria_label": label_categoria(cat_id) if cat_id else None,
        "matched_keywords": matched,
        "reasons": reasons,
        "profile": enriched,
    }


# Back-compat alias requested by ops brief.
quality_gate = evaluate
