from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
LIVE_WORKFLOW = ROOT / ".github" / "workflows" / "stage-a-live-slot.yml"
OFFLINE_WORKFLOW = ROOT / ".github" / "workflows" / "stage-a-offline-ci.yml"
LIVE_LANE = ROOT / "src" / "jianghe_stage_a_live_lane.py"


class StageALiveWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.live = LIVE_WORKFLOW.read_text(encoding="utf-8")
        cls.offline = OFFLINE_WORKFLOW.read_text(encoding="utf-8")
        cls.lane = LIVE_LANE.read_text(encoding="utf-8")

    def test_workflow_is_manual_only_and_main_only(self) -> None:
        self.assertIn("workflow_dispatch:", self.live)
        self.assertNotIn("pull_request:", self.live)
        self.assertNotIn("push:", self.live)
        self.assertIn("if: github.ref == 'refs/heads/main'", self.live)
        self.assertIn("ref: main", self.live)

    def test_workflow_uses_protected_environment_and_bounded_permission(self) -> None:
        self.assertIn("environment: stage-a-readiness", self.live)
        self.assertIn("permissions:\n  contents: write", self.live)
        self.assertNotIn("id-token: write", self.live)
        self.assertNotIn("actions: write", self.live)

    def test_workflow_concurrency_is_secondary_fail_safe(self) -> None:
        self.assertIn("group: stage-a-live-single-slot", self.live)
        self.assertIn("cancel-in-progress: false", self.live)
        self.assertIn("compare_and_swap", self.lane)

    def test_frozen_plan_is_checked_before_secret_injection(self) -> None:
        plan_index = self.live.index("Verify frozen plan before credentials")
        secret_index = self.live.index("MOONSHOT_API_KEY: ${{ secrets.MOONSHOT_API_KEY }}")
        self.assertLess(plan_index, secret_index)

    def test_named_environment_secrets_are_not_echoed(self) -> None:
        for name in ("MOONSHOT_API_KEY", "DEEPSEEK_API_KEY", "MINIMAX_API_KEY"):
            self.assertIn(f"{name}: ${{{{ secrets.{name} }}}}", self.live)
            self.assertNotIn(f"echo ${name}", self.live)
        self.assertNotIn("Authorization", self.live)
        self.assertNotIn("curl ", self.live)
        self.assertNotIn("wget ", self.live)

    def test_offline_pr_ci_has_empty_provider_credentials(self) -> None:
        for name in ("MOONSHOT_API_KEY", "DEEPSEEK_API_KEY", "MINIMAX_API_KEY"):
            self.assertIn(f'{name}: ""', self.offline)
        self.assertNotIn("secrets.", self.offline)
        self.assertNotIn("run_jianghe_stage_a_live_slot.py", self.offline)

    def test_production_workflow_uses_only_remote_reserved_orchestrator(self) -> None:
        self.assertIn("run_jianghe_stage_a_live_slot.py", self.live)
        self.assertNotIn("run_jianghe_stage_a_slot.py", self.live)
        self.assertIn("execute_remote_reserved_slot", self.lane)

    def test_raw_journal_has_no_remote_commit_path_and_bsp003_is_absent(self) -> None:
        self.assertNotIn("journal.jsonl", self.live)
        self.assertNotIn("acknowledged_principles", self.lane)
        self.assertNotIn("violated_principles", self.lane)
        self.assertNotIn("fidelity_score", self.lane)
        self.assertNotIn("provider_ranking", self.lane)


if __name__ == "__main__":
    unittest.main()
