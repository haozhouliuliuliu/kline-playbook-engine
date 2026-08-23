from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src" / "jianghe_prespend_runtime.py"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one exact replacement, found {count}: {old[:120]!r}")
    path.write_text(text.replace(old, new), encoding="utf-8", newline="\n")


replace_once(
    RUNTIME,
    '''        payload["model_context_identity"] = self.model_payload()["model_context_identity"]
        if include_identity:
            payload["selected_context_identity"] = self.identity
        return payload
''',
    '''        payload["model_context_identity"] = (
            self.model_payload()["model_context_identity"]
            if self.fixture_id is not None and self.selection_basis_identity is not None
            else None
        )
        if include_identity:
            payload["selected_context_identity"] = self.identity
        return payload
''',
)

print("prespend context artifact layering v07 staged")
