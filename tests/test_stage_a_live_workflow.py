from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
V02_WORKFLOW = ROOT / ".github" / "workflows" / "stage-a-live-slot.yml"
V03_WORKFLOW = ROOT / ".github" / "workflows" / "stage-a-v0-3-live-slot.yml"
OFFLINE_WORKFLOW = ROOT / ".github" / "workflows" / "stage-a-offline-ci.yml"
V03_LANE = ROOT / "src" / "jianghe_v03_live_lane.py"
V03_CLI = ROOT / "tools" / "run_jianghe_v03_slot.py"
V03_PLAN = ROOT / "docs" / "evidence" / "JIANGHE_STAGE_A_FROZEN_PLAN_V0_3.json"


class StageAV02RetiredWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.live = V02_WORKFLOW.read_text(encoding="utf-8")
        cls.offline = OFFLINE_WORKFLOW.read_text(encoding="utf-8")

    def test_v0_2_workflow_is_retired_and_fails_closed(self) -> None:
        self.assertIn("RETIRED", self.live)
        self.assertIn("PAID_CALLS=PAUSED_UNTIL_V0_3_OFFLINE_CLOSURE", self.live)
        self.assertIn("exit 1", self.live)
        self.assertNotIn("run_jianghe_stage_a_live_slot.py", self.live)
        self.assertNotIn("secrets.DEEPSEEK_API_KEY", self.live)

    def test_v0_2_old_slots_are_not_executable(self) -> None:
        self.assertIn("OLD_DEEPSEEK_1=HISTORICAL_DO_NOT_RERUN", self.live)
        self.assertIn("OLD_MINIMAX_1=HISTORICAL_DO_NOT_RERUN", self.live)
        self.assertIn("OLD_KIMI_1=SUPERSEDED_DO_NOT_EXECUTE", self.live)

    def test_offline_pr_ci_has_empty_provider_credentials_and_v7_actions(self) -> None:
        for name in ("MOONSHOT_API_KEY", "DEEPSEEK_API_KEY", "MINIMAX_API_KEY"):
            self.assertIn(f'{name}: ""', self.offline)
        self.assertNotIn("secrets.", self.offline)
        self.assertNotIn("run_jianghe_stage_a_live_slot.py", self.offline)
        self.assertNotIn("run_jianghe_v03_slot.py", self.offline)
        self.assertIn("actions/checkout@v7", self.offline)
        self.assertIn("actions/setup-python@v7", self.offline)
        self.assertNotIn("actions/checkout@v4", self.offline)
        self.assertNotIn("actions/setup-python@v5", self.offline)


class StageAV03WorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.v03 = V03_WORKFLOW.read_text(encoding="utf-8")
        cls.lane = V03_LANE.read_text(encoding="utf-8")
        cls.cli = V03_CLI.read_text(encoding="utf-8")
        cls.plan = V03_PLAN.read_text(encoding="utf-8")

    def test_v0_3_workflow_is_manual_only_and_main_only(self) -> None:
        self.assertIn("workflow_dispatch:", self.v03)
        self.assertNotIn("pull_request:", self.v03)
        self.assertNotIn("push:", self.v03)
        self.assertIn("if: github.ref == 'refs/heads/main'", self.v03)

    def test_v0_3_workflow_input_is_provider_only(self) -> None:
        self.assertIn("inputs:", self.v03)
        self.assertIn("provider:", self.v03)
        for forbidden in ("slot", "remote_ref", "model", "max_output", "timeout"):
            self.assertNotIn(f"        {forbidden}:", self.v03)
            self.assertNotIn(f"      {forbidden}:", self.v03)

    def test_v0_3_workflow_protected_environment_and_node24_actions(self) -> None:
        self.assertIn("environment: stage-a-readiness", self.v03)
        self.assertIn("contents: write", self.v03)
        self.assertIn("persist-credentials: true", self.v03)
        self.assertIn("actions/checkout@v7", self.v03)
        self.assertIn("actions/setup-python@v7", self.v03)
        self.assertNotIn("actions/checkout@v4", self.v03)
        self.assertNotIn("actions/setup-python@v5", self.v03)
        self.assertIn('python-version: "3.12"', self.v03)
        self.assertIn("timeout-minutes: 30", self.v03)

    def test_v0_3_workflow_secrets_are_per_provider_and_not_echoed(self) -> None:
        deepseek_step = self.v03.split("Execute one V0.3 DeepSeek", 1)[1]
        deepseek_step = deepseek_step.split("Execute one V0.3 MiniMax", 1)[0]
        self.assertIn("DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}", deepseek_step)
        self.assertNotIn("MOONSHOT_API_KEY: ${{ secrets.MOONSHOT_API_KEY }}", deepseek_step)
        self.assertNotIn("MINIMAX_API_KEY: ${{ secrets.MINIMAX_API_KEY }}", deepseek_step)
        for name in ("MOONSHOT_API_KEY", "DEEPSEEK_API_KEY", "MINIMAX_API_KEY"):
            self.assertNotIn(f"echo ${name}", self.v03)
        self.assertNotIn("curl ", self.v03)
        self.assertNotIn("wget ", self.v03)

    def test_v0_3_cli_exposes_only_provider_and_blocks_caller_choice(self) -> None:
        self.assertEqual(1, self.cli.count("parser.add_argument("))
        self.assertIn('parser.add_argument("--provider"', self.cli)
        for forbidden in ("--slot", "--remote-ref", "--model", "--max-output", "--timeout"):
            self.assertNotIn(forbidden, self.cli)
        self.assertIn("DEFAULT_REMOTE_REF", self.lane)
        self.assertIn("refs/heads/stage-a-live-state-v0-3", self.lane)
        self.assertIn("caller-selected V0.3 remote ref is forbidden", self.lane)
        self.assertIn("terminal = reserved.append_terminal(", self.cli)
        self.assertNotIn("terminal = ledger.append_terminal(", self.cli)

    def test_v0_3_plan_frozen_identities_present(self) -> None:
        self.assertIn("JIANGHE_STAGE_A_FROZEN_PLAN_V0_3", self.plan)
        self.assertIn("common_exam_identity", self.plan)
        self.assertIn("V0_3:DEEPSEEK:CAPABILITY_MATCHED_001", self.plan)
        self.assertIn("V0_3:MINIMAX:CAPABILITY_MATCHED_001", self.plan)
        self.assertIn("V0_3:KIMI:CAPABILITY_MATCHED_001", self.plan)
        self.assertIn("0.270021", self.plan)
        self.assertIn('"100"', self.plan)
        self.assertIn("refs/heads/stage-a-live-state-v0-3", self.plan)

    def test_v0_3_workflow_uploads_secret_safe_evidence_always(self) -> None:
        self.assertIn("if: always()", self.v03)
        self.assertIn("actions/upload-artifact@v4", self.v03)
        self.assertIn("stage-a-v0-3-evidence", self.v03)


if __name__ == "__main__":
    unittest.main()
