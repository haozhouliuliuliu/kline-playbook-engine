"""Bounded, attributable, read-only retrieval over JIANGHE_CANON text artifacts.

This module deliberately has no write path.  Retrieval is deterministic and bounded
by both hit count and returned characters so source truth cannot silently become an
unbounded prompt dump.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Iterable


RETRIEVER_VERSION = "KPE_JIANGHE_CANON_RETRIEVER_V0_1"
DEFAULT_MAX_RESULTS = 6
DEFAULT_MAX_CHARS = 6000
HARD_MAX_RESULTS = 12
HARD_MAX_CHARS = 12000


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _normalize(text: str) -> str:
    return " ".join(text.casefold().split())


def _tokens(query: str) -> tuple[str, ...]:
    # Latin/numeric words plus individual CJK runs.  Exact normalized-substring
    # matching receives the dominant score, so Chinese phrases remain useful even
    # without an external tokenizer.
    raw = re.findall(r"[a-zA-Z0-9_./:-]+|[\u3400-\u9fff]+", query.casefold())
    return tuple(sorted(set(token for token in raw if token)))


def _safe_relative(relative_path: str) -> Path:
    candidate = Path(relative_path)
    if candidate.is_absolute() or ".." in candidate.parts or not candidate.parts:
        raise ValueError("JIANGHE_CANON allowlist paths must be safe relative paths")
    return candidate


@dataclass(frozen=True)
class JiangheCanonHit:
    document_path: str
    document_sha256: str
    start_line: int
    end_line: int
    excerpt: str
    excerpt_sha256: str
    score: int
    retrieval_identity: str

    def to_context_payload(self) -> dict[str, object]:
        return {
            "semantic_class": "JIANGHE_CANON_READ_ONLY_SOURCE_TRUTH",
            "document_path": self.document_path,
            "document_sha256": self.document_sha256,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "excerpt": self.excerpt,
            "excerpt_sha256": self.excerpt_sha256,
            "retrieval_identity": self.retrieval_identity,
        }


@dataclass(frozen=True)
class _Document:
    relative_path: str
    sha256: str
    lines: tuple[str, ...]


class JiangheCanonRetriever:
    """Deterministic lexical retriever over an explicit read-only source allowlist."""

    def __init__(
        self,
        repo_root: str | Path,
        *,
        allowed_paths: Iterable[str],
        max_results: int = DEFAULT_MAX_RESULTS,
        max_chars: int = DEFAULT_MAX_CHARS,
        context_lines: int = 1,
    ) -> None:
        if not 1 <= max_results <= HARD_MAX_RESULTS:
            raise ValueError(f"max_results must be 1..{HARD_MAX_RESULTS}")
        if not 256 <= max_chars <= HARD_MAX_CHARS:
            raise ValueError(f"max_chars must be 256..{HARD_MAX_CHARS}")
        if not 0 <= context_lines <= 3:
            raise ValueError("context_lines must be 0..3")
        self.repo_root = Path(repo_root).resolve()
        self.max_results = max_results
        self.max_chars = max_chars
        self.context_lines = context_lines
        normalized = tuple(sorted(set(str(_safe_relative(path)) for path in allowed_paths)))
        if not normalized:
            raise ValueError("JIANGHE_CANON allowlist cannot be empty")
        if any(not path.startswith("docs/research/jianghe/") for path in normalized):
            raise ValueError("JIANGHE_CANON retrieval is restricted to docs/research/jianghe/")
        self.allowed_paths = normalized
        self._documents = tuple(self._load_document(path) for path in normalized)
        self.identity = _hash(
            {
                "version": RETRIEVER_VERSION,
                "allowed_documents": [(doc.relative_path, doc.sha256) for doc in self._documents],
                "max_results": self.max_results,
                "max_chars": self.max_chars,
                "context_lines": self.context_lines,
                "mutation_capability": "NONE",
            }
        )

    def _load_document(self, relative_path: str) -> _Document:
        path = (self.repo_root / relative_path).resolve()
        try:
            path.relative_to(self.repo_root)
        except ValueError as error:
            raise ValueError("JIANGHE_CANON path escaped repo root") from error
        if not path.is_file():
            raise FileNotFoundError(relative_path)
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        return _Document(relative_path, sha256(raw).hexdigest(), tuple(text.splitlines()))

    def search(self, query: str) -> tuple[JiangheCanonHit, ...]:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("retrieval query must be non-empty")
        normalized_query = _normalize(query)
        tokens = _tokens(query)
        candidates: list[tuple[int, str, int, int, _Document]] = []

        for document in self._documents:
            for index, line in enumerate(document.lines):
                normalized_line = _normalize(line)
                if not normalized_line:
                    continue
                score = 0
                if normalized_query in normalized_line:
                    score += 100
                for token in tokens:
                    if token in normalized_line:
                        score += 10
                if score <= 0:
                    continue
                start = max(0, index - self.context_lines)
                end = min(len(document.lines), index + self.context_lines + 1)
                candidates.append((score, document.relative_path, start, end, document))

        candidates.sort(key=lambda item: (-item[0], item[1], item[2], item[3]))
        results: list[JiangheCanonHit] = []
        used_chars = 0
        seen_ranges: set[tuple[str, int, int]] = set()
        query_sha = sha256(query.encode("utf-8")).hexdigest()

        for score, relative_path, start, end, document in candidates:
            if len(results) >= self.max_results:
                break
            range_key = (relative_path, start, end)
            if range_key in seen_ranges:
                continue
            seen_ranges.add(range_key)
            excerpt = "\n".join(document.lines[start:end]).strip()
            if not excerpt:
                continue
            remaining = self.max_chars - used_chars
            if remaining <= 0:
                break
            if len(excerpt) > remaining:
                excerpt = excerpt[:remaining]
            excerpt_sha = sha256(excerpt.encode("utf-8")).hexdigest()
            retrieval_identity = _hash(
                {
                    "retriever_identity": self.identity,
                    "query_sha256": query_sha,
                    "document_path": relative_path,
                    "document_sha256": document.sha256,
                    "start_line": start + 1,
                    "end_line": end,
                    "excerpt_sha256": excerpt_sha,
                }
            )
            results.append(
                JiangheCanonHit(
                    document_path=relative_path,
                    document_sha256=document.sha256,
                    start_line=start + 1,
                    end_line=end,
                    excerpt=excerpt,
                    excerpt_sha256=excerpt_sha,
                    score=score,
                    retrieval_identity=retrieval_identity,
                )
            )
            used_chars += len(excerpt)
        return tuple(results)


__all__ = [
    "DEFAULT_MAX_CHARS",
    "DEFAULT_MAX_RESULTS",
    "HARD_MAX_CHARS",
    "HARD_MAX_RESULTS",
    "JiangheCanonHit",
    "JiangheCanonRetriever",
    "RETRIEVER_VERSION",
]
