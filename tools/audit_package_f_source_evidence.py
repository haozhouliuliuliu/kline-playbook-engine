"""PACKAGE_F_SOURCE_EVIDENCE_HARDENING_PREFLIGHT_V0_1 - read-only source-bundle audit.

Read-only inventory that confirms audit finding S-01 for the accepted source
bundles:

- which fields actually compose each bundle's `canonical_bundle_hash`;
- whether any fetched-content byte SHA256 participates in that identity;
- whether the committed `canonical_bundle_hash` recomputes from metadata-only
  fields (bundle_id, retrieval_mode, materials[material_id/url/canonical_title/
  date|publication_date], selection_criteria) using the same canonical JSON+sha256
  scheme as `src/research_firewall.py` and the extraction drivers.

BOUNDARIES (frozen authority, do not violate):
- No production code is imported and no source file is modified.
- No source page is fetched and no historical artifact is rewritten.
- Wave 1 / Wave 2 / Raschke-screen manifests are not present on main; they are
  read from the durable accepted evidence refs (S-03 ref durability, R-PB-01)
  and the accepted screen branch. Holy Grail / NR7 manifests are read from HEAD.
- This audit only reports current facts; it never claims that bytes seen in an
  earlier extraction session are retroactively byte-provable.

Run:
    python -m tools.audit_package_f_source_evidence
"""

from __future__ import annotations

import json
import subprocess
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Accepted source bundles and where each manifest lives. `refs` is tried in
# order until `git show <ref>:<path>` resolves (local branch, remote ref, commit).
BUNDLES = [
    {
        "bundle": "Wave 1 Grimes",
        "bundle_id": "SB-W1-PUBLIC-GRIMES-V1",
        "refs": [
            "evidence/wave1-accepted-raw-20260819",
            "refs/remotes/origin/evidence/wave1-accepted-raw-20260819",
            "b68da256bbc493ac6e1de0fe02b7fde5a0396ddf",
        ],
        "path": "docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_WAVE_1_MANIFEST.json",
        "date_field": "date",
    },
    {
        "bundle": "Wave 2 Steenbarger",
        "bundle_id": "SB-W2-PUBLIC-STEENBARGER-V1",
        "refs": [
            "evidence/wave2-accepted-raw-20260819",
            "refs/remotes/origin/evidence/wave2-accepted-raw-20260819",
            "c0fef50bb3b0f5a97c7bdf472d5a9e2d9339273a",
        ],
        "path": "docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_WAVE_2_STEENBARGER_MANIFEST.json",
        "date_field": "date",
    },
    {
        "bundle": "Raschke screen",
        "bundle_id": "SB-RASCHKE-PUBLIC-SCREEN-V1",
        "refs": [
            "parallel/raschke-public-current-data-screen-v01",
            "refs/remotes/origin/parallel/raschke-public-current-data-screen-v01",
            "bd09f9acc4647f9a2240a2f20bf9c919c4d8bb23",
        ],
        "path": "docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_SCREEN_V0_1.json",
        "date_field": "publication_date",
    },
    {
        "bundle": "Raschke Holy Grail",
        "bundle_id": "SB-RASCHKE-HOLY-GRAIL-SEMANTIC-V1",
        "refs": ["HEAD", "main", "origin/main"],
        "path": "docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_HOLY_GRAIL_V0_1.json",
        "date_field": "publication_date",
    },
    {
        "bundle": "Raschke NR7",
        "bundle_id": "SB-RASCHKE-NR7-SEMANTIC-V1",
        "refs": ["HEAD", "main", "origin/main"],
        "path": "docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_NR7_SEMANTIC_V0_1.json",
        "date_field": "publication_date",
    },
]

# Keys that would indicate fetched raw-content byte binding if ever present.
BYTE_BIND_KEYS = ("sha256", "sha-256", "byte", "bytes", "fetched", "raw_content", "file_hash", "pdf_hash", "html_hash", "content_hash")


