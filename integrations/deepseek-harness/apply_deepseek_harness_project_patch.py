from __future__ import annotations

from pathlib import Path
import sys


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: apply_deepseek_harness_project_patch.py <harness-root>")

    root = Path(sys.argv[1])
    target = root / "packages/llm/llm-deepseek/src/adapter.ts"
    text = target.read_text(encoding="utf-8")

    old_counter = "    let representation: 'file' | 'base64' = 'file'\n    let fileAttempt = 0\n"
    new_counter = "    let representation: 'file' | 'base64' = 'file'\n"
    if text.count(old_counter) != 1:
        raise RuntimeError("pinned Harness adapter counter shape drifted")
    text = text.replace(old_counter, new_counter, 1)

    old_retry = """          if (fileAttempt === 0) {
            fileAttempt += 1
            continue
          }
"""
    new_retry = """          // kline-playbook-engine policy: one chat-completions request per
          // adapter stream() call. Keep stale mapping invalidation so a later
          // explicit project request may upload a fresh image, but never issue
          // a hidden second model request inside the current call.
"""
    if text.count(old_retry) != 1:
        raise RuntimeError("pinned Harness stale-file retry shape drifted")
    text = text.replace(old_retry, new_retry, 1)

    if "fileAttempt" in text:
        raise RuntimeError("hidden stale-file retry state remains after project patch")

    target.write_text(text, encoding="utf-8")
    print("PROJECT_HARNESS_PATCH=APPLIED__NO_HIDDEN_STALE_CHAT_RETRY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
