"""Signal Validator — RFC-0001 gate. No invalid Signal enters the Core pipeline."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

from signalhub.core.models.signal import (
    KNOWN_CATEGORIES,
    SIGNAL_CONTRACT_VERSION,
    Signal,
    SignalPriority,
    SignalStatus,
)


@dataclass(slots=True, frozen=True)
class ValidationIssue:
    field: str
    message: str


@dataclass(slots=True, frozen=True)
class ValidationResult:
    ok: bool
    issues: tuple[ValidationIssue, ...] = ()

    @property
    def reasons(self) -> list[str]:
        return [f"{i.field}: {i.message}" for i in self.issues]


class SignalValidator:
    """Ensures Providers (including future third parties) cannot inject invalid Signals."""

    SUPPORTED_CONTRACTS = frozenset({SIGNAL_CONTRACT_VERSION, "1.0.0"})

    def validate(self, signal: Signal) -> ValidationResult:
        issues: list[ValidationIssue] = []

        if not str(signal.id or "").strip():
            issues.append(ValidationIssue("id", "obrigatório"))
        if not (signal.provider or "").strip():
            issues.append(ValidationIssue("provider", "obrigatório"))
        if not (signal.title or "").strip():
            issues.append(ValidationIssue("title", "obrigatório / não vazio"))
        if signal.source is None:
            issues.append(ValidationIssue("source", "obrigatório"))

        if signal.url:
            parsed = urlparse(signal.url)
            if parsed.scheme not in ("http", "https") or not parsed.netloc:
                issues.append(ValidationIssue("url", "deve ser http(s) com host"))

        if signal.occurred_at and signal.collected_at:
            occ = _aware(signal.occurred_at)
            col = _aware(signal.collected_at)
            if occ > col + timedelta(days=1):
                issues.append(
                    ValidationIssue("occurred_at", "não pode ser muito depois de collected_at")
                )

        try:
            if not isinstance(signal.priority, SignalPriority):
                SignalPriority(str(signal.priority))
        except ValueError:
            issues.append(ValidationIssue("priority", "valor não permitido"))

        status = _parse_status(signal.status)
        if status is None:
            issues.append(ValidationIssue("status", "estado desconhecido"))

        if signal.category is not None and signal.category not in KNOWN_CATEGORIES:
            if status in (
                SignalStatus.CLASSIFIED,
                SignalStatus.SCORED,
                SignalStatus.STORED,
                SignalStatus.CONSUMED,
            ):
                issues.append(ValidationIssue("category", f"desconhecida: {signal.category}"))

        if status in (SignalStatus.SCORED, SignalStatus.STORED, SignalStatus.CONSUMED):
            if signal.score is None:
                issues.append(ValidationIssue("score", "obrigatório após scored"))
            elif not (0.0 <= float(signal.score) <= 100.0):
                issues.append(ValidationIssue("score", "deve estar em [0, 100]"))
            if signal.confidence is None:
                issues.append(ValidationIssue("confidence", "obrigatório após scored"))
            elif not (0.0 <= float(signal.confidence) <= 1.0):
                issues.append(ValidationIssue("confidence", "deve estar em [0, 1]"))

        if signal.contract_version not in self.SUPPORTED_CONTRACTS:
            issues.append(
                ValidationIssue(
                    "contract_version",
                    f"incompatível: {signal.contract_version}",
                )
            )

        if not signal.version or not str(signal.version).strip():
            issues.append(ValidationIssue("version", "obrigatório"))

        if signal.provenance is None:
            issues.append(ValidationIssue("provenance", "obrigatório"))
        elif not signal.provenance.provider_id:
            issues.append(ValidationIssue("provenance.provider_id", "obrigatório"))

        return ValidationResult(ok=not issues, issues=tuple(issues))


def _aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _parse_status(status: SignalStatus | str) -> SignalStatus | None:
    if isinstance(status, SignalStatus):
        return status
    try:
        return SignalStatus(str(status))
    except ValueError:
        return None
