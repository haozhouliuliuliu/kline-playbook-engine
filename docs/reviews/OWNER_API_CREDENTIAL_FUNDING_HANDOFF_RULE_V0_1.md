# OWNER API CREDENTIAL / FUNDING HANDOFF RULE V0.1

Status: `OWNER_APPROVED_COLLABORATION_RULE`
Date: 2026-08-24

## Rule

Whenever project execution reaches a point where the Owner must manually provide an API credential, create/select an API key, inspect account balance, or perform a new recharge/top-up/payment action, the project brain must stop at the Owner gate and provide:

1. the exact provider/account action required;
2. the provider's current official website/control-panel entry URL, verified from first-party sources at that time;
3. the exact minimum information the Owner needs to enter or click;
4. for any new recharge/top-up/payment, the exact amount requested and the reason it is required before any funding action;
5. an explicit statement that credentials must not be pasted into GitHub, evidence artifacts, logs, or chat unless the product provides a designated secure credential-entry surface.

Do not tell the Owner merely to “go to the provider platform” or make the Owner search for the correct official site.

## Current official platform roots

These are current as of 2026-08-24 and must be re-verified when actually used:

- Kimi / Moonshot API Platform: `https://platform.kimi.ai/`
- DeepSeek API Platform: `https://platform.deepseek.com/`
- MiniMax API Platform: `https://platform.minimaxi.com/`

## Funding boundary

Existing funded balance or granted credits may be used only within the already-authorized project funnel. Any new recharge, prepaid purchase, subscription, or payment remains an Owner external-action gate and requires the exact requested amount before action.
