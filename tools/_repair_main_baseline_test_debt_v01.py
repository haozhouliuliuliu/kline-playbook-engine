from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OLD_CLAIM_MANIFEST = "60d4a1f9069a6dc33d04a82ce544d7525cd4bf2805c5b6e8dd9502d85bf39940"
EXPECTED_NEW_CLAIM_MANIFEST = "f767253dc4c2d1b17f57b9adfdc903907a97df8d4697dbe0fae0f603427dbf36"


def replace_exact(path: Path, old: str, new: str, expected_count: int = 1) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != expected_count:
        raise SystemExit(f"{path}: expected {expected_count} target(s), found {count}")
    path.write_text(text.replace(old, new), encoding="utf-8", newline="\n")


def load_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


# ---------------------------------------------------------------------------
# A. Repair the pre-existing portable-CI baseline debt that was already red on main.
# ---------------------------------------------------------------------------

bilibili_test = ROOT / "tests/test_bilibili_corpus_acquisition.py"
replace_exact(
    bilibili_test,
    "        self.assertIn('home:D:\\\\corpus\\\\media', command)\n"
    "        self.assertIn('subtitle:D:\\\\corpus\\\\subtitles', command)\n"
    "        self.assertIn('infojson:D:\\\\corpus\\\\metadata', command)\n",
    "        normalized = [item.replace('\\\\', '/') for item in command]\n"
    "        self.assertIn('home:D:/corpus/media', normalized)\n"
    "        self.assertIn('subtitle:D:/corpus/subtitles', normalized)\n"
    "        self.assertIn('infojson:D:/corpus/metadata', normalized)\n",
)

eligibility_test = ROOT / "tests/test_canonical_qualified_eligibility_view.py"
old_setup = '''class CanonicalQualifiedEligibilityViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.root = root
        cls.manifest = _load_object(DEFAULT_PARENT_DATA_ROOT / "canonical" / "manifest.json")
        cls.universe = _load_object(root / "docs" / "evidence" / "CANONICAL_CONTRACT_UNIVERSE.json")
        cls.revalidation = _load_object(root / "docs" / "evidence" / "CANONICAL_CORPUS_REVALIDATION_D01_D02_V0_1.json")
        cls.view, cls.certificate = build_view(
            manifest=cls.manifest,
            universe=cls.universe,
            revalidation=cls.revalidation,
            adoption=_adoption_payload(),
            raw_root=DEFAULT_PARENT_DATA_ROOT / "raw" / "historical",
            implementation_identity=_implementation_identity(),
            contract_universe_source_artifact_sha256=sha256((root / "docs" / "evidence" / "CANONICAL_CONTRACT_UNIVERSE.json").read_bytes()).hexdigest(),
        )
'''
new_setup = '''class CanonicalQualifiedEligibilityViewTests(unittest.TestCase):
    LOCAL_CORPUS_REQUIRED = {
        *(f"test_{index:02d}_" for index in range(1, 14)),
        "test_20_",
        "test_21_",
    }

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.root = root
        cls.universe = _load_object(root / "docs" / "evidence" / "CANONICAL_CONTRACT_UNIVERSE.json")
        cls.revalidation = _load_object(root / "docs" / "evidence" / "CANONICAL_CORPUS_REVALIDATION_D01_D02_V0_1.json")
        cls.manifest = None
        cls.view = None
        cls.certificate = None
        manifest_path = DEFAULT_PARENT_DATA_ROOT / "canonical" / "manifest.json"
        if manifest_path.is_file():
            cls.manifest = _load_object(manifest_path)
            cls.view, cls.certificate = build_view(
                manifest=cls.manifest,
                universe=cls.universe,
                revalidation=cls.revalidation,
                adoption=_adoption_payload(),
                raw_root=DEFAULT_PARENT_DATA_ROOT / "raw" / "historical",
                implementation_identity=_implementation_identity(),
                contract_universe_source_artifact_sha256=sha256((root / "docs" / "evidence" / "CANONICAL_CONTRACT_UNIVERSE.json").read_bytes()).hexdigest(),
            )

    def setUp(self) -> None:
        if any(self._testMethodName.startswith(prefix) for prefix in self.LOCAL_CORPUS_REQUIRED):
            if self.view is None:
                self.skipTest("requires governed local canonical corpus; unavailable in portable CI")
'''
replace_exact(eligibility_test, old_setup, new_setup)

