"""生成江河 V1.1 SOURCE_ONLY verification 的机器可读证据。"""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.jianghe_source_only_verification import build_verification_payload


OUTPUT = ROOT / "docs" / "evidence" / "JIANGHE_V1_1_SOURCE_ONLY_VERIFICATION_V0_1.json"


def main() -> None:
    payload = build_verification_payload()
    OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
