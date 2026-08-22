# 江河交易员 Strategy Families V1.1 — Exhaustive Second-Pass Reconciled

This is a source-faithful research specification, not a machine strategy or trading authorization. The exhaustive second pass does **not** justify a fifth independent mechanism. Core Families remain A–D.

## JH-FAMILY-A — 趋势关键位回调延续

| field | V1.1 source-faithful specification |
|---|---|
| applicable_market | Confirmed trend / post-break continuation. Strong established trends may only offer shallow pullbacks; weaker trends more often require deeper, clearer pullbacks. |
| preconditions | Trend/timeframe is explicit; prior directional leg has sufficient quality; counter-move is weaker than the prior push and does not fully negate it. 006/008/024/025/028 add strong source detail. |
| location | Trend defense/firing/origin areas, key swing points, post-break retest, shallow pullback before second push. |
| trigger | Trend-direction recovery after weak pullback; confirmation close/conditional break; two-push failure against the pullback; lower-TF actual reaction where used. |
| no_trade | Deep/accelerating counter-move, old trend no longer stable, poor location/space, no actual confirmation, chase entry with bad stop/RR. |
| stop_or_invalidation | Pullback/entry structural extreme, defense point loss, or sustained counter follow-through that invalidates the trend premise. |
| management | Dynamic new structure/defense, key-location/space or order-mode-specific fixed target. Early-trend vs non-early exit sensitivity differs. |
| position_risk | Fixed tolerated-loss / stop-distance sizing is compatible; quality/score/confluence/state may reduce size. Planned additions are source-local, not universal. |
| timeframes | Higher/main TF sets trend/location; lower TF can refine actual trigger. Every TF has its own structure. |
| source-local numeric rules | V024 ABC local rules and planned-add limits remain scoped; V019 1:1 is a temporal personal baseline, not universal. |
| human_discretion | Trend stage, pullback depth, relative strength, key zones, remaining space. |
| machine gaps | Unified strong/weak thresholds, stage classifier, key-zone algorithm, universal risk formula. |

## JH-FAMILY-B — 趋势衰弱反转 / 高周期回调

| field | V1.1 source-faithful specification |
|---|---|
| applicable_market | Old trend/leg is damaged, late, unable to continue, or price reaches a high-value HTF area where a lower-TF counter opportunity may form. |
| preconditions | Old direction first weakens or loses continuation; one counter candle is insufficient; actual new-direction takeover/follow-through is still required. |
| location | HTF key/reference/defense areas, prior trend defense, high-value range boundary. |
| trigger | Failure to make new extreme + defense break, failed pushes, counter engulf/acceleration, or lower-TF structural reversal after HTF location. |
| no_trade | Intact strong trend, first counter bar only, old direction weak but new direction lacks burst/follow-through, location without lower-TF signal. |
| stop_or_invalidation | New direction fails to continue, old direction resumes, structure opposite side. |
| management | Context/order-mode based; a short-term counter order that stalls can be actively closed. |
| position_risk | Left-side/imperfect/low-score variants can be light; no universal percentage. |
| timeframes | HTF supplies context/location; actual execution is read on the chosen lower/main TF. Same-TF internal structure alone is not entry permission. |
| human_discretion | Degree of damage/weakening, takeover quality, “second battle” resolution. |
| machine gaps | Reversal-stage classifier, acceleration threshold, universal risk adjustment. |

## JH-FAMILY-C — 确认突破

| field | V1.1 source-faithful specification |
|---|---|
| applicable_market | Real displacement from structure/range, especially strong/imbalance start phase. |
| preconditions | Price leaves old space; breakout has directional quality; follow-through/lower-TF continuation should not quickly negate the break. |
| location | External range/structure boundary, firing/defense point, post-break retest. |
| trigger | Break + follow-through; lower-TF second confirmation/continuation; “crushing” quality is a positive source concept. |
| no_trade | Wick-only test, rapid return to old space, no second confirmation, poor follow-through, exhausted/consumptive break when quality is insufficient. |
| stop_or_invalidation | Re-entry into old space, failed structure, opposite structural side. |
| management | Once breakout becomes stable trend, management can transition to A-style continuation/structure tracking. |
| position_risk | Tolerated-loss sizing; staged entries/additions only under source-specific new confirmation. |
| timeframes | Outer/main TF identifies break; lower TF confirms where used. Lower-TF structure must be actually read on that TF. |
| human_discretion | Break distance, follow-through, crushing vs consumptive quality, retest strength. |
| machine gaps | Quantitative break/follow thresholds and quality scoring. |

## JH-FAMILY-D — 震荡边界反转

| field | V1.1 source-faithful specification |
|---|---|
| applicable_market | Confirmed range/wide range where neither side sustains dominance; weak trend and range can overlap if they grant the same direction. |
| preconditions | Focus on external high-value upper/lower boundaries; middle is not main-TF swing permission. |
| location | External range highs/lows or source-defined outer gray/key zones. |
| trigger | Second/multiple push fails to make a new extreme, counter strength appears, engulf/rejection/strength conversion after boundary test. |
| no_trade | Middle area, boundary arrival without confirmation, first counter candle only, or genuine breakout with sustained follow-through. |
| stop_or_invalidation | Real break of outer boundary + continuation; structure opposite side. |
| management | Often proactive; opposite boundary is not mandatory target. Manage actual available space, momentum/stall, and newly formed structures. |
| position_risk | Several source-era examples use lighter/0.5x risk; second pass confirms this is source-scoped, not a universal permanent formula. |
| timeframes | Outer/main TF defines range; smaller TF can refine trigger. Mid-range lower-TF scalp is a separate execution scale, not permission for main-TF swing. |
| human_discretion | Outer boundary placement, second-push quality, internal weak-bull/weak-bear bias, active-exit timing. |
| machine gaps | Boundary algorithm, bias threshold, universal D sizing, exit formula. |

## Mechanism switching / overlap

- D genuine breakout -> C.
- C confirmed breakout that becomes a stable trend -> A continuation can take over on later pullbacks.
- B only becomes active after old-direction weakening/damage plus new-direction evidence; it is not blind reversal against an intact trend.
- Weak-trend and range labels may overlap when both produce the same directional permission; action logic is more important than forcing a mutually exclusive label.

## NON-FAMILY — SCALPING_EXECUTION_MODE

Still `NON_CORE_EXECUTION_MODE`. V040/V043/V067/V073/V074/V084/V086 show teachable scalp mechanics, but V074 explicitly anchors the trader's routine focus to day swing/micro-swing. No Family E.

## AUXILIARY_TOOL_USAGE

Price/K-line/structure/location/momentum remain core. MA/EMA appears in V020/V021/V061/V069/V078 as optional auxiliary evidence. Early V006 “naked K / no indicator” teaching is preserved chronologically; later auxiliary use does not create an indicator family.