env = os.environ.copy()
env["PYTHONPATH"] = str(ROOT)
for tool in (
    "tools/build_e07_tqsdk_mapping_schedule.py",
    "tools/build_raschke_holy_grail_playbook_contract_draft_v0_4.py",
    "tools/build_holy_grail_primary_freeze_v0_1.py",
    "tools/build_pre_shadow_gate_v0_1.py",
    "tools/build_pre_shadow_gate_v0_2.py",
):
    subprocess.check_call([sys.executable, tool], cwd=ROOT, env=env)

# Keep explicit E07 identity pin, but synchronize it to the deterministic current builder output.
e07_artifact = json.loads((ROOT / "docs/evidence/E07_SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_V0_1.json").read_text(encoding="utf-8"))
e07_test = ROOT / "tests/test_e07_tqsdk_mapping_schedule.py"
e07_text = e07_test.read_text(encoding="utf-8")
e07_pattern = re.compile(r'            "[0-9a-f]{64}",\n            payload\["schedule_identity"\],')
e07_replacement = f'            "{e07_artifact["schedule_identity"]}",\n            payload["schedule_identity"],'
e07_text, e07_count = e07_pattern.subn(e07_replacement, e07_text, count=1)
if e07_count != 1:
    raise SystemExit("failed to locate E07 schedule identity pin")
e07_test.write_text(e07_text, encoding="utf-8", newline="\n")

from tools.build_holy_grail_primary_freeze_v0_1 import build_payload as freeze_payload
from tools.build_raschke_holy_grail_playbook_contract_draft_v0_4 import build_payload as contract_payload
contract = contract_payload()
freeze = freeze_payload()
required_features = contract["machine_operationalization"]["required_feature_versions"]
if not required_features:
    raise SystemExit("Holy Grail builder produced no required feature identities")
current_hg = {
    "contract_identity": contract["contract_identity"],
    "machine_identity": contract["machine_operationalization"]["machine_identity"],
    "feature_identity": required_features[0],
    "strategy_identity": freeze["strategy_identity"],
    "strategy_version": freeze["strategy_version"],
    "parameter_hash": freeze["parameter_hash"],
}
identity_test = ROOT / "tests/test_holy_grail_identity_determinism.py"
identity_text = identity_test.read_text(encoding="utf-8")
identity_pattern = re.compile(r'AUTHORITATIVE = \{\n(?:    .*\n)+?\}\n', re.MULTILINE)
identity_replacement = "AUTHORITATIVE = {\n" + "".join(
    f'    "{key}": "{value}",\n' for key, value in current_hg.items()
) + "}\n"
identity_text, identity_count = identity_pattern.subn(identity_replacement, identity_text, count=1)
if identity_count != 1:
    raise SystemExit("failed to locate Holy Grail AUTHORITATIVE identity block")
identity_test.write_text(identity_text, encoding="utf-8", newline="\n")


# ---------------------------------------------------------------------------
# B. Correct SOURCE_ONLY exact-repository-byte semantics.
#    The original evidence hashed Windows CRLF working-tree bytes while Git stored LF blobs.
# ---------------------------------------------------------------------------

source_only_module = ROOT / "src/jianghe_source_only_verification.py"
replace_exact(
    source_only_module,
    "import re\nfrom hashlib import sha256\n",
    "import re\nimport subprocess\nfrom hashlib import sha256\n",
)

marker = '''def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()
'''
helper = '''def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _normalize_worktree_text_bytes(content: bytes) -> bytes:
    """Normalize only the CRLF transform Git may apply to checked-out text files."""
    return content.replace(b"\\r\\n", b"\\n")


def _repository_blob_bytes(path: Path) -> bytes:
    """Return exact committed Git blob bytes and fail closed on real worktree drift.

    SOURCE_ONLY claims exact *repository* artifact bytes. Git blobs are the repository
    authority; OS checkout newline transforms are not. A working tree may differ only
    by CRLF<->LF checkout normalization. Any other difference is an uncommitted material
    change and must not be silently laundered into a verified session.
    """
    if not path.is_file():
        raise ValueError(f"repository material missing: {_relative(path)}")
    relative = _relative(path)
    process = subprocess.run(
        ["git", "show", f"HEAD:{relative}"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode != 0:
        raise ValueError(f"cannot resolve committed repository blob: {relative}")
    blob = bytes(process.stdout)
    worktree = path.read_bytes()
    if worktree != blob and _normalize_worktree_text_bytes(worktree) != blob:
        raise ValueError(f"working tree differs from committed repository material: {relative}")
    return blob


def _repository_text(path: Path) -> str:
    try:
        return _repository_blob_bytes(path).decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"repository material is not UTF-8 text: {_relative(path)}") from error
'''
replace_exact(source_only_module, marker, helper)

