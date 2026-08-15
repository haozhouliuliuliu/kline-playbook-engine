# PROJECT_BOOTSTRAP 正式验收

日期：2026-08-16

## 验收结论

- 接受候选提交：`b6d1961dca5b4c879bc7deb6406f3c63723b04d4`
- 完整回归：`python -m unittest discover -s tests -v`，89 项测试全部通过。
- 工具结论：`TOOL_DECISION=USE_EXISTING`；本验收包未引入依赖，也未采用数据源或外部框架。
- `BOOTSTRAP_ACCEPTANCE=GO`

## 独立对抗评审及裁决

独立 DeepSeek 对抗评审检查了以下范围，并均报告 `PASS`：

- PIT（按当时可得信息）/未见数据完整性；
- 策略身份与证据；
- 执行因果顺序；
- 资金与持仓生命周期；
- 中国期货合约语义；
- 多策略组合语义；
- 范围陈述诚实性；
- 验证质量。

评审最初仍给出 `NO_GO`，唯一理由是认为已采用合同的 SHA-256 与已提交 Git blob 不一致。该原始结论不被改写或隐藏，但其唯一阻塞理由已由下述原始字节验证确定性推翻。

字节安全验证命令（直接读取 Git 对象，不经过 PowerShell 文本管道）：

```powershell
python -c "import subprocess,hashlib; b=subprocess.check_output(['git','cat-file','blob','HEAD:CROSS_PROJECT_OPERATING_CONTRACT.md']); print(len(b)); print(hashlib.sha256(b).hexdigest())"
```

验证结果：

- Git blob SHA-1：`e529434a0d5f86a3c27c381a142d0618ca710ccf`
- Git blob 字节数：`46532`
- Git blob SHA-256：`3b5ceaaa3696375b941fd2aaba95615cf9352dcada3696b60137650bf690101e`
- 该 SHA-256 与 `CURRENT_STATE.md` 的 `ADOPTED_CONTRACT_SHA256` 完全一致。
- 该 SHA-256 与 `docs/evidence/ADOPTED_CONTRACT.sha256` 完全一致。

Windows 工作树文件可能因 CRLF 换行产生不同的直接文件哈希；项目固定的是上述规范 Git blob 身份。因此合同固定值有效，无需重新固定，也不得修改合同或其哈希。

## 非阻塞发现

独立评审还记录了两项轻微发现：

1. 旧版会话日历辅助函数与权威 `SessionMetadata` 存在重叠。
2. 部分平仓的未实现盈亏建模采用了简化处理。

两项发现均不阻塞本次验收，保留为后续工程清理事项；本验收包不修复它们，也不改变既有执行或研究语义。

本次验收没有削弱任何技术安全门、研究门、最终未见数据门、Shadow/实盘门或真实资金门。综合完整回归、独立评审覆盖及合同固定值裁决，`PROJECT_BOOTSTRAP` 正式验收通过。
