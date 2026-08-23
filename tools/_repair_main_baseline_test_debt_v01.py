from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SOURCE_ONLY_COMMIT = "ca7d99beacdaeb3b6bd7d8ef9fc3422f9481bf28"
FORMAL_PATH = ROOT / "docs" / "evidence" / "JIANGHE_V1_1_SOURCE_ONLY_VERIFICATION_V0_1.json"
formal = json.loads(FORMAL_PATH.read_text(encoding="utf-8"))
materials = formal["claim_manifest"]["materials"]

rows = []
all_crlf_signature = True
for item in materials:
    path = item["repository_artifact"]
    git_bytes = subprocess.check_output(["git", "show", f"{SOURCE_ONLY_COMMIT}:{path}"], cwd=ROOT)
    lf_count = git_bytes.count(b"\n")
    formal_size = int(item["byte_size"])
    git_size = len(git_bytes)
    delta = formal_size - git_size
    current_sha = hashlib.sha256(git_bytes).hexdigest()
    crlf_signature = delta == lf_count
    all_crlf_signature = all_crlf_signature and crlf_signature
    rows.append({
        "path": path,
        "formal_size": formal_size,
        "git_size": git_size,
        "size_delta": delta,
        "lf_count": lf_count,
        "delta_equals_lf_count": crlf_signature,
        "formal_sha256": item["content_sha256"],
        "git_sha256": current_sha,
    })

print("CLAIM_MANIFEST_LINE_ENDING_DIAGNOSTIC_V0_3")
print(f"SOURCE_ONLY_COMMIT={SOURCE_ONLY_COMMIT}")
print(f"ALL_16_SIZE_DELTA_EQUALS_LF_COUNT={all_crlf_signature}")
print("ROWS=" + json.dumps(rows, ensure_ascii=False, sort_keys=True))
print("INTERPRETATION=If every formal_size minus Git blob size equals the blob LF count, the formal evidence was hashed/sized from CRLF working-tree bytes while Git stored normalized LF bytes.")
raise SystemExit(7)