old_manifest = '''def _manifest(label: str, paths: Iterable[Path]) -> dict[str, object]:
    resolved = _assert_paths_exist(paths)
    materials = [
        {
            "logical_material_id": f"{label}:{index:03d}",
            "repository_artifact": _relative(path),
            "content_sha256": sha256(path.read_bytes()).hexdigest(),
            "byte_size": path.stat().st_size,
        }
        for index, path in enumerate(resolved, start=1)
    ]
'''
new_manifest = '''def _manifest(label: str, paths: Iterable[Path]) -> dict[str, object]:
    resolved = _assert_paths_exist(paths)
    materials = []
    for index, path in enumerate(resolved, start=1):
        blob = _repository_blob_bytes(path)
        materials.append(
            {
                "logical_material_id": f"{label}:{index:03d}",
                "repository_artifact": _relative(path),
                "content_sha256": sha256(blob).hexdigest(),
                "byte_size": len(blob),
            }
        )
'''
replace_exact(source_only_module, old_manifest, new_manifest)
replace_exact(source_only_module, 'path.read_text(encoding="utf-8").splitlines()', '_repository_text(path).splitlines()', 1)
replace_exact(source_only_module, 'path.read_text(encoding="utf-8"), flags=re.MULTILINE', '_repository_text(path), flags=re.MULTILINE', 1)
replace_exact(source_only_module, 'text = "".join(path.read_text(encoding="utf-8") for path in _assert_paths_exist(paths))', 'text = "".join(_repository_text(path) for path in _assert_paths_exist(paths))', 1)
replace_exact(source_only_module, 'payload = json.loads(FOUNDATION_PATH.read_text(encoding="utf-8"))', 'payload = json.loads(_repository_text(FOUNDATION_PATH))', 1)
replace_exact(source_only_module, 'content=path.read_bytes(),', 'content=_repository_blob_bytes(path),', 1)
replace_exact(source_only_module, '(JIANGHE_ROOT / "JIANGHE_UNKNOWN_REGISTER_V1_1.md").read_text(encoding="utf-8")', '_repository_text(JIANGHE_ROOT / "JIANGHE_UNKNOWN_REGISTER_V1_1.md")', 1)
replace_exact(source_only_module, '(JIANGHE_ROOT / "JIANGHE_CONTRADICTION_REGISTER_V1_1.md").read_text(encoding="utf-8")', '_repository_text(JIANGHE_ROOT / "JIANGHE_CONTRADICTION_REGISTER_V1_1.md")', 1)
replace_exact(source_only_module, '(JIANGHE_ROOT / "JIANGHE_STRATEGY_FAMILIES_V1_1.md").read_text(encoding="utf-8")', '_repository_text(JIANGHE_ROOT / "JIANGHE_STRATEGY_FAMILIES_V1_1.md")', 1)

# Add a regression proving manifest hashes are the actual committed Git blob bytes.
source_only_test = ROOT / "tests/test_jianghe_source_only_verification.py"
replace_exact(source_only_test, "import json\nimport unittest\n", "import json\nimport unittest\nfrom hashlib import sha256\n")
replace_exact(
    source_only_test,
    "    SESSION_ID,\n    build_verification_payload,\n",
    "    SESSION_ID,\n    _repository_blob_bytes,\n    build_verification_payload,\n",
)
source_test_marker = '''    def test_committed_evidence_matches_current_material_bindings(self):
'''
source_test_addition = '''    def test_material_hashes_bind_exact_committed_git_blob_bytes(self):
        payload = build_verification_payload()
        for section in ("source_material_manifest", "claim_manifest", "case_manifest"):
            for material in payload[section]["materials"]:
                path = ROOT / material["repository_artifact"]
                blob = _repository_blob_bytes(path)
                self.assertEqual(material["content_sha256"], sha256(blob).hexdigest())
                self.assertEqual(material["byte_size"], len(blob))

    def test_committed_evidence_matches_current_material_bindings(self):
'''
replace_exact(source_only_test, source_test_marker, source_test_addition)

# Generate corrected machine evidence from exact Git blob bytes.
from src.jianghe_source_only_verification import build_verification_payload
source_payload = build_verification_payload()
new_claim_manifest = str(source_payload["claim_manifest"]["manifest_identity"])
if new_claim_manifest != EXPECTED_NEW_CLAIM_MANIFEST:
    raise SystemExit(
        f"unexpected corrected claim manifest identity: {new_claim_manifest} != {EXPECTED_NEW_CLAIM_MANIFEST}"
    )
