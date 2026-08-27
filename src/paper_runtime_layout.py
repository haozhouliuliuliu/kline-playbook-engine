"""Deterministic local PAPER runtime-state layout under an explicit state root.

OFFLINE ONLY. This module owns *where* durable PAPER runtime state lives and
how a restart safely reopens it. It creates no database framework and performs
no network/provider/credential/account/order action.

Layout invariants
-----------------
- All paths are derived deterministically from the state root (stable relative
  names), so first startup, restart and offline rehearsal agree.
- First startup may create missing directories and a fresh runtime-metadata
  marker; it never deletes or overwrites existing durable state.
- Restart reopens the existing durable state. If the metadata marker is missing
  while durable state already exists, or the recorded identity disagrees with
  the requested identity, the layout fails closed (``PaperRuntimeIdentityMismatch``)
  rather than silently starting over evidence.
- Windows path handling is supported through ``pathlib.Path`` and normalized
  absolute paths in the identity hash.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

PAPER_RUNTIME_LAYOUT_SCHEMA_VERSION = "KPE_PAPER_RUNTIME_LAYOUT_V0_1"


def _canonical_json(value: object) -> str:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False
    )


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be non-empty text")
    return value.strip()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


class PaperRuntimeLayoutError(RuntimeError):
    """Base class for PAPER runtime layout failures."""


class PaperRuntimeIdentityMismatch(PaperRuntimeLayoutError):
    """The state root is bound to a different runtime identity than requested."""


@dataclass(frozen=True)
class PaperRuntimeLayout:
    """One deterministic runtime-state layout under an explicit state root."""

    state_root: str | Path
    trader_identity: str
    concrete_contract_id: str
    config_identity: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "state_root", Path(self.state_root).expanduser())
        object.__setattr__(self, "trader_identity", _text(self.trader_identity, "paper layout trader identity"))
        object.__setattr__(
            self, "concrete_contract_id", _text(self.concrete_contract_id, "paper layout concrete contract")
        )
        object.__setattr__(self, "config_identity", _text(self.config_identity, "paper layout config identity"))

    # ------------------------------------------------------------------ paths

    @property
    def order_journal_path(self) -> Path:
        """Durable paper order journal (submit-attempt idempotency)."""
        return self.state_root / "journals" / "paper_order_journal.sqlite3"

    @property
    def wake_journal_path(self) -> Path:
        """Durable paper wake journal (cognition dispatch idempotency)."""
        return self.state_root / "journals" / "paper_wake_journal.sqlite3"

    @property
    def trader_store_path(self) -> Path:
        """Persistent trader state / working-memory store."""
        return self.state_root / "trader" / "trader_store.sqlite3"

    @property
    def runtime_metadata_path(self) -> Path:
        """Runtime metadata marker binding this state root to an identity."""
        return self.state_root / "runtime" / "runtime_metadata.json"

    @property
    def causal_checkpoint_path(self) -> Path:
        """Causal-context checkpoint for deterministic restart continuity."""
        return self.state_root / "runtime" / "causal_checkpoint.json"

    @property
    def directories(self) -> tuple[Path, ...]:
        return (
            self.state_root,
            self.state_root / "journals",
            self.state_root / "trader",
            self.state_root / "runtime",
        )

    # ---------------------------------------------------------------- identity

    @property
    def identity(self) -> str:
        """Deterministic identity of the layout binding.

        The normalized absolute state root is included so a moved/copied tree
        is treated as a distinct runtime identity and fails closed on reopen.
        """
        return _hash(
            {
                "schema_version": PAPER_RUNTIME_LAYOUT_SCHEMA_VERSION,
                "state_root": str(self.state_root.resolve()),
                "trader_identity": self.trader_identity,
                "concrete_contract_id": self.concrete_contract_id,
                "config_identity": self.config_identity,
            }
        )

    def _metadata_document(self) -> dict[str, object]:
        return {
            "schema_version": PAPER_RUNTIME_LAYOUT_SCHEMA_VERSION,
            "layout_identity": self.identity,
            "state_root": str(self.state_root.resolve()),
            "trader_identity": self.trader_identity,
            "concrete_contract_id": self.concrete_contract_id,
            "config_identity": self.config_identity,
            "created_at": _now_iso(),
        }

    # -------------------------------------------------------------- lifecycle

    def durable_state_exists(self) -> bool:
        """Whether any durable runtime state already exists under the root."""
        for path in (
            self.order_journal_path,
            self.wake_journal_path,
            self.trader_store_path,
            self.causal_checkpoint_path,
        ):
            if path.exists():
                return True
        return self.runtime_metadata_path.exists()

    def ensure_initialized(self) -> None:
        """First-startup-safe initialization.

        Creates missing directories. If no runtime metadata marker exists yet,
        writes a fresh one only when no other durable state is present (so we
        never claim a fresh identity over existing evidence). If the marker
        already exists, verifies the recorded identity matches (fail closed).
        """
        for directory in self.directories:
            directory.mkdir(parents=True, exist_ok=True)
        if not self.runtime_metadata_path.exists():
            if self.durable_state_exists():
                raise PaperRuntimeIdentityMismatch(
                    "PAPER_RUNTIME_LAYOUT_DURABLE_STATE_WITHOUT_METADATA"
                )
            self._write_metadata()
            return
        self.reopen()

    def reopen(self) -> None:
        """Reopen an existing layout, refusing unsafe identity mismatch.

        Requires the runtime-metadata marker to exist and to agree with the
        requested identity. If it is missing while durable state exists, or its
        recorded identity disagrees, this raises ``PaperRuntimeIdentityMismatch``
        and never silently wipes/overwrites the existing state.
        """
        if not self.runtime_metadata_path.exists():
            if self.durable_state_exists():
                raise PaperRuntimeIdentityMismatch(
                    "PAPER_RUNTIME_LAYOUT_DURABLE_STATE_WITHOUT_METADATA"
                )
            raise PaperRuntimeIdentityMismatch("PAPER_RUNTIME_LAYOUT_METADATA_MISSING")
        try:
            payload = json.loads(self.runtime_metadata_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            raise PaperRuntimeLayoutError("PAPER_RUNTIME_LAYOUT_METADATA_UNREADABLE") from error
        if payload.get("schema_version") != PAPER_RUNTIME_LAYOUT_SCHEMA_VERSION:
            raise PaperRuntimeIdentityMismatch("PAPER_RUNTIME_LAYOUT_SCHEMA_MISMATCH")
        recorded = payload.get("layout_identity")
        if not isinstance(recorded, str) or recorded != self.identity:
            raise PaperRuntimeIdentityMismatch("PAPER_RUNTIME_LAYOUT_IDENTITY_MISMATCH")
        if payload.get("trader_identity") != self.trader_identity:
            raise PaperRuntimeIdentityMismatch("PAPER_RUNTIME_LAYOUT_TRADER_IDENTITY_MISMATCH")
        if payload.get("concrete_contract_id") != self.concrete_contract_id:
            raise PaperRuntimeIdentityMismatch("PAPER_RUNTIME_LAYOUT_CONTRACT_IDENTITY_MISMATCH")

    # ---------------------------------------------------------------- metadata

    def _write_metadata(self) -> None:
        self.runtime_metadata_path.parent.mkdir(parents=True, exist_ok=True)
        # Only ever write a fresh marker; never overwrite an existing one.
        if self.runtime_metadata_path.exists():
            return
        self.runtime_metadata_path.write_text(
            _canonical_json(self._metadata_document()) + "\n",
            encoding="utf-8",
        )

    def write_causal_checkpoint(self, payload: object) -> None:
        """Persist a causal-context checkpoint for restart continuity.

        This is runtime state (not immutable evidence); it is replaced on a
        clean shutdown so a restart reopens the most recent durable context.
        """
        self.causal_checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        self.causal_checkpoint_path.write_text(
            _canonical_json(payload) + "\n", encoding="utf-8"
        )

    def read_causal_checkpoint(self) -> dict[str, object]:
        """Load a persisted causal checkpoint, or fail closed when absent/invalid."""
        if not self.causal_checkpoint_path.exists():
            raise PaperRuntimeLayoutError("PAPER_RUNTIME_LAYOUT_CHECKPOINT_MISSING")
        try:
            payload = json.loads(self.causal_checkpoint_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            raise PaperRuntimeLayoutError("PAPER_RUNTIME_LAYOUT_CHECKPOINT_UNREADABLE") from error
        if not isinstance(payload, dict):
            raise PaperRuntimeLayoutError("PAPER_RUNTIME_LAYOUT_CHECKPOINT_INVALID")
        return payload


__all__ = [
    "PAPER_RUNTIME_LAYOUT_SCHEMA_VERSION",
    "PaperRuntimeIdentityMismatch",
    "PaperRuntimeLayout",
    "PaperRuntimeLayoutError",
]
