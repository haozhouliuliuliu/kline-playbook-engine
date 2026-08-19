"""RASCHKE_FREE_PUBLIC_CURRENT_DATA_SCREEN_V1 - official free article acquisition.

Bounded acquisition support for the Raschke free/public current-data screen.

SCOPE:
- Downloads ONLY official Linda Bradford Raschke free-public PDF articles that are
  hosted on her official domain (lindaraschke.net) and are directly reachable
  without authentication, cookies, login, DRM bypass or anti-bot circumvention.
- Extracts text locally with `pypdf` (pure-Python parser; installed only in the
  private isolated probe venv).
- Writes ALL raw/downloaded/extracted artifacts to a local TEMP directory that is
  deliberately OUTSIDE the git repository. Nothing raw is committed. Only this
  small driver script is committed as reproducibility/support code.

HARD BOUNDARIES (frozen authority, do not violate):
- FREE_PUBLIC_UNAUTHENTICATED_FIRST. No purchase, subscription, login, cookie,
  credential, DRM, paywall or anti-bot bypass.
- No YouTube media download (recorded environment = BLOCKED_BY_403). Do not
  circumvent. The official videos are YouTube-hosted only and are therefore NOT
  part of this acquisition; official free article/text material is used instead.
- No candidate outcome / PnL / backtest / indicator search / chart-pattern
  mining. This script only acquires and extracts official source text.
- Do not commit full article copies or raw media. Copyright boundary respected:
  only short excerpts and attributable anchors may appear in project artifacts.

Usage:
    python -m tools.acquire_raschke_official_articles --out <temp_dir>
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import requests

# Official free-public PDFs hosted on the official domain (no auth).
# The WP /2026/01/ /2026/03/ paths are site-rebuild upload folders, NOT
# publication dates; the original publication dates are inside each document and
# are audited separately (SOURCE_EXAMPLE_DATE_STATUS).
OFFICIAL_ARTICLES = [
    {
        "material_id": "SR-V0-M01",
        "canonical_title": "Short Term Trading Strategies",
        "source_publication": "AIQ Opening Bell",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/01/august1997.pdf",
        "filename": "august1997.pdf",
    },
    {
        "material_id": "SR-V0-M02",
        "canonical_title": "The Discerning Trader",
        "source_publication": "Technical Analysis of Stocks & Commodities",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/01/Discerning-trader.pdf",
        "filename": "Discerning-trader.pdf",
    },
    {
        "material_id": "SR-V0-M03",
        "canonical_title": "Trading Style and Daily Market Regimen",
        "source_publication": "Active Trader",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/01/raschke0204.pdf",
        "filename": "raschke0204.pdf",
    },
    {
        "material_id": "SR-V0-M04",
        "canonical_title": "The Rituals of Trading",
        "source_publication": "Active Trader",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/01/rituals.pdf",
        "filename": "rituals.pdf",
    },
    {
        "material_id": "SR-V0-M05",
        "canonical_title": "Traders Toolbox",
        "source_publication": "Active Trader",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/03/raschke_pt2_0304.pdf",
        "filename": "raschke_pt2_0304.pdf",
    },
    {
        "material_id": "SR-V0-M06",
        "canonical_title": "Multi-Market Traders Rule",
        "source_publication": "Financial Trader",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/01/ftrader.pdf",
        "filename": "ftrader.pdf",
    },
    {
        "material_id": "SR-V0-M07",
        "canonical_title": "Trade Trends (interview/profile)",
        "source_publication": "Futures",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/01/upstairs.pdf",
        "filename": "upstairs.pdf",
    },
    {
        "material_id": "SR-V0-M08",
        "canonical_title": "Trading Insights (interview/profile)",
        "source_publication": "Omega Research",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/01/Omega.pdf",
        "filename": "Omega.pdf",
    },
    {
        "material_id": "SR-V0-M09",
        "canonical_title": "Maintain your Mindset Using the Three R's of Positive Thinking",
        "source_publication": "Stock Futures & Options",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/01/SFO_July04.pdf",
        "filename": "SFO_July04.pdf",
    },
    {
        "material_id": "SR-V0-M10",
        "canonical_title": "Who are You? Zoom in on Personal Trading Behavior and Profit from it!",
        "source_publication": "Stock Futures & Options",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/01/SFO_raschke_0803.pdf",
        "filename": "SFO_raschke_0803.pdf",
    },
    {
        "material_id": "SR-V0-M11",
        "canonical_title": "Everything You Wanted to Know about Electronic Trading but were Afraid to Ask",
        "source_publication": "Stock Futures & Options",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/01/Rashke_0406.pdf",
        "filename": "Rashke_0406.pdf",
    },
]


def _extract_pdf_text(pdf_path: Path) -> str:
    from pypdf import PdfReader  # local import; pypdf is a venv-only parsing dep

    reader = PdfReader(str(pdf_path))
    pages = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception as exc:  # page-level parse issues should not abort whole doc
            pages.append(f"[PAGE_EXTRACT_ERROR:{exc}]")
    return "\n\n".join(pages)


def _detect_dates(text: str) -> list[str]:
    patterns = [
        r"\b(January|February|March|April|May|June|July|August|September|October|November|December)"
        r"\s+(\d{1,2})?,?\s+(\d{4})\b",
        r"\b(19|20)\d{2}\b",
    ]
    found: list[str] = []
    for pat in patterns:
        found.extend(re.findall(pat, text) if pat.startswith("\\b(January") else re.findall(pat, text))
    # year-like tokens
    years = re.findall(r"\b(19[8-9]\d|20[0-2]\d)\b", text)
    return years


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, help="temp output dir (outside repo)")
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    pdf_dir = out / "pdf"
    txt_dir = out / "txt"
    pdf_dir.mkdir(exist_ok=True)
    txt_dir.mkdir(exist_ok=True)

    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

    manifest = []
    for m in OFFICIAL_ARTICLES:
        url = m["url"]
        filename = m["filename"]
        record = dict(m)
        try:
            resp = session.get(url, timeout=90)
            record["http_status"] = resp.status_code
            record["content_type"] = resp.headers.get("Content-Type")
            record["bytes"] = len(resp.content)
            if resp.status_code == 200 and resp.content[:5] == b"%PDF-":
                pdf_path = pdf_dir / filename
                pdf_path.write_bytes(resp.content)
                text = _extract_pdf_text(pdf_path)
                txt_path = txt_dir / (Path(filename).stem + ".txt")
                txt_path.write_text(text, encoding="utf-8")
                years = _detect_dates(text)
                record["pdf_pages"] = int(len(resp.content))  # placeholder replaced below
                record["extracted_chars"] = len(text)
                record["detected_years"] = sorted(set(years))
                record["status"] = "OK"
            else:
                record["status"] = "NOT_PDF"
        except Exception as exc:  # noqa: BLE001 - acquisition must not abort the whole batch
            record["status"] = "ERROR"
            record["error"] = repr(exc)
        manifest.append(record)
        print(f"{record['material_id']} {filename} -> {record['status']} ({record.get('bytes', 0)} bytes)")

    # page counts from extracted text (best-effort, per file)
    for record in manifest:
        txt_path = txt_dir / (Path(record["filename"]).stem + ".txt")
        if txt_path.exists():
            record["extracted_chars"] = txt_path.stat().st_size

    manifest_path = out / "acquisition_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"MANIFEST={manifest_path}")


if __name__ == "__main__":
    main()
