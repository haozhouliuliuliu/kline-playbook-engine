from __future__ import annotations

import collections
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.jianghe_source_only_verification import _claim_paths, _manifest, _relative

SOURCE_ONLY_COMMIT = "ca7d99beacdaeb3b6bd7d8ef9fc3422f9481bf28"
FORMAL_PATH = ROOT / "docs" / "evidence" / "JIANGHE_V1_1_SOURCE_ONLY_VERIFICATION_V0_1.json"
formal = json.loads(FORMAL_PATH.read_text(encoding="utf-8"))
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

print("CLAIM_MANIFEST_FIELD_DRIFT_DIAGNOSTIC_V0_2")
print(f"SOURCE_ONLY_COMMIT={SOURCE_ONLY_COMMIT}")
print(f"FORMAL_IDENTITY={formal_manifest['claim_manifest_identity']}")
print(f"CURRENT_DYNAMIC_MANIFEST_IDENTITY={current_manifest['manifest_identity']}")
print(f"FORMAL_MATERIAL_COUNT={len(formal_materials)}")
print(f"CURRENT_DYNAMIC_MATERIAL_COUNT={len(current_materials)}")
print("ADDED_PATHS=" + json.dumps(sorted(set(current_materials) - set(formal_materials))))
print("REMOVED_PATHS=" + json.dumps(sorted(set(formal_materials) - set(current_materials))))

primary_consumed_fields = {
    "source_ordinal", "bvid",
    "source_anchor_type", "source_anchor", "language_anchor_short",
    "source_timestamp_start", "source_timestamp_end",
    "claim_status", "claim_category", "interpretation_status",
    "machineability", "review_status", "interpretation_text",
    "ambiguity_notes", "strategy_family_ids",
}
meaning_fields = {
    "source_ordinal", "bvid",
    "source_anchor_type", "source_anchor", "language_anchor_short",
    "source_timestamp_start", "source_timestamp_end",
    "claim_status", "claim_category", "interpretation_status",
    "machineability", "interpretation_text", "ambiguity_notes",
    "strategy_family_ids",
}

all_changed_fields = collections.Counter()
primary_changed_fields = collections.Counter()
meaning_changed_fields = collections.Counter()
changed_claims = 0
primary_changed_claims = 0
meaning_changed_claims = 0
history_hash_mismatches = []
file_summaries = []

for relative_path in sorted(formal_materials):
    historical_bytes = subprocess.check_output(
        ["git", "show", f"{SOURCE_ONLY_COMMIT}:{relative_path}"], cwd=ROOT
    )
    historical_sha = hashlib.sha256(historical_bytes).hexdigest()
    if historical_sha != formal_materials[relative_path]:
        history_hash_mismatches.append({
            "path": relative_path,
            "formal_sha256": formal_materials[relative_path],
            "source_only_commit_sha256": historical_sha,
        })

    old_rows = [json.loads(line) for line in historical_bytes.decode("utf-8").splitlines() if line.strip()]
    new_rows = [json.loads(line) for line in (ROOT / relative_path).read_text(encoding="utf-8").splitlines() if line.strip()]
    old_by_id = {row["claim_id"]: row for row in old_rows}
    new_by_id = {row["claim_id"]: row for row in new_rows}
    old_ids = set(old_by_id)
    new_ids = set(new_by_id)
    local_changed = 0
    local_primary = 0
    local_meaning = 0
    local_fields = collections.Counter()
    local_primary_fields = collections.Counter()
    local_meaning_fields = collections.Counter()

    for claim_id in sorted(old_ids & new_ids):
        old = old_by_id[claim_id]
        new = new_by_id[claim_id]
        fields = sorted(set(old) | set(new))
        changed = {field for field in fields if old.get(field) != new.get(field)}
        if changed:
            changed_claims += 1
            local_changed += 1
            all_changed_fields.update(changed)
            local_fields.update(changed)
        primary_changed = changed & primary_consumed_fields
        if primary_changed:
            primary_changed_claims += 1
            local_primary += 1
            primary_changed_fields.update(primary_changed)
            local_primary_fields.update(primary_changed)
        meaning_changed = changed & meaning_fields
        if meaning_changed:
            meaning_changed_claims += 1
            local_meaning += 1
            meaning_changed_fields.update(meaning_changed)
            local_meaning_fields.update(meaning_changed)

    file_summaries.append({
        "path": relative_path,
        "old_rows": len(old_rows),
        "new_rows": len(new_rows),
        "added_claim_ids": sorted(new_ids - old_ids),
        "removed_claim_ids": sorted(old_ids - new_ids),
        "changed_claims": local_changed,
        "primary_consumed_changed_claims": local_primary,
        "meaning_changed_claims": local_meaning,
        "changed_fields": dict(local_fields),
        "primary_changed_fields": dict(local_primary_fields),
        "meaning_changed_fields": dict(local_meaning_fields),
    })

print("SOURCE_ONLY_COMMIT_HASH_MISMATCHES=" + json.dumps(history_hash_mismatches, ensure_ascii=False, sort_keys=True))
print(f"CHANGED_CLAIMS={changed_claims}")
print(f"PRIMARY_CONSUMED_CHANGED_CLAIMS={primary_changed_claims}")
print(f"MEANING_CHANGED_CLAIMS={meaning_changed_claims}")
print("ALL_CHANGED_FIELDS=" + json.dumps(dict(all_changed_fields), ensure_ascii=False, sort_keys=True))
print("PRIMARY_CHANGED_FIELDS=" + json.dumps(dict(primary_changed_fields), ensure_ascii=False, sort_keys=True))
print("MEANING_CHANGED_FIELDS=" + json.dumps(dict(meaning_changed_fields), ensure_ascii=False, sort_keys=True))
print("FILE_SUMMARIES=" + json.dumps(file_summaries, ensure_ascii=False, sort_keys=True))

# Diagnostic only. Never rebind or mutate PRIMARY from this run.
raise SystemExit(7)
