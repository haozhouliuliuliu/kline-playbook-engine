#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Regression test for the Jianghe formal evidence artifact set."""
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class JiangheEvidenceTests(unittest.TestCase):
    def test_evidence_package_is_consistent(self):
        result = subprocess.run(
            [sys.executable, "tools/validate_jianghe_evidence.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("JIANGHE_EVIDENCE_VALIDATION=OK", result.stdout)
