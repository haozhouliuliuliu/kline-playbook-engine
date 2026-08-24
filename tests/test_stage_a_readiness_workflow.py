from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "stage-a-provider-readiness.yml"


class StageAReadinessWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_is_manual_only_and_main_only(self) -> None:
        self.assertIn("workflow_dispatch:", self.text)
        self.assertNotIn("pull_request:", self.text)
        self.assertNotIn("push:", self.text)
        self.assertIn("if: github.ref == 'refs/heads/main'", self.text)
        self.assertIn("ref: main", self.text)

    def test_uses_read_only_permissions_and_protected_environment(self) -> None:
        self.assertIn("permissions:\n  contents: read", self.text)
        self.assertNotIn("contents: write", self.text)
        self.assertIn("environment: stage-a-readiness", self.text)
        self.assertIn("persist-credentials: false", self.text)

    def test_reads_only_named_provider_secrets(self) -> None:
        self.assertIn("MOONSHOT_API_KEY: ${{ secrets.MOONSHOT_API_KEY }}", self.text)
        self.assertIn("DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}", self.text)
        self.assertIn("MINIMAX_API_KEY: ${{ secrets.MINIMAX_API_KEY }}", self.text)
        self.assertNotIn("echo $MOONSHOT_API_KEY", self.text)
        self.assertNotIn("echo $DEEPSEEK_API_KEY", self.text)
        self.assertNotIn("echo $MINIMAX_API_KEY", self.text)

    def test_cannot_run_stage_a_model_slot(self) -> None:
        self.assertIn("tools/check_jianghe_provider_readiness.py", self.text)
        self.assertNotIn("run_jianghe_stage_a_slot.py", self.text)
        self.assertNotIn("chat/completions", self.text)
        self.assertNotIn("curl ", self.text)
        self.assertNotIn("wget ", self.text)

    def test_report_is_sanitized_and_short_lived(self) -> None:
        self.assertIn("model_endpoint_called", self.text)
        self.assertIn("credential_value_exposed", self.text)
        self.assertIn("retention-days: 1", self.text)
        self.assertIn("No model call was made.", self.text)


if __name__ == "__main__":
    unittest.main()
