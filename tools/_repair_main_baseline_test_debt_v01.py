from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD = "60d4a1f9069a6dc33d04a82ce544d7525cd4bf2805c5b6e8dd9502d85bf39940"
NEW = "f767253dc4c2d1b17f57b9adfdc903907a97df8d4697dbe0fae0f603427dbf36"

result = subprocess.run(
    ["git", "grep", "-l", OLD, "--", ":!docs/reviews/MAIN_BASELINE_TEST_DEBT_CI_DIAGNOSTIC.tmp.md"],
    cwd=ROOT,
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    check=False,
)
paths = [line.strip() for line in result.stdout.splitlines() if line.strip()]
print("CLAIM_MANIFEST_REFERENCE_INVENTORY_V0_1")
print(f"OLD={OLD}")
print(f"EXPECTED_NEW={NEW}")
print(f"MATCH_COUNT={len(paths)}")
print("MATCH_PATHS=" + json.dumps(paths, ensure_ascii=False))
for path in paths:
    count = (ROOT / path).read_text(encoding="utf-8").count(OLD)
    print(f"PATH_COUNT {path} {count}")
raise SystemExit(7)
