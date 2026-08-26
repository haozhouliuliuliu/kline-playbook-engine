from __future__ import annotations

import json
import unittest

from tools.check_authority_consistency import (
    REPO_ROOT,
    SMOKE_AUTHORITY_PATH,
    SMOKE_RETEST_AUTHORITY_PATH,
    _assignment_values,
    _canonical_identity,
    check_repository,
)


class AuthorityConsistencyTests(unittest.TestCase):
    def test_current_repository_authority_consistency_passes(self) -> None:
        self.assertEqual(check_repository(REPO_ROOT), [])

    def test_assignment_parser_detects_markdown_wrapped_assignment(self) -> None:
        text = "before\n`CURRENT_WORK_PACKAGE = EXAMPLE`\nafter\n"
        self.assertEqual(_assignment_values(text, "CURRENT_WORK_PACKAGE"), ["EXAMPLE"])

    def test_machine_authority_identity_is_self_consistent(self) -> None:
        path = REPO_ROOT / SMOKE_AUTHORITY_PATH
        payload = json.loads(path.read_text(encoding="utf-8"))
        state = (REPO_ROOT / "CURRENT_STATE.md").read_text(encoding="utf-8")
        self.assertEqual(payload["authority_identity"], _canonical_identity(payload))
        self.assertIn(payload["status"], {"PENDING_OWNER_PAYMENT_CONFIRMATION", "ACTIVE", "REVOKED"})
        self.assertEqual(payload["api_key_env"], "DEEPSEEK_API_KEY")

        # CURRENT_STATE must reflect the current machine authority status. The
        # post-repair state uses ORIGINAL_SMOKE_MACHINE_AUTHORITY (old terminal
        # slot) and FRESH_THREE_CALL_RETEST_MACHINE_AUTHORITY (new retest slot);
        # the legacy THREE_CALL_SMOKE_MACHINE_AUTHORITY_STATUS key is optional.
        legacy = _assignment_values(state, "THREE_CALL_SMOKE_MACHINE_AUTHORITY_STATUS")
        if legacy:
            self.assertEqual(legacy, [payload["status"]])
        original = _assignment_values(state, "ORIGINAL_SMOKE_MACHINE_AUTHORITY")
        if original:
            if payload["status"] == "REVOKED":
                self.assertIn("REVOKED", original[0])
        fresh = _assignment_values(state, "FRESH_THREE_CALL_RETEST_MACHINE_AUTHORITY")
        if fresh:
            self.assertIn(
                fresh[0], {"NOT_YET_ACTIVE", "ACTIVE", "REVOKED", "REVOKED__TERMINAL"}
            )

    def test_retest_machine_authority_is_self_consistent(self) -> None:
        path = REPO_ROOT / SMOKE_RETEST_AUTHORITY_PATH
        if not path.is_file():
            self.skipTest("fresh retest machine authority not yet generated")
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["authority_identity"], _canonical_identity(payload))
        self.assertIn(payload["status"], {"PENDING_OWNER_PAYMENT_CONFIRMATION", "ACTIVE", "REVOKED"})
        self.assertEqual(payload["api_key_env"], "DEEPSEEK_API_KEY")
        state = (REPO_ROOT / "CURRENT_STATE.md").read_text(encoding="utf-8")
        fresh = _assignment_values(state, "FRESH_THREE_CALL_RETEST_MACHINE_AUTHORITY")
        expected = {
            "ACTIVE": "ACTIVE",
            "REVOKED": "REVOKED__TERMINAL",
            "PENDING_OWNER_PAYMENT_CONFIRMATION": "NOT_YET_ACTIVE",
        }[payload["status"]]
        if fresh:
            self.assertIn(expected, fresh[0])

    def test_owner_windows_user_environment_credential_convention_is_preserved(self) -> None:
        registry = (REPO_ROOT / "TOOL_REGISTRY.md").read_text(encoding="utf-8")
        self.assertIn(
            "LOCAL_PROVIDER_SECRET_STORE = WINDOWS_CURRENT_USER_ENVIRONMENT_VARIABLES",
            registry,
        )
        for variable_name in (
            "ANTHROPIC_API_KEY",
            "DASHSCOPE_API_KEY",
            "DEEPSEEK_API_KEY",
            "GEMINI_API_KEY",
            "SILICONFLOW_API_KEY",
        ):
            self.assertIn(variable_name, registry)
        self.assertIn("CREDENTIAL_ENV = DEEPSEEK_API_KEY", registry)
        self.assertIn(
            "CREDENTIAL_LOCATION = WINDOWS_CURRENT_USER_ENVIRONMENT_VARIABLES",
            registry,
        )


if __name__ == "__main__":
    unittest.main()
