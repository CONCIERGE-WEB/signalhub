"""Platform hardening surfaces — health + compatibility."""

from signalhub.platform.compatibility import run_contract_suite
from signalhub.platform.health import run_all_health_checks

__all__ = ["run_all_health_checks", "run_contract_suite"]
