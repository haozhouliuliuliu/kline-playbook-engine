from __future__ import annotations

import json
import unittest

from tools.check_authority_consistency import (
    REPO_ROOT,
    SMOKE_AUTHORITY_PATH,
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
        machine_status = _assignment_values(
            state, "THREE_CALL_SMOKE_MACHINE_AUTHORITY_STATUS"
        )
        self.assertEqual(payload["authority_identity"], _canonical_identity(payload))
        self.assertEqual(machine_status, [payload["status"]])
        self.assertIn(payload["status"], {"PENDING_OWNER_PAYMENT_CONFIRMATION", "ACTIVE", "REVOKED"})
        self.assertEqual(payload["api_key_env"], "DEEPSEEK_API_KEY")

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