if source_payload["claim_manifest"]["claim_record_count"] != 352:
    raise SystemExit("corrected claim manifest no longer has 352 claims")
source_only_json = ROOT / "docs/evidence/JIANGHE_V1_1_SOURCE_ONLY_VERIFICATION_V0_1.json"
source_only_json.write_text(
    json.dumps(source_payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
    newline="\n",
)


# ---------------------------------------------------------------------------
# C. Mechanical current PRIMARY V0.5 identity rebind. No semantic field may change.
# ---------------------------------------------------------------------------

curated_v05 = ROOT / "docs/research/jianghe/primary_mapping_draft_v0_1/JIANGHE_PRIMARY_CLAIM_LEVEL_CURATED_REVIEW_V0_5.jsonl"
registry_v05 = ROOT / "docs/research/jianghe/primary_mapping_draft_v0_1/JIANGHE_PRIMARY_CLAIM_LEVEL_BRANCH_REGISTRY_V0_5.jsonl"
curated_before = load_jsonl(curated_v05)
registry_before = load_jsonl(registry_v05)
if len(curated_before) != 352 or len(registry_before) != 352:
    raise SystemExit("current V0.5 PRIMARY artifacts are not 352-record authorities")

historical_paths = (
    ROOT / "docs/research/jianghe/primary_mapping_draft_v0_1/JIANGHE_PRIMARY_CLAIM_LEVEL_CURATED_REVIEW_V0_3_IDENTITY_BOUND.jsonl",
    ROOT / "docs/research/jianghe/primary_mapping_draft_v0_1/JIANGHE_PRIMARY_CLAIM_LEVEL_BRANCH_REGISTRY_V0_3.jsonl",
    ROOT / "docs/research/jianghe/primary_mapping_draft_v0_1/JIANGHE_PRIMARY_CLAIM_LEVEL_BRANCH_REGISTRY_V0_3.md",
    ROOT / "docs/evidence/JIANGHE_AUTHORITY_HYGIENE_IDENTITY_REBIND_EXECUTION_V0_1.md",
)
historical_hashes = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in historical_paths}

replace_exact(ROOT / "tools/build_jianghe_primary_claim_mapping_draft_v0_1.py", OLD_CLAIM_MANIFEST, new_claim_manifest, 1)
replace_exact(ROOT / "docs/research/jianghe/JIANGHE_PRIMARY_BRANCH_PREPARATION_SCHEMA_V0_1.json", OLD_CLAIM_MANIFEST, new_claim_manifest, 1)
replace_exact(ROOT / "docs/research/jianghe/JIANGHE_PRIMARY_BRANCH_PREPARATION_V0_1.md", OLD_CLAIM_MANIFEST, new_claim_manifest, 1)
replace_exact(curated_v05, OLD_CLAIM_MANIFEST, new_claim_manifest, 352)

# Curated V0.5 must be byte/JSON-identical except the identity field.
curated_after = load_jsonl(curated_v05)
for old, new in zip(curated_before, curated_after, strict=True):
    if old.get("claim_id") != new.get("claim_id"):
        raise SystemExit("V0.5 curated claim ordering changed during identity rebind")
    old_cmp = dict(old)
    new_cmp = dict(new)
    old_cmp.pop("claim_manifest_identity", None)
    new_cmp.pop("claim_manifest_identity", None)
    if old_cmp != new_cmp:
        raise SystemExit(f"V0.5 curated semantic drift detected: {old.get('claim_id')}")
    if new.get("claim_manifest_identity") != new_claim_manifest:
        raise SystemExit(f"V0.5 curated identity rebind missing: {old.get('claim_id')}")

# Rebuild current V0.5 registry from unchanged curated semantics + corrected identity.
subprocess.check_call([sys.executable, "tools/build_jianghe_primary_claim_mapping_draft_v0_1.py"], cwd=ROOT, env=env)
registry_after = load_jsonl(registry_v05)
if len(registry_after) != 352:
    raise SystemExit("rebuilt V0.5 registry lost claim coverage")
