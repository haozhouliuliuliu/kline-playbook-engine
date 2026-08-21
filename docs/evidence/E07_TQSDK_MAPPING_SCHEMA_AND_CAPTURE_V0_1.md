# E07 TqSdk 主连映射接口与捕获证据 V0.1

## 结论

`E07_SCHEMA_PROBE_DONE` 已完成。经 Owner 授权的已认证 TqSdk 会话仅查询
`TqApi.query_his_cont_quotes`，确认 TqSdk `3.10.1` 返回 pandas 表：`date`
列加上每个请求 `KQ.m@交易所.品种` 的具体合约字符串列。

原始捕获：[E07_TQSDK_QUERY_HIS_CONT_QUOTES_RAW_V0_1.json](E07_TQSDK_QUERY_HIS_CONT_QUOTES_RAW_V0_1.json)。
它只含日期与主连到具体合约的映射；不含 OHLC、成交量、持仓量、费用、收益、
候选表现或订单数据。

## 固定边界

- 接口：`TqApi.query_his_cont_quotes(symbol, n)`。
- SDK 版本：`3.10.1`。
- 解码版本：`TQSDK_3_10_1_PANDAS_DATE_PLUS_SYMBOL_COLUMNS`。
- 目标窗口：2024-01-01 至 2025-12-31；构建时只使用窗口开始前最近一条映射和
  窗口内变化，窗口后的行一律忽略。
- 六个来源符号：`KQ.m@SHFE.cu`、`al`、`ni`、`au`、`ag`、`rb`。
- 切换规则：捕获日映射变化在下一条捕获交易日的 09:00（Asia/Shanghai）生效，
  并同时可用；不以项目侧规则推断换月。
- 生成物：[E07_SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_V0_1.json](E07_SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_V0_1.json)，
  共 105 条变化记录，六品种全部映射到 canonical concrete universe，违规数为 0。

## 完整性与可复现性

原始文件 SHA-256 为
`b95c53a455af5b2dcc8e862875390a843adf28d0b829a72283c77f0343cba303`；
映射日程身份为
`331ba31e2a03695160aff28f7c7c58888dcc9bc091515e176c8d5c6b66edcb5c`。
原始文件记录的 `retrieved_at` 来自本地捕获文件元数据，不能单独证明外部服务端时间；
该限制不改变本项目对已认证来源、内容哈希和可重复构建的边界。

## 禁止事项仍然有效

不得生成或使用伪主连价格柱，不得用成交量、持仓量、日历、价格、收益或 PnL
替代来源映射；当前证据也不授权真实行情接入、订单提交或真实资金交易。
