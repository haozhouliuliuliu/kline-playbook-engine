from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src" / "jianghe_prespend_runtime.py"

text = RUNTIME.read_text(encoding="utf-8")
marker = "__all__ = ["
if text.count(marker) != 1:
    raise SystemExit(f"expected exactly one __all__ marker, found {text.count(marker)}")

exports = '''__all__ = [
    "BUDGET_LEDGER_VERSION", "BudgetGuardError", "CanonicalStructuredObservationArtifact",
    "CnyBudgetLedger", "CURRENT_ACTIVE_KNOWLEDGE_PACK_IDENTITY", "CURRENT_PRIMARY_MANIFEST_IDENTITY",
    "DEEPSEEK_VISION_SPEC", "DomesticProviderTransport", "FxAuthority", "HARD_PROJECT_CAP_CNY",
    "current_context_selection_policy_identity", "load_current_repository_rate_card",
    "load_owner_paid_call_authorization", "HttpResponse", "IMPLEMENTATION_TARGET_SPECS",
    "InvocationBounds", "KIMI_K3_SPEC", "MINIMAX_M3_SPEC", "PaidCallAuthorization",
    "PaidCallNotAuthorizedError", "ProviderInvocationEvidence", "ProviderResponseError",
    "ProviderSpec", "ProviderTransportError", "ProviderUsage", "RateCard",
    "SelectedContextDocument", "SelectedJiangheContextArtifact", "SpendEligibleJiangheRequest",
    "TEXT_INPUT_BOUND_POLICY_VERSION", "VisualInputArtifact",
]
'''

RUNTIME.write_text(text[: text.index(marker)] + exports, encoding="utf-8", newline="\n")
print("applied prespend final fixes v05")
