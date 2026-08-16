"""Deterministic acquisition manifest for the pilot historical dataset.

The manifest binds, per concrete-contract/date partition, every non-secret
fact required to reproduce and audit an acquired raw artifact.  Ordering is
deterministic and repeated construction over identical raw artifacts produces
an identical manifest identity.

This module is vendor-neutral and contains no credentials or raw market data.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

import re

_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def canonical_hash(value: Any) -> str:
    """Deterministic JSON-stable SHA256 (matches src.historical_data style)."""
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


def _required_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")


@dataclass(frozen=True)
class ManifestPartition:
    """One acquired concrete-contract/date partition (no secrets, no raw data)."""

    provider: str
    api_version: str
    contract: str
    exchange: str
    granularity_seconds: int
    requested_start: datetime
    requested_end: datetime
    returned_start: datetime
    returned_end: datetime
    retrieved_at: datetime
    raw_bytes: int
    raw_sha256: str
    request_identity: str
    normalizer_identity: str
    session_metadata_version: str
    data_version_id: str
    normalized_batch_id: str
    quality_status: str

    def __post_init__(self) -> None:
        for value, name in (
            (self.provider, "manifest provider"),
            (self.api_version, "manifest api version"),
            (self.contract, "manifest contract"),
            (self.exchange, "manifest exchange"),
            (self.request_identity, "manifest request identity"),
            (self.normalizer_identity, "manifest normalizer identity"),
            (self.session_metadata_version, "manifest session metadata version"),
            (self.data_version_id, "manifest data-version identity"),
            (self.normalized_batch_id, "manifest normalized batch identity"),
            (self.quality_status, "manifest quality status"),
        ):
            _required_text(value, name)
        for value, name in (
            (self.retrieved_at, "manifest retrieval timestamp"),
            (self.requested_start, "manifest requested coverage start"),
            (self.requested_end, "manifest requested coverage end"),
            (self.returned_start, "manifest returned coverage start"),
            (self.returned_end, "manifest returned coverage end"),
        ):
            if value.tzinfo is None:
                raise ValueError(f"{name} must be timezone-aware")
        if self.requested_end <= self.requested_start:
            raise ValueError("requested coverage end must follow its start")
        if self.returned_end <= self.returned_start:
            raise ValueError("returned coverage end must follow its start")
        if type(self.granularity_seconds) is not int or self.granularity_seconds <= 0:
            raise ValueError("manifest granularity must be positive whole seconds")
        if type(self.raw_bytes) is not int or self.raw_bytes < 0:
            raise ValueError("manifest raw byte size must be a non-negative integer")
        if not _SHA256.fullmatch(self.raw_sha256):
            raise ValueError("manifest raw SHA256 must be 64 lowercase hexadecimal characters")

    @property
    def partition_key(self) -> tuple:
        return (self.contract, self.granularity_seconds, self.requested_start.isoformat())

    def identity(self) -> str:
        return canonical_hash(
            {
                "provider": self.provider,
                "api_version": self.api_version,
                "contract": self.contract,
                "exchange": self.exchange,
                "granularity_seconds": self.granularity_seconds,
                "requested_coverage_start": self.requested_start.isoformat(),
                "requested_coverage_end": self.requested_end.isoformat(),
                "returned_coverage_start": self.returned_start.isoformat(),
                "returned_coverage_end": self.returned_end.isoformat(),
                "retrieved_at": self.retrieved_at.isoformat(),
                "raw_bytes": self.raw_bytes,
                "raw_sha256": self.raw_sha256,
                "request_identity": self.request_identity,
                "normalizer_identity": self.normalizer_identity,
                "session_metadata_version": self.session_metadata_version,
                "data_version_id": self.data_version_id,
                "normalized_batch_id": self.normalized_batch_id,
                "quality_status": self.quality_status,
            }
        )

    def to_dict(self) -> dict:
        return {
            "provider": self.provider,
            "api_version": self.api_version,
            "contract": self.contract,
            "exchange": self.exchange,
            "granularity_seconds": self.granularity_seconds,
            "requested_coverage_start": self.requested_start.isoformat(),
            "requested_coverage_end": self.requested_end.isoformat(),
            "returned_coverage_start": self.returned_start.isoformat(),
            "returned_coverage_end": self.returned_end.isoformat(),
            "retrieved_at": self.retrieved_at.isoformat(),
            "raw_bytes": self.raw_bytes,
            "raw_sha256": self.raw_sha256,
            "request_identity": self.request_identity,
            "normalizer_identity": self.normalizer_identity,
            "session_metadata_version": self.session_metadata_version,
            "data_version_id": self.data_version_id,
            "normalized_batch_id": self.normalized_batch_id,
            "quality_status": self.quality_status,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ManifestPartition":
        return cls(
            provider=data["provider"],
            api_version=data["api_version"],
            contract=data["contract"],
            exchange=data["exchange"],
            granularity_seconds=data["granularity_seconds"],
            requested_start=datetime.fromisoformat(data["requested_coverage_start"]),
            requested_end=datetime.fromisoformat(data["requested_coverage_end"]),
            returned_start=datetime.fromisoformat(data["returned_coverage_start"]),
            returned_end=datetime.fromisoformat(data["returned_coverage_end"]),
            retrieved_at=datetime.fromisoformat(data["retrieved_at"]),
            raw_bytes=data["raw_bytes"],
            raw_sha256=data["raw_sha256"],
            request_identity=data["request_identity"],
            normalizer_identity=data["normalizer_identity"],
            session_metadata_version=data["session_metadata_version"],
            data_version_id=data["data_version_id"],
            normalized_batch_id=data["normalized_batch_id"],
            quality_status=data["quality_status"],
        )


@dataclass(frozen=True)
class DatasetManifest:
    schema_version: str
    partitions: tuple[ManifestPartition, ...]

    def __post_init__(self) -> None:
        _required_text(self.schema_version, "manifest schema version")
        if any(not isinstance(item, ManifestPartition) for item in self.partitions):
            raise ValueError("manifest partitions must be ManifestPartition values")
        if not self.partitions:
            raise ValueError("manifest requires at least one partition")
        ordered = tuple(sorted(self.partitions, key=lambda p: p.partition_key))
        if any(
            left.partition_key >= right.partition_key
            for left, right in zip(ordered, ordered[1:])
        ):
            raise ValueError("manifest partitions must be unique and deterministically ordered")
        object.__setattr__(self, "partitions", ordered)

    @property
    def partition_identities(self) -> tuple[str, ...]:
        return tuple(item.identity() for item in self.partitions)

    def identity(self) -> str:
        return canonical_hash(
            {
                "schema_version": self.schema_version,
                "partitions": list(self.partition_identities),
            }
        )

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "manifest_identity": self.identity(),
            "partitions": [item.to_dict() for item in self.partitions],
        }

    def to_json_bytes(self) -> bytes:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2).encode("utf-8")

    @classmethod
    def from_entries(cls, schema_version: str, partitions: Any) -> "DatasetManifest":
        if isinstance(partitions, (list, tuple)):
            return cls(schema_version, tuple(partitions))
        raise ValueError("manifest partitions must be an iterable")

    @classmethod
    def load(cls, path: Path) -> "DatasetManifest":
        """Load and verify a manifest; fail closed on corruption."""
        data = json.loads(Path(path).read_bytes().decode("utf-8"))
        if data.get("schema_version") is None:
            raise ValueError("manifest file has no schema version")
        partitions = tuple(ManifestPartition.from_dict(item) for item in data["partitions"])
        manifest = cls(data["schema_version"], partitions)
        recorded = data.get("manifest_identity")
        if recorded is not None and recorded != manifest.identity():
            raise ValueError("manifest identity does not match its recorded value")
        return manifest

    @classmethod
    def save(cls, manifest: "DatasetManifest", path: Path) -> None:
        path.write_bytes(manifest.to_json_bytes())
