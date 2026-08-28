# PAPER 订单恢复 Codex Worker 证据（候选）

状态：`BRANCH_LOCAL_EVIDENCE_CANDIDATE__OFFLINE_ONLY__AWAITING_INTEGRATION_REVIEW`

实现提交：`f3270ceea76080e3925674b95c542e5fa90cace7`

工作分支：`codex/paper-order-recovery-v01-20260827`

集成基线：`61f47c87d89035f856021ef1e7235f2815f34076`

## 已实现的离线状态机

- 提交：`PREPARED -> ATTEMPT_STARTED -> BROKER_ORDER_ID_KNOWN`；异常、丢失结果或快照缺失会保留为 UNKNOWN，绝不自动重试。
- 取消：先持久化 `CANCEL_ATTEMPT_STARTED`，只有经纪商快照给出 `CANCELLED`、`FILLED` 或 `REJECTED` 的精确终态才会解析；超时后为 `UNKNOWN_CANCEL`。
- 替换：持久化绑定原订单、替换代次、替换意图、旧取消操作和新子请求。只有旧单被确认 `CANCELLED` 时才允许子单进入提交尝试；未知取消禁止子单提交。
- 恢复：`reconcile_broker_orders` 只使用传入的经纪商订单快照；提交后看不到订单不是“未发送”的证明，而是持久化 UNKNOWN。重复订单标识、未知经纪商订单和标识不匹配会产生机器可见阻塞。

## 故障与对抗测试

新增测试覆盖：提交尝试后的重启/快照缺失、取消超时且不得重试、重连后取消解析及幂等、取消中的部分成交、取消成功与未知两条替换路径、替换子单单次使用、重复原生订单标识、异常数量。

同时收紧了原生订单映射：未知生命周期、缺少稳定标识、重复经纪商订单标识、非法 `volume_left`、成交数量超过委托数量均会失败关闭。

## 验证结果

以下命令均在本地离线执行并通过：

```text
python -m unittest tests.test_paper_order_recovery tests.test_paper_live_execution_foundation tests.test_paper_execution_readiness tests.test_paper_supervisor_foundation -v
python -m unittest discover -s tests
python -m compileall -q src tools tests
python tools/check_authority_consistency.py
git diff --check
```

完整测试套件通过；其中现有的 `pyarrow` 不可用测试按原有条件跳过。

## 仍需后续独立验证的第三方边界

TqSdk 的 PAPER 连接、账户、订单对象字段和原子替换能力仍均未验证、未采用。本分支只使用注入式伪对象；没有读取凭据、没有登录账户、没有连接外部 PAPER、没有发送提交/取消/替换，也没有任何真实资金或提供商调用。
