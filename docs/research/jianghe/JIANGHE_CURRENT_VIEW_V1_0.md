# 江河交易员当前研究视图 V1.0 — Final Source Distillation

```text
TRADER_ID=JIANGHE_TRADER
SOURCE_SCOPE=001..099
SOURCE_TOTAL=99
MEDIA_AVAILABLE=98
SEMANTICALLY_REVIEWED_WITH_RELIABLE_LANGUAGE_OR_BURNED_TEXT=97
VISUAL_ONLY_NO_RELIABLE_LANGUAGE=065
BLOCKED_PAID_GATE=022
CORPUS_MEDIA_RECOVERY=COMPLETE
FINAL_SOL_REVIEW=COMPLETE
FINAL_SOURCE_DISTILLATION=COMPLETE
SOURCE_ONLY_VERIFIED=NO
PRIMARY_ELIGIBLE=NO
TOOL_DECISION=USE_EXISTING
```

## 当前权威组合

V1.0 不删除旧证据；旧V0.x继续保留来源演进历史。当前读取优先级：

1. `JIANGHE_TRADER_DOSSIER_V1_0.md`
2. `JIANGHE_SOL_FINAL_REVIEW_RESOLUTION_V1_0.md`
3. `JIANGHE_CLAIM_LEDGER_SUPPLEMENT_FINAL_V1_0.jsonl`
4. `JIANGHE_CASE_LIBRARY_SUPPLEMENT_FINAL_V1_0.md`
5. `JIANGHE_STRATEGY_FAMILIES_V1_0.md`
6. `JIANGHE_SYSTEM_PROCESS_V1_0.md`
7. `JIANGHE_UNKNOWN_REGISTER_V1_0.md`
8. `JIANGHE_CONTRADICTION_REGISTER_V1_0.md`
9. `JIANGHE_EVIDENCE_REVIEW_QUEUE_V1_0.csv`
10. 既有V0.1–V0.9 claim/case/source artifacts。

## V1.0最终变化

- 007修复后正式补审；直接支持 `势/趋势 > 位/位置 > 态/形态`，以及重叠对抗先等待。
- 016只确认“势位态动”框架名，不足以补全四维定义。
- 017补全退出体系，并把“趋势初期 vs 非初期退出”关闭为阶段依赖关系。
- 018与069共同关闭内部结构术语冲突：同周期内部结构可确认/重分类/管理，但不独立给入场；低周期结构必须到真实低周期重画。
- 048、099所谓恢复远端SRT均被Sol判定为错视频字幕并拒绝；分别改用视频烧录文字/字幕。
- 065本地ASR虽然模型、哈希、时间轴验收通过，但语义明显幻觉；转写被拒绝，保持视觉可读但无可靠语言交易语义。
- 030三分开仓边界、078严格50/50、079收盘价止损均关闭为**来源本身不能唯一锁定**，不替作者补规则。
- 096三个维度已由完整视频烧录字幕钉死。
- 核心Family仍只有A–D；没有Family E。

## Corpus exception

- `022`：`SOURCE_UNAVAILABLE_PAID_GATED`，合法不可达例外，不购买、不绕过。
- `065`：媒体可用，但可靠语言证据不可用；不从订单结果倒推策略。

## 解释与安全边界

- `SOURCE CLAIM != PROJECT/AI INTERPRETATION != MACHINE OPERATIONALIZATION`
- `UNKNOWN > GUESSING`
- 收益/R/账户结果不是validity evidence。
- 本V1.0是**来源蒸馏收口**，不是SOURCE_ONLY验证、PRIMARY冻结或绩效验证。
