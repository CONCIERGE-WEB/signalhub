"""Canonical domain models — Signal is primary (RFC-0001); Lead is an interpretation."""
from .common import EntityId, GeoHint, VerticalId
from .company import Company
from .lead import Lead, LeadStatus
from .provenance import Provenance
from .signal import (
    SIGNAL_CONTRACT_VERSION,
    KNOWN_CATEGORIES,
    ProcessingStep,
    PublicSignal,
    ScoreBreakdown,
    Signal,
    SignalPriority,
    SignalStatus,
    SignalType,
)

__all__ = [
    "KNOWN_CATEGORIES",
    "SIGNAL_CONTRACT_VERSION",
    "Company",
    "EntityId",
    "GeoHint",
    "Lead",
    "LeadStatus",
    "ProcessingStep",
    "Provenance",
    "PublicSignal",
    "ScoreBreakdown",
    "Signal",
    "SignalPriority",
    "SignalStatus",
    "SignalType",
    "VerticalId",
]
