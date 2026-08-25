# Jianghe Stage-A V0.3 three-provider matched capability comparison V0.1

## Decision

```text
COMPARISON_STATUS=COMPLETE
RESULT_SCOPE=MODEL_CAPABILITY_SELECTION_SIGNAL__ONE_MATCHED_FIXTURE
COMMON_EXAM_IDENTITY=7521af411b5df17d27ced17c27a2db34e776ba85a97070f7634e3a197bf3c4e8
QUALITY_RANK_1=DEEPSEEK
QUALITY_RANK_2=KIMI
QUALITY_RANK_3=MINIMAX
STAGE_A_CURRENT_LEADING_PROVIDER=DEEPSEEK
STAGE_A_SELECTION_CONFIDENCE=PROVISIONAL__ONE_MATCHED_FIXTURE
PERMANENTLY_ADOPTED_PROVIDER=NONE
NEXT_PHASE=DOWNLOADED_KLINE_EVALUATION
```

Quality is binding before cost, and cost before latency. DeepSeek leads because it
alone combined the correct `NONE / NO_TRADE / NONE` decision with high visual and
structured fidelity and no invented fixed rule. Kimi is second: its safe conclusion
and breakout logic are strong, but `FAMILY=C` is a material current-setup
misclassification and two detailed data claims are inaccurate. MiniMax is third:
it reached the safe result and was cheapest and fastest, but invented an unfrozen
two-close confirmation rule and made material visual/data errors.

## Same-fixture results

| Provider | Slot | Result | Cost CNY | Latency ms |
|---|---|---|---:|---:|
| DeepSeek | `V0_3:DEEPSEEK:CAPABILITY_MATCHED_002` | `PASS`; `NONE / NO_TRADE / NONE` | 0.110874 | 85,682 |
| MiniMax | `V0_3:MINIMAX:CAPABILITY_MATCHED_001` | `PASS__WITH_MATERIAL_QUALITY_DEFECTS`; `NONE / WAIT / NONE` | 0.1085952 | 36,973 |
| Kimi | `V0_3:KIMI:CAPABILITY_MATCHED_001` | `PASS`; quality status `PASS__WITH_MATERIAL_QUALITY_DEFECTS`; `C / NO_TRADE / NONE` | 0.61002 | 160,533 |

## Comparison matrix

| Dimension | DeepSeek | MiniMax | Kimi |
|---|---|---|---|
| A. JIANGHE_SEMANTIC_FIDELITY | High: correct current `NONE` family and no trade | Medium: safe result, but invented a fixed confirmation rule | Medium: safe result, but misclassified the current family as `C` |
| B. MARKET_STRUCTURE_ACCURACY | High: narrow consolidation after failed sweeps | Medium: failed probe recognized; 1H body description inaccurate | High: range and failed probe correctly identified |
| C. VISUAL_FACT_FIDELITY | High: visual observations agree with the fixture | Low/medium: said all three 1H candle bodies were wide | Medium: overall shape correct; last-ten-close statement inaccurate |
| D. STRUCTURED_DATA_ACCURACY | High: no material governed-data error found | Low/medium: misstated post-poke 5m bar count/range | Medium: called a non-monotonic 15m-high sequence progressively lower and excluded a 101.0 close |
| E. NO_TRADE_DISCIPLINE | High: `NO_TRADE` | High: `WAIT` | High: `NO_TRADE` |
| F. BREAKOUT_CONFIRMATION_LOGIC | High: rejected 103 without lower-timeframe confirmation | Medium: correct principle contaminated by an invented two-close requirement | High: correctly required leaving old space plus lower-timeframe confirmation/continuation |
| G. NO_INVENTED_RULES | High: no material fixed rule invented | Low: actual answer introduced “two consecutive 5m closes” | High: explicitly avoided unsupported numeric thresholds |
| H. UNCERTAINTY_HONESTY | High: direction and breakout validity left unknown | High: direction left unknown | High: higher-timeframe context, exact boundaries and thresholds declared unknown |
| I. VISUAL_STRUCTURED_CONSISTENCY | High | Medium/low because cited visual/data details conflict with governed values | Medium because broad interpretation is consistent but two exact claims are not |
| J. ANSWER_COMPLETENESS | Complete and scoreable | Complete and scoreable | Complete and scoreable |
| K. ACTUAL_COST_CNY | 0.110874 | 0.1085952 | 0.61002 |
| L. LATENCY_MS | 85,682 | 36,973 | 160,533 |

## Provider findings

### DeepSeek

DeepSeek correctly rejected the trade, treated 103 as a failed probe rather than a
qualified breakout, applied lower-timeframe confirmation, preserved uncertainty,
and did not invent a fixed rule. No material visual or structured-data error was
found in its final answer on this fixture.

### MiniMax

MiniMax correctly chose `NONE / WAIT / NONE`, but its answer required “two
consecutive 5m closes,” a fixed rule absent from the frozen Jianghe material. It
also described all three 1H bodies as wide and misstated the count/range of the 5m
bars following the probe. Its lower cost and latency cannot override those quality
defects.

### Kimi

Kimi correctly chose `NO_TRADE / NONE`, rejected the 103 probe, applied the real
lower-timeframe confirmation principle, and declared unknowns without inventing a
fixed threshold. Its `FAMILY=C` label conflicts with its own finding that no setup
exists; `NONE` is the permissible current classification. It also called the
`101.35 / 101.15 / 101.25 / 101.15 / 101.05` highs progressively lower and said
the last ten 5m closes all stayed at or below 100.9 although one is 101.0.

## One-fixture limitation and next phase

This ranking is only a current model-capability selection signal from one matched
fixture. It establishes neither overall accuracy, long-run trading performance nor
a permanent provider adoption.

No formal downloaded-K-line batch-evaluation protocol or populated local canonical
dataset path is currently present in this checkout. The minimal next action is to
use DeepSeek with the current Stage-A V0.3 Jianghe prompt/context, first verify or
materialize the already-authorized canonical dataset path through the existing
dataset-build authority, then freeze a small causal point-in-time pilot batch before
execution. Do not expose future/outcome data and do not start a large batch until
that existing-authority binding is explicit.
