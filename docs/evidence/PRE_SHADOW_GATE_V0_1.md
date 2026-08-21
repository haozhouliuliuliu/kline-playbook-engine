# Pre-Shadow Gate V0.1

`src/pre_shadow_gate.py` 是 machine-readable gate。它分别输出 `technically_ready` 与
`authorized_to_start`；后者只有技术项齐全且独立 Shadow authorization 为真才为真。
当前项目仍保持 `PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED`，所以该 gate 不能自动启动
Shadow。`src/prospective_execution_authority.py` 要求未来每次执行都有当时可得的费用/保证金、
逐日涨跌停和显式 slippage authority；任何缺失都 fail closed，绝不以历史回填或零滑点替代。
