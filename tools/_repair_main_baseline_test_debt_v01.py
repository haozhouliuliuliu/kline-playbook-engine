from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.jianghe_source_only_verification import _claim_paths, _manifest, _relative

formal_path = ROOT / "docs" / "evidence" / "JIANGHE_V1_1_SOURCE_ONLY_VERIFICATION_V0_1.json"
formal = json.loads(formal_path.read_text(encoding="utf-8"))
formal_manifest = formal["claim_manifest"]
formal_materials = {
    item["repository_artifact"]: item["content_sha256"]
    for item in formal_manifest["materials"]
}

current_paths = tuple(_claim_paths())
current_materials = {
    _relative(path): hashlib.sha256(path.read_bytes()).hexdigest()
    for path in current_paths
}
current_manifest = _manifest("JIANGHE_V1_1_CLAIM_MANIFEST", current_paths)

formal_names = set(formal_materials)
current_names = set(current_materials)
added = sorted(current_names - formal_names)
removed = sorted(formal_names - current_names)
hash_mismatches = [
    {
        "path": name,
        "formal_sha256": formal_materials[name],
        "current_sha256": current_materials[name],
    }
    for name in sorted(formal_names & current_names)
    if formal_materials[name] != current_materials[name]
]

print("CLAIM_MANIFEST_IDENTITY_DIAGNOSTIC_V0_1")
print(f"FORMAL_IDENTITY={formal_manifest['claim_manifest_identity']}")
print(f"FORMAL_MANIFEST_IDENTITY={formal_manifest['manifest_identity']}")
print(f"CURRENT_DYNAMIC_MANIFEST_IDENTITY={current_manifest['manifest_identity']}")
print(f"FORMAL_MATERIAL_COUNT={len(formal_materials)}")
print(f"CURRENT_DYNAMIC_MATERIAL_COUNT={len(current_materials)}")
print("ADDED_PATHS=" + json.dumps(added, ensure_ascii=False, sort_keys=True))
print("REMOVED_PATHS=" + json.dumps(removed, ensure_ascii=False, sort_keys=True))
print("HASH_MISMATCHES=" + json.dumps(hash_mismatches, ensure_ascii=False, sort_keys=True))
print("CURRENT_DYNAMIC_PATHS=" + json.dumps(sorted(current_materials), ensure_ascii=False))

# This is intentionally diagnostic-only. Never mutate PRIMARY identity from this run.
raise SystemExit(7)
