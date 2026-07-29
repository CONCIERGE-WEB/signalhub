"""Back-compat — quality_gate is the canonical module."""

from scout_kiryano.quality_gate import (  # noqa: F401
    bio_ok,
    evaluate,
    family_privacy_violation,
    is_b2b_noise,
    quality_gate,
    relevance_score,
)