def _canonical_hash(value: object) -> str:
    """Same canonical JSON+sha256 scheme used by src.research_firewall / drivers."""
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


def _load_manifest(spec: dict) -> tuple[dict | None, str]:
    """Return (manifest, resolved_ref) or (None, error) using the first resolvable ref."""
    for ref in spec["refs"]:
        proc = subprocess.run(
            ["git", "show", f"{ref}:{spec['path']}"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0:
            try:
                return json.loads(proc.stdout), ref
            except json.JSONDecodeError as exc:
                return None, f"JSON decode failed at {ref}: {exc}"
    return None, "no ref resolved"


def _recompute_from_metadata_only(manifest: dict, date_field: str) -> str:
    materials = manifest["materials"]
    return _canonical_hash(
        {
            "bundle_id": manifest["bundle_id"],
            "retrieval_mode": manifest["retrieval_mode"],
            "materials": [
                {k: m[k] for k in ("material_id", "url", "canonical_title", date_field)}
                for m in materials
            ],
            "selection_criteria": manifest["selection_criteria"],
        }
    )


def _byte_binding_keys(manifest: dict) -> list[str]:
    """Any top-level or per-material key that would indicate raw-content byte binding."""
    found: list[str] = []
    sources = [manifest] + manifest.get("materials", [])
    for obj in sources:
        for key in obj:
            if any(needle in key.lower() for needle in BYTE_BIND_KEYS):
                if key not in found:
                    found.append(key)
    return found


def _hash_like_keys(manifest: dict) -> list[str]:
    """Top-level hash keys plus any per-material hash keys (e.g. content_note_hash)."""
    found = [key for key in manifest if "hash" in key.lower()]
    for material in manifest.get("materials", []):
        for key in material:
            if "hash" in key.lower() and key not in found:
                found.append(key)
    return found


def main() -> None:
    print("PACKAGE_F_SOURCE_EVIDENCE_HARDENING_PREFLIGHT_V0_1 - source-bundle identity audit")
    print("=" * 88)
    header = (
        f"{'BUNDLE':<20}{'BUNDLE_ID':<34}{'REF':<34}{'META_ONLY_MATCH':<16}{'BYTE_SHA':<9}"
    )
    print(header)
    print("-" * 88)
    for spec in BUNDLES:
        manifest, ref = _load_manifest(spec)
        if manifest is None:
            print(f"{spec['bundle']:<20}{spec['bundle_id']:<34}UNAVAILABLE: {ref}")
            continue
        recomputed = _recompute_from_metadata_only(manifest, spec["date_field"])
        match = recomputed == manifest["canonical_bundle_hash"]
        byte_keys = _byte_binding_keys(manifest)
        print(
            f"{spec['bundle']:<20}{spec['bundle_id']:<34}{ref[:33]:<34}"
            f"{'MATCH' if match else 'MISMATCH':<16}{'NO' if not byte_keys else ','.join(byte_keys)[:8]:<9}"
        )
        print(f"    canonical_bundle_hash          = {manifest['canonical_bundle_hash']}")
        print(f"    recompute (metadata-only)      = {recomputed}")
        print(f"    hash-like manifest keys        = {_hash_like_keys(manifest)}")
        print(f"    fetched-byte-sha fields        = {byte_keys or 'NONE'}")
        print(f"    materials in identity          = {len(manifest['materials'])}")
        print(
            f"    identity date field           = {spec['date_field']}"
            f"  | raw-retention note present?   = "
            f"{any('raw' in str(v).lower() and 'retain' in str(v).lower() for v in manifest.values())}"
        )
    print("-" * 88)
    print("Interpretation: META_ONLY_MATCH=MATCH proves the canonical bundle identity")
    print("is composed of metadata-only fields; BYTE_SHA=NO confirms no fetched-content")
    print("byte SHA256 is part of any accepted bundle identity (audit S-01).")


if __name__ == "__main__":
    main()
