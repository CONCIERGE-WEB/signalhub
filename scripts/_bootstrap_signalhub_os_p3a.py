"""Bootstrap phase 3 — security, observability, ai, providers, capabilities, apps."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "signalhub"


def w(rel: str, content: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")


FILES: dict[str, str] = {
    "security/__init__.py": '''\
from .policy import RateLimit, SecurityPolicy

__all__ = ["RateLimit", "SecurityPolicy"]
''',
    "security/policy.py": '''\
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(slots=True, frozen=True)
class RateLimit:
    requests_per_minute: int = 30
    burst: int = 5


@dataclass
class SecurityPolicy:
    """Operator-controlled gates — disable providers, rate-limit, audit."""

    enabled_providers: set[str] | None = None  # None = all registered
    disabled_providers: set[str] = field(default_factory=set)
    enabled_capabilities: set[str] | None = None
    disabled_capabilities: set[str] = field(default_factory=set)
    rate_limits: Mapping[str, RateLimit] = field(default_factory=dict)
    require_public_source: bool = True
    human_in_the_loop: bool = True

    def is_provider_allowed(self, provider_id: str) -> bool:
        pid = provider_id.strip().lower()
        if pid in {d.lower() for d in self.disabled_providers}:
            return False
        if self.enabled_providers is None:
            return True
        return pid in {e.lower() for e in self.enabled_providers}

    def is_capability_allowed(self, capability_id: str) -> bool:
        cid = capability_id.strip().lower()
        if cid in {d.lower() for d in self.disabled_capabilities}:
            return False
        if self.enabled_capabilities is None:
            return True
        return cid in {e.lower() for e in self.enabled_capabilities}

    def rate_limit_for(self, provider_id: str) -> RateLimit:
        return self.rate_limits.get(provider_id, RateLimit())
''',
    "observability/__init__.py": '''\
from .logging import StructuredLogger
from .metrics import InMemoryMetrics
from .tracing import ExecutionTrace, Span

__all__ = ["ExecutionTrace", "InMemoryMetrics", "Span", "StructuredLogger"]
''',
    "observability/logging.py": '''\
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Mapping


class StructuredLogger:
    def __init__(self, name: str = "signalhub") -> None:
        self._log = logging.getLogger(name)

    def info(self, message: str, **fields: Any) -> None:
        self._emit("INFO", message, fields)

    def error(self, message: str, **fields: Any) -> None:
        self._emit("ERROR", message, fields)

    def _emit(self, level: str, message: str, fields: Mapping[str, Any]) -> None:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "message": message,
            **dict(fields),
        }
        line = json.dumps(payload, ensure_ascii=False, default=str)
        if level == "ERROR":
            self._log.error(line)
        else:
            self._log.info(line)
''',
    "observability/metrics.py": '''\
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class InMemoryMetrics:
    counters: dict[str, float] = field(default_factory=lambda: defaultdict(float))
    timings_ms: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list))

    def incr(self, name: str, value: float = 1.0) -> None:
        self.counters[name] += value

    def timing(self, name: str, ms: float) -> None:
        self.timings_ms[name].append(ms)
'''
,
    "observability/tracing.py": '''\
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass
class Span:
    name: str
    started_at: float = field(default_factory=time.perf_counter)
    ended_at: float | None = None
    status: str = "running"
    detail: str = ""

    def ok(self) -> None:
        self.ended_at = time.perf_counter()
        self.status = "ok"

    def fail(self, detail: str) -> None:
        self.ended_at = time.perf_counter()
        self.status = "error"
        self.detail = detail

    @property
    def duration_ms(self) -> float | None:
        if self.ended_at is None:
            return None
        return (self.ended_at - self.started_at) * 1000.0


@dataclass
class ExecutionTrace:
    operation: str
    trace_id: str = field(default_factory=lambda: str(uuid4()))
    spans: list[Span] = field(default_factory=list)
    _started: float = field(default_factory=time.perf_counter)
    _ended: float | None = None
    meta: dict[str, Any] = field(default_factory=dict)

    def start_span(self, name: str) -> Span:
        span = Span(name=name)
        self.spans.append(span)
        return span

    def __enter__(self) -> ExecutionTrace:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        self._ended = time.perf_counter()
        return None

    @property
    def duration_ms(self) -> float | None:
        end = self._ended if self._ended is not None else time.perf_counter()
        return (end - self._started) * 1000.0
''',
    "ai/__init__.py": '''\
"""AI adapters — Providers never import LLM clients directly."""
from .null import NullAI

__all__ = ["NullAI"]
''',
    "ai/null.py": '''\
from __future__ import annotations

from typing import Any, Mapping, Sequence

from signalhub.core.contracts.ai import (
    ClassificationPort,
    EmbeddingsPort,
    LLMPort,
    ProposalGeneratorPort,
    RerankingPort,
    ReportGeneratorPort,
    SummariesPort,
)


class NullAI(
    LLMPort,
    EmbeddingsPort,
    RerankingPort,
    SummariesPort,
    ClassificationPort,
    ProposalGeneratorPort,
    ReportGeneratorPort,
):
    """Explicit empty AI — no invented completions."""

    def complete(self, prompt: str, *, options: Mapping[str, Any] | None = None) -> str:
        _ = (prompt, options)
        return ""

    def embed(self, texts: Sequence[str]) -> Sequence[Sequence[float]]:
        return [() for _ in texts]

    def rerank(self, query: str, documents: Sequence[str]) -> Sequence[int]:
        _ = query
        return list(range(len(documents)))

    def summarize(self, text: str, *, options: Mapping[str, Any] | None = None) -> str:
        _ = (text, options)
        return ""

    def classify(self, text: str, labels: Sequence[str]) -> Mapping[str, float]:
        _ = text
        return {label: 0.0 for label in labels}

    def generate(self, context: Mapping[str, Any]) -> Any:
        _ = context
        return "" if not isinstance(self, ReportGeneratorPort) else {"status": "ai_null", "content": ""}
'''
,
    "providers/__init__.py": '''\
"""Providers — each implements Provider; none knows another."""
from signalhub.providers.base import BaseProvider
from signalhub.providers.dorking.provider import DorkingProvider
from signalhub.providers.scout.provider import ScoutProvider

__all__ = ["BaseProvider", "DorkingProvider", "ScoutProvider"]
''',
    "providers/base.py": '''\
from __future__ import annotations

from typing import Sequence

from signalhub.core.contracts.provider import (
    HealthStatus,
    Provider,
    ProviderMetadata,
    ProviderQuery,
    RawHit,
)
from signalhub.core.models import Lead, Provenance
from signalhub.core.models.common import EntityId, GeoHint, VerticalId
from signalhub.core.models.lead import LeadStatus


class BaseProvider(Provider):
    """Shared helpers — subclasses still must implement search/metadata."""

    provider_id: str = "base"
    provider_name: str = "Base"
    version: str = "0.1.0"
    capability_ids: tuple[str, ...] = ()

    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            provider_id=self.provider_id,
            name=self.provider_name,
            version=self.version,
            capabilities=self.capability_ids,
            description=getattr(self, "description", ""),
            enabled_by_default=False,
        )

    def healthcheck(self) -> HealthStatus:
        return HealthStatus(ok=True, provider_id=self.provider_id, detail="scaffold")

    def collect(self, hits: Sequence[RawHit]) -> Sequence[RawHit]:
        return list(hits)

    def normalize(self, hits: Sequence[RawHit]) -> Sequence[Lead]:
        leads: list[Lead] = []
        for hit in hits:
            prov = hit.provenance or Provenance(
                provider_id=self.provider_id,
                source_url=hit.url,
            )
            leads.append(
                Lead(
                    id=EntityId(f"{self.provider_id}:{hit.external_id}"),
                    title=hit.title,
                    url=hit.url,
                    snippet=hit.snippet,
                    status=LeadStatus.CANDIDATE,
                    provenance=(prov,),
                    attributes=dict(hit.raw),
                )
            )
        return leads

    def validate(self, leads: Sequence[Lead]) -> Sequence[Lead]:
        return [L for L in leads if (L.url or L.id)]

    def enrich(self, leads: Sequence[Lead]) -> Sequence[Lead]:
        return list(leads)

    def search(self, query: ProviderQuery) -> Sequence[RawHit]:
        _ = query
        return ()
'''
,
    "providers/scout/__init__.py": "from .provider import ScoutProvider\n\n__all__ = [\"ScoutProvider\"]\n",
    "providers/scout/provider.py": '''\
from __future__ import annotations

from typing import Sequence

from signalhub.core.contracts.provider import ProviderQuery, RawHit
from signalhub.providers.base import BaseProvider


class ScoutProvider(BaseProvider):
    """Scout channel — P1 will plug real discovery; today returns empty explicit."""

    provider_id = "scout"
    provider_name = "Scout"
    description = "Lead discovery via Scout (scaffold — no invented leads)."
    capability_ids = ("discover_leads", "search_companies")

    def search(self, query: ProviderQuery) -> Sequence[RawHit]:
        _ = query
        return ()
'''
,
    "providers/dorking/__init__.py": "from .provider import DorkingProvider\n\n__all__ = [\"DorkingProvider\"]\n",
    "providers/dorking/provider.py": '''\
"""Dork Engine as specialized Provider.

