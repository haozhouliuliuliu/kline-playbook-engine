from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tools.run_persistent_deepseek_trader_offline_probe import run_probe


class PersistentDeepSeekOfflineProbeTests(unittest.TestCase):
    def test_real_repository_offline_core_probe_passes_without_provider_transport(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as root:
            summary = run_probe(repo_root=repo_root, state_dir=Path(root))
            self.assertFalse(summary["provider_call_made"])
            self.assertTrue(all(summary["checks"].values()))
            self.assertGreaterEqual(summary["post_restart_audit_count"], 1)
            self.assertTrue(Path(summary["database_path"]).is_file())
            self.assertTrue((Path(root) / "offline-probe-summary.json").is_file())
            for timeframe in ("4H", "1H", "15m", "5m"):
                self.assertTrue((Path(root) / "charts" / f"{timeframe}.png").is_file())
                self.assertTrue((Path(root) / "charts" / f"{timeframe}.manifest.json").is_file())


if __name__ == "__main__":
    unittest.main()
