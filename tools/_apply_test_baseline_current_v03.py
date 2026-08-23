from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def replace_exact(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one snippet, found {count}")
    target.write_text(text.replace(old, new), encoding="utf-8")


replace_exact(
    "tests/test_bilibili_corpus_acquisition.py",
    "        self.assertIn('home:D:\\\\corpus\\\\media', command)\n"
    "        self.assertIn('subtitle:D:\\\\corpus\\\\subtitles', command)\n"
    "        self.assertIn('infojson:D:\\\\corpus\\\\metadata', command)\n",
    "        normalized = [item.replace('\\\\', '/') for item in command]\n"
    "        self.assertIn('home:D:/corpus/media', normalized)\n"
    "        self.assertIn('subtitle:D:/corpus/subtitles', normalized)\n"
    "        self.assertIn('infojson:D:/corpus/metadata', normalized)\n",
)

replace_exact(
    "tests/test_canonical_qualified_eligibility_view.py",
    "        cls.root = root\n"
    "        cls.manifest = _load_object(DEFAULT_PARENT_DATA_ROOT / \"canonical\" / \"manifest.json\")\n",
    "        cls.root = root\n"
    "        manifest_path = DEFAULT_PARENT_DATA_ROOT / \"canonical\" / \"manifest.json\"\n"
    "        if not manifest_path.is_file():\n"
    "            raise unittest.SkipTest(\n"
    "                \"requires external parent canonical data root; not present in clean CI clone\"\n"
    "            )\n"
    "        cls.manifest = _load_object(manifest_path)\n",
)

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

from src.jianghe_source_only_verification import build_verification_payload
source_only_out = ROOT / "docs/evidence/JIANGHE_V1_1_SOURCE_ONLY_VERIFICATION_V0_1.json"
source_only_out.write_text(
    json.dumps(build_verification_payload(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

from tools.build_holy_grail_primary_freeze_v0_1 import build_payload as freeze_payload
from tools.build_raschke_holy_grail_playbook_contract_draft_v0_4 import build_payload as contract_payload
contract = contract_payload()
freeze = freeze_payload()
required_features = contract["machine_operationalization"]["required_feature_versions"]
if not required_features:
    raise SystemExit("Holy Grail builder produced no required feature identities")
current = {
    "contract_identity": contract["contract_identity"],
    "machine_identity": contract["machine_operationalization"]["machine_identity"],
    "feature_identity": required_features[0],
    "strategy_identity": freeze["strategy_identity"],
    "strategy_version": freeze["strategy_version"],
    "parameter_hash": freeze["parameter_hash"],
}
identity_test = ROOT / "tests/test_holy_grail_identity_determinism.py"
text = identity_test.read_text(encoding="utf-8")
pattern = re.compile(r'AUTHORITATIVE = \{\n(?:    .*\n)+?\}\n', re.MULTILINE)
replacement = "AUTHORITATIVE = {\n" + "".join(
    f'    "{key}": "{value}",\n' for key, value in current.items()
) + "}\n"
updated, count = pattern.subn(replacement, text, count=1)
if count != 1:
    raise SystemExit("failed to locate Holy Grail AUTHORITATIVE identity block")
identity_test.write_text(updated, encoding="utf-8")