Locates public references and public signals only, respecting operator config,
platform terms, and applicable law. Returns canonical RawHit/Lead for enrichment.
Does NOT know other providers. Does NOT call LLMs.
"""
from __future__ import annotations

from typing import Sequence

from signalhub.core.contracts.provider import HealthStatus, ProviderQuery, RawHit
from signalhub.providers.base import BaseProvider


class DorkingProvider(BaseProvider):
    provider_id = "dorking"
    provider_name = "Dork Engine"
    description = (
        "Specialized provider for public-reference discovery under operator "
        "controls, rate limits and compliance gates."
    )
    capability_ids = (
        "discover_leads",
        "discover_social_signals",
        "search_documents",
    )

    def healthcheck(self) -> HealthStatus:
        return HealthStatus(
            ok=True,
            provider_id=self.provider_id,
            detail="scaffold_ready — engine not wired (empty explicit)",
        )

    def search(self, query: ProviderQuery) -> Sequence[RawHit]:
        # Real dork execution is operator-gated and lives behind this contract.
        # Until wired: empty explicit (never invent hits).
        _ = query
        return ()
'''
,
    "providers/google/__init__.py": "from .provider import GoogleProvider\n\n__all__ = [\"GoogleProvider\"]\n",
    "providers/google/provider.py": '''\
from __future__ import annotations

from typing import Sequence

from signalhub.core.contracts.provider import ProviderQuery, RawHit
from signalhub.providers.base import BaseProvider


class GoogleProvider(BaseProvider):
    provider_id = "google"
    provider_name = "Google"
    description = "Public web discovery stub — respects ToS when implemented."
    capability_ids = ("discover_leads", "search_companies", "analyze_website")

    def search(self, query: ProviderQuery) -> Sequence[RawHit]:
        _ = query
        return ()
'''
,
    "providers/websites/__init__.py": "from .provider import WebsitesProvider\n\n__all__ = [\"WebsitesProvider\"]\n",
    "providers/websites/provider.py": '''\
from __future__ import annotations

from typing import Sequence

from signalhub.core.contracts.provider import ProviderQuery, RawHit
from signalhub.providers.base import BaseProvider


class WebsitesProvider(BaseProvider):
    provider_id = "websites"
    provider_name = "Websites"
    description = "Website analysis stub — public pages only."
    capability_ids = ("analyze_website", "detect_stack", "company_enrichment")

    def search(self, query: ProviderQuery) -> Sequence[RawHit]:
        _ = query
        return ()
'''
,
    "providers/linkedin/__init__.py": "from .provider import LinkedInProvider\n\n__all__ = [\"LinkedInProvider\"]\n",
    "providers/linkedin/provider.py": '''\
from __future__ import annotations

from typing import Sequence

from signalhub.core.contracts.provider import ProviderQuery, RawHit
from signalhub.providers.base import BaseProvider


class LinkedInProvider(BaseProvider):
    provider_id = "linkedin"
    provider_name = "LinkedIn"
    description = "Public professional signals stub — ToS-gated when implemented."
    capability_ids = ("discover_social_signals", "search_companies")

    def search(self, query: ProviderQuery) -> Sequence[RawHit]:
        _ = query
        return ()
'''
,
    "providers/github/__init__.py": "from .provider import GitHubProvider\n\n__all__ = [\"GitHubProvider\"]\n",
    "providers/github/provider.py": '''\
from __future__ import annotations

from typing import Sequence

from signalhub.core.contracts.provider import ProviderQuery, RawHit
from signalhub.providers.base import BaseProvider


class GitHubProvider(BaseProvider):
    provider_id = "github"
    provider_name = "GitHub"
    description = "Public repo / org signals stub."
    capability_ids = ("detect_stack", "search_companies", "tech_stack_detection")

    def search(self, query: ProviderQuery) -> Sequence[RawHit]:
        _ = query
        return ()
'''
,
    "providers/telegram/__init__.py": "from .provider import TelegramProvider\n\n__all__ = [\"TelegramProvider\"]\n",
    "providers/telegram/provider.py": '''\
from __future__ import annotations

from typing import Sequence

from signalhub.core.contracts.provider import ProviderQuery, RawHit
from signalhub.providers.base import BaseProvider


class TelegramProvider(BaseProvider):
    """Alert sink oriented — not Lex CDC. Ops/commercial bot only when configured."""

    provider_id = "telegram"
    provider_name = "Telegram"
    description = "Notification channel stub (human-in-the-loop)."
    capability_ids = ("crm_automation",)

    def search(self, query: ProviderQuery) -> Sequence[RawHit]:
        _ = query
        return ()
'''
,
}

def main() -> None:
    for rel, content in FILES.items():
        w(rel, content)
    print(f"phase3a: {len(FILES)} files")


if __name__ == "__main__":
    main()
