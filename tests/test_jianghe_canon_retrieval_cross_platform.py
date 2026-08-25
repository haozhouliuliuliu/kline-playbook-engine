from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from src.jianghe_canon_retrieval import JiangheCanonRetriever


CANONICAL_PATH = "docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md"
WINDOWS_STYLE_PATH = r"docs\research\jianghe\JIANGHE_CURRENT_VIEW_V1_1.md"


class JiangheCanonCrossPlatformPathTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        target = self.root / Path(CANONICAL_PATH)
        target.parent.mkdir(parents=True)
        target.write_text(
            "# Jianghe fixture\nUNKNOWN 必须保持 UNKNOWN。\n",
            encoding="utf-8",
        )

    def test_windows_and_posix_separator_inputs_share_one_canonical_identity(self) -> None:
        windows = JiangheCanonRetriever(
            self.root,
            allowed_paths=(WINDOWS_STYLE_PATH,),
            max_results=3,
            max_chars=1000,
            context_lines=0,
        )
        posix = JiangheCanonRetriever(
            self.root,
            allowed_paths=(CANONICAL_PATH,),
            max_results=3,
            max_chars=1000,
            context_lines=0,
        )

        self.assertEqual(windows.allowed_paths, (CANONICAL_PATH,))
        self.assertEqual(windows.identity, posix.identity)
        hits = windows.search("UNKNOWN")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0].document_path, CANONICAL_PATH)
        self.assertEqual(hits[0].retrieval_identity, posix.search("UNKNOWN")[0].retrieval_identity)

    def test_windows_absolute_unc_and_traversal_paths_remain_fail_closed(self) -> None:
        invalid_paths = (
            r"C:\repo\docs\research\jianghe\JIANGHE_CURRENT_VIEW_V1_1.md",
            r"\\server\share\docs\research\jianghe\JIANGHE_CURRENT_VIEW_V1_1.md",
            "/docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md",
            r"docs\research\jianghe\..\outside.md",
            "../docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md",
        )
        for path in invalid_paths:
            with self.subTest(path=path), self.assertRaises(ValueError):
                JiangheCanonRetriever(self.root, allowed_paths=(path,))


if __name__ == "__main__":
    unittest.main()
