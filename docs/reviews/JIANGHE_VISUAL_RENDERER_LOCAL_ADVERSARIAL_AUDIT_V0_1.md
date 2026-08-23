# 江河 VISUAL Renderer V0.1 — 本地独立对抗审计报告

- 审计角色：独立 adversarial verifier（非开发 lane，非 integration lane）
- Worktree：`kline-playbook-engine-wt-visual-renderer-v01`（local-only，未 fetch/pull/push）
- 基线 commit：`1dc1e34bea6edce3e44c0b693c496a1e15ea9177`（renderer source 冻结基线）
- 审计产物：`tests/test_jianghe_visual_renderer_adversarial.py`（76 tests）
- 约束遵守：未修改 `src/jianghe_visual_renderer.py`、`tools/render_jianghe_visual_observation_v0_1.py`、`tests/test_jianghe_visual_renderer.py`；source 修复归 integration lane。

## 结论

**VISUAL_RENDERER_ADVERSARIAL_FINDINGS_FOUND** — 3 个 finding（全部留有可运行 reproducer 测试）。

---

## FINDINGS

### F-ADV-01 — 渲染依赖进程全局 decimal context（未治理环境依赖）

- **SEVERITY**: HIGH（决定论 governed-ness 漏洞）
- **REPRODUCER_TEST**: `NumericAdversarialTests.test_rendering_must_not_depend_on_global_decimal_context`
- **EXPECTED**: 同一 input + 同一 config，无论调用进程如何设置 `decimal.getcontext().prec`，PNG 字节流必须完全相同（renderer 声称"同一输入永远得到同一字节流"）。
- **ACTUAL**: 同一 crafted input 在 `prec=28` 与 `prec=6` 下产生不同 PNG SHA（`8acea1c8…` vs `f0b75595…`）。`y_of` / `_price_ticks` 中的 Decimal 除法与 `ROUND_HALF_UP` 取整使用调用时点的全局 context，renderer 未固定 precision、未使用 `localcontext` 隔离。
- **AFFECTED_IDENTITY_OR_CAUSAL_RULE**: 决定论规则——`input_observation_identity` 与 `renderer_config_identity` 相同的两份渲染可以产生不同 `png_sha256`；身份不变量依赖未被 renderer 治理的进程全局状态，任何同进程代码（或其他模块）修改 decimal context 即可改变模型所见图像。

### F-ADV-02 — CLI 输出非原子：manifest 写失败后遗留"裸 PNG"半成品

- **SEVERITY**: MEDIUM（产物完整性 / fail-closed 语义）
- **REPRODUCER_TEST**: `CliAdversarialTests.test_cli_write_must_be_atomic_no_half_success`
- **EXPECTED**: CLI 任何失败路径不得留下貌似成功的半成品 PNG/manifest 组合（task contract："不得留下貌似成功的半成品 manifest/PNG 组合"）。
- **ACTUAL**: CLI 先 `write_bytes(png)` 再 `write_text(manifest)`；当 manifest 路径失败（父目录不存在 / read-only）时退出码为 1，但 PNG 已落盘且无 manifest。下游拾取者可能把无 manifest 的 PNG 当作合法产物。
- **AFFECTED_IDENTITY_OR_CAUSAL_RULE**: 产物原子性——`visual_artifact_identity` 声明的 (png, manifest) 配对关系在失败路径上被破坏。

### F-ADV-03 — 极端指数 Decimal 未 fail closed，label 字符串无界展开（DoS 面）

- **SEVERITY**: MEDIUM（资源治理；输入驱动的内存/CPU 消耗无上限）
- **REPRODUCER_TEST**: `NumericAdversarialTests.test_extreme_decimal_exponent_must_fail_closed`
- **EXPECTED**: 极端数值（如 `1E-3000`、乃至 `1E-999999999`）应被 fail closed（受控 ValueError），而非产生随指数线性增长的未治理资源消耗。
- **ACTUAL**: renderer 接受 `1E-3000` 并成功渲染。`_format_decimal` 用 `format(value.normalize(), "f")` 把 tick label 展开为十进制纯字符串，长度 ≈ |指数|；`1E-999999999` 会构造约 1GB 字符串并逐字形绘制，导致 MemoryError / 长时间阻塞——未治理异常而非 fail closed。
- **AFFECTED_IDENTITY_OR_CAUSAL_RULE**: fail-closed 规则——"不能 crash 为未治理异常"被违反；数值校验只排除了 NaN/Inf，未约束有限但极端指数的 Decimal。

---

## OBSERVED 行为记录（非 finding，contract 未明确处的真实语义）