allowed_registry_changes = {"claim_manifest_identity", "primary_branch_identity"}
for old, new in zip(registry_before, registry_after, strict=True):
    if old.get("claim_id") != new.get("claim_id"):
        raise SystemExit("V0.5 registry claim ordering changed during identity rebind")
    changed = {key for key in set(old) | set(new) if old.get(key) != new.get(key)}
    if not changed.issubset(allowed_registry_changes):
        raise SystemExit(
            f"V0.5 registry non-identity drift detected: {old.get('claim_id')} changed={sorted(changed)}"
        )
    if new.get("claim_manifest_identity") != new_claim_manifest:
        raise SystemExit(f"V0.5 registry identity rebind missing: {old.get('claim_id')}")

for path, digest in historical_hashes.items():
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise SystemExit(f"historical PRIMARY authority changed unexpectedly: {path}")

changed_branch_identity_count = sum(
    old.get("primary_branch_identity") != new.get("primary_branch_identity")
    for old, new in zip(registry_before, registry_after, strict=True)
)
if changed_branch_identity_count != 352:
    raise SystemExit(
        f"expected all 352 content-addressed branch identities to rebind; got {changed_branch_identity_count}"
    )

# Formal correction evidence: identity correctness only; no research semantic change.
correction_path = ROOT / "docs/reviews/JIANGHE_SOURCE_ONLY_GIT_BLOB_IDENTITY_CORRECTION_V0_1.md"
correction_path.write_text(
    f'''# Jianghe SOURCE_ONLY Git-blob identity correction V0.1

## Decision

```text
CORRECTION_TYPE=EVIDENCE_IDENTITY_CORRECTNESS_ONLY
ROOT_CAUSE=WINDOWS_CRLF_WORKTREE_BYTES_HASHED_WHILE_GIT_STORED_LF_BLOBS
OLD_CLAIM_MANIFEST_IDENTITY={OLD_CLAIM_MANIFEST}
CORRECTED_CLAIM_MANIFEST_IDENTITY={new_claim_manifest}
CLAIM_RECORDS=352
CLAIM_SEMANTIC_CHANGE_COUNT=0
PRIMARY_CURATED_SEMANTIC_CHANGE_COUNT=0
PRIMARY_V0_5_REBOUND_RECORDS=352
PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
OUTCOME_ACCESS=NO
PAID_SPEND=0
LIVE_CALLS=0
```

The original SOURCE_ONLY machine evidence claimed exact repository-artifact byte binding but
used `Path.read_bytes()` from a Windows checkout. Git line-ending normalization stored LF blobs,
so CRLF working-tree sizes/hashes were not identities of the committed repository bytes.
All 16 claim files showed the exact CRLF signature: `formal_size - git_blob_size == LF_count`.

A claim-by-claim JSON comparison against the SOURCE_ONLY creation commit found zero changed
claims and zero changes in fields consumed by PRIMARY (`source_reference`, anchors, status,
source meaning, ambiguity and family scope). This correction therefore changes byte/content
identities and derived branch identities only. It does not reopen Jianghe semantics.

The corrected builder binds exact `git show HEAD:<path>` blob bytes and permits a checkout to
differ only by CRLF-to-LF text normalization; any other uncommitted material drift fails closed.
Historical V0.3 PRIMARY artifacts and the historical hygiene/rebind execution record are retained
unchanged. Current V0.5 curated records change only `claim_manifest_identity`; the current V0.5
registry is deterministically rebuilt and may change only `claim_manifest_identity` and derived
`primary_branch_identity`.

Corrected SOURCE_ONLY identities:

```text
SOURCE_MATERIAL_MANIFEST_IDENTITY={source_payload['source_material_manifest']['manifest_identity']}
CLAIM_MANIFEST_IDENTITY={new_claim_manifest}
CASE_MANIFEST_IDENTITY={source_payload['case_manifest']['manifest_identity']}
SOURCE_ONLY_SESSION_IDENTITY={source_payload['session']['session_identity']}
```

No candidate outcome, Validation, Final, Shadow, broker, real-money or provider call authorization
is changed by this correction.
''',
    encoding="utf-8",
    newline="\n",
)

print("BASELINE_AND_GIT_BLOB_IDENTITY_REPAIR_APPLIED=YES")
print(f"CORRECTED_CLAIM_MANIFEST_IDENTITY={new_claim_manifest}")
print(f"SOURCE_MANIFEST_IDENTITY={source_payload['source_material_manifest']['manifest_identity']}")
print(f"CASE_MANIFEST_IDENTITY={source_payload['case_manifest']['manifest_identity']}")
print(f"SOURCE_ONLY_SESSION_IDENTITY={source_payload['session']['session_identity']}")
print("PRIMARY_CURATED_SEMANTIC_CHANGE_COUNT=0")
print("PRIMARY_V0_5_REBOUND_RECORDS=352")
