"""Isolation and guard tests for the new REAL authority modules.

Proves the new REAL modules stay semantically separate from the accepted PAPER
machinery (no paper imports, no PAPER mutation), carry no secret surface and no
invented credential names/endpoints, embed no permanent numeric risk rules, and
that the accepted PAPER authority behavior remains unchanged.
"""

from __future__ import annotations

from pathlib import Path
import re
import unittest

from src.paper_execution_authority import PaperAuthorityStatus, PaperExecutionAuthority

REPO_ROOT = Path(__file__).resolve().parents[1]

REAL_MODULES = (
    "src/real_execution_authority.py",
    "src/real_activation_profile.py",
    "src/real_runtime_config.py",
    "src/real_preflight.py",
    "src/real_runtime_controller.py",
    "src/real_supervisor.py",
    "src/real_offline_activation_rehearsal.py",
    "src/realtime_provider_control.py",
    "src/realtime_provider_attempt_ledger.py",
)

# Permanent numeric risk-rule identifiers that must never be silently embedded
# in the REAL prebuild modules.
FORBIDDEN_RISK_IDENTIFIERS = (
    "risk_percent",
    "stop_loss_percent",
    "max_drawdown",
    "daily_loss_limit",
    "per_trade_risk",
    "margin_rate",
)

# Anything that would imply an invented credential seam, endpoint or secret.
FORBIDDEN_SECRET_OR_ENDPOINT_IDENTIFIERS = (
    "FANGZHENG",
    "FUT_OPEND",
    "CTP_USER",
    "CTP_PASSWORD",
    "API_KEY",
    "API_SECRET",
    "broker_endpoint",
    "broker_addr",
    "password",
)


class RealAuthorityIsolationTests(unittest.TestCase):
    def test_real_modules_do_not_import_paper_or_broker_modules(self) -> None:
        for relative in REAL_MODULES:
            source = (REPO_ROOT / relative).read_text(encoding="utf-8")
            for forbidden_import in (
                "paper_",
                "broker_adapter",
                "paper",
            ):
                # only guard real import lines, not prose mentioning paper
                for line in source.splitlines():
                    stripped = line.strip()
                    if stripped.startswith("import ") or stripped.startswith("from "):
                        self.assertNotIn(
                            forbidden_import,
                            stripped,
                            f"{relative} imports {forbidden_import!r}: {stripped}",
                        )

    def test_real_modules_have_no_secret_or_invented_endpoint_surface(self) -> None:
        for relative in REAL_MODULES:
            source = (REPO_ROOT / relative).read_text(encoding="utf-8")
            for forbidden in FORBIDDEN_SECRET_OR_ENDPOINT_IDENTIFIERS:
                self.assertNotIn(forbidden, source, f"{relative} contains {forbidden!r}")

    def test_real_modules_embed_no_permanent_numeric_risk_rule(self) -> None:
        for relative in REAL_MODULES:
            source = (REPO_ROOT / relative).read_text(encoding="utf-8")
            for forbidden in FORBIDDEN_RISK_IDENTIFIERS:
                self.assertNotIn(forbidden, source, f"{relative} contains {forbidden!r}")
            # no numeric risk-ratio literal assignments such as risk = 0.01
            for match in re.finditer(r"risk\s*=\s*0?\.?\d+", source):
                self.fail(f"{relative} embeds numeric risk literal: {match.group(0)}")

    def test_real_modules_represent_unknown_explicitly_not_fabricated(self) -> None:
        config_source = (REPO_ROOT / "src" / "real_runtime_config.py").read_text(encoding="utf-8")
        self.assertIn("UNBOUND", config_source)
        self.assertIn("RESULT_DEPENDENT_BINDING_NAMES", config_source)
        profile_source = (REPO_ROOT / "src" / "real_activation_profile.py").read_text(encoding="utf-8")
        self.assertIn("RESULT_DEPENDENT_POLICY_NAMES", profile_source)

    def test_paper_authority_behavior_is_unchanged(self) -> None:
        # The accepted PAPER authority still rejects secret values and order
        # permission without connect permission.
        with self.assertRaisesRegex(ValueError, "never values"):
            PaperExecutionAuthority(
                authority_id="bad-secret",
                broker_kind="TQSDK",
                account_kind="TQKQ",
                status=PaperAuthorityStatus.PENDING,
                allow_connect=False,
                allow_order_submit=False,
                credential_env_names=("PASSWORD=secret",),
            )
        with self.assertRaises(ValueError):
            PaperExecutionAuthority(
                authority_id="bad",
                broker_kind="TQSDK",
                account_kind="TQKQ",
                status=PaperAuthorityStatus.ACTIVE,
                allow_connect=False,
                allow_order_submit=True,
            )

    def test_real_authority_is_semantically_separate_from_paper(self) -> None:
        from src.real_execution_authority import (
            REAL_EXECUTION_AUTHORITY_SCHEMA_VERSION,
            RealAuthorityStatus,
            RealExecutionAuthority,
        )

        self.assertTrue(REAL_EXECUTION_AUTHORITY_SCHEMA_VERSION.startswith("KPE_REAL_"))
        self.assertNotIn("allow_connect", REAL_EXECUTION_AUTHORITY_SCHEMA_VERSION)
        self.assertEqual(
            {item.value for item in RealAuthorityStatus},
            {"PENDING", "ACTIVE", "REVOKED", "DISABLED"},
        )


if __name__ == "__main__":
    unittest.main()