1. **Representation-sensitive identity**：同一 instant 的不同时区表示（`+08:00` vs `Z`）、数值相同的不同价格字符串（`"100"` vs `"100.0"`）产生不同 input/artifact identity（identity 严格于像素，方向正确，无 coverage hole）。
2. **Title 大小写**：product/contract/timeframe 在 title 中统一 `.upper()`；`cu` 与 `CU` 像素相同但 identity 不同。
3. **close_time > as_of 不可能**：canonical `ObservationBar` 强制 `available_at >= close_time`，故 `close_time > as_of` 必蕴含 `available_at > as_of` 而被拒绝（closed/partial 皆然）。
4. **未知 JSON 字段被忽略**：CLI 对输入 JSON 中混入的 `future_bars`/`outcome`/`annotation` 等额外字段完全忽略，输出与基线逐字节相同（这正是未来泄露防护所期望的）。
5. **已存在输出文件被静默覆盖**：内容确定性相同；渲染校验失败的路径不留任何输出文件（仅 F-ADV-02 的 manifest 写失败路径例外）。
6. **锁定样式字段**：`partial_body_style`/`closed_body_style` 的任何 mutate 被 validation 拒绝（fail closed，正确）。

## 审计覆盖与结果

| 审计项 | 结果 |
|---|---|
| 跨进程确定性（10 次：不同 subprocess / PYTHONHASHSEED / cwd / 输出路径 / TZ） | PASS——PNG SHA、config/input/artifact 三层身份全部一致 |
| PNG 结构（signature/IHDR/IDAT/IEND/CRC/尺寸/filter 字节） | PASS——仅 IHDR+IDAT+IEND，无 tIME/tEXt/zTXt/iTXt/eXIf/pHYs/gAMA，无机器元数据明文 |
| 数值边界（极小/极大/多位小数/科学计数/-0/0/平盘/单 bar/high==low/微价差/巨量/零量） | PASS（除 F-ADV-01、F-ADV-03）；NaN/±Inf/sNaN 全字段 fail closed |
| OHLC 攻击（high<open / high<close / high<low / low>open / low>close / 负量） | PASS——全部拒绝；flat 蜡烛稳定且与 up/down 像素可区分 |
| 时间/时区（naive/异 offset 同 instant/非法 offset/available_at 边界/非单调/重复） | PASS——不读 Windows 本地时区（TZ=UTC/US/Pacific/Asia/Tokyo 输出一致） |
| 未来泄露（future bars reject、旁边未来文件、额外 JSON 字段） | PASS——reject 而非忽略；磁盘污染不影响输出 |
| 刻度因果（可见 outlier 合法改刻度、未来 outlier 被拒、刻度只依赖可见 bars） | PASS |
| 多 panel（1–4 渲染 / 5 拒绝 / 重复周期拒绝 / 顺序 swap 改 identity+像素 / 空 panel 拒绝 / 异 bar 数） | PASS |
| 字符串/字形（长标签/标点/Unicode/换行/控制符/路径样式/JSON 转义） | PASS——非法字符全部 fail closed（ValueError），无越界、无机器路径写入 |
| Config mutation 完备性（28 个可 mutate 字段逐一） | PASS——每个 mutation 均改变 config identity 与 artifact identity；无"画面变 identity 不变"hole；视觉颜色字段逐一验证改像素 |
| Input mutation 完备性（open/high/low/close/volume/三时间戳/is_closed/timeframe/product/contract/as_of） | PASS——全部正确改变 input/artifact identity；无 coverage hole |
| Partial/closed 语义 | PASS——同 OHLCV 下 closed vs partial 像素与 identity 均不同；时间语义矛盾由 canonical bar 阻断 |
| Manifest 独立重算（png_sha256 / config / input / artifact 四层哈希） | PASS——验证方可不依赖声明值独立重算全部四层；无 PnL/outcome/win/loss/future_* 内容 |
| CLI 对抗（malformed/unknown/missing/wrong-type/覆盖写/相对 vs 绝对路径） | PASS（除 F-ADV-02） |
| 依赖/网络静态扫描（AST + token） | PASS——纯 stdlib；无 requests/urllib/socket/PIL/matplotlib/font/random/uuid/time.time/datetime.now/os.environ/getpid |
| 结果推断静态扫描（可执行代码 AST） | PASS——renderer/CLI 无 LONG/SHORT/entry/stop/target/支撑阻力/breakout/MA/EMA 等推断逻辑 |

## 执行记录

- `python -m unittest tests.test_jianghe_visual_renderer -v`：31/31 PASS（原始测试未被修改、全部通过）
- `python -m unittest tests.test_jianghe_visual_renderer_adversarial -v`：76 tests，73 PASS / 3 FAIL（3 个 FAIL 即 F-ADV-01/02/03 的 reproducer，刻意保留）
- `python -m unittest discover -s tests`：1075 tests，FAILED (failures=3, skipped=8)——3 个 failure 全部是本审计的 finding reproducer，其余全部通过（8 个 skip 为既有 skip）
- `git diff --check`：clean
