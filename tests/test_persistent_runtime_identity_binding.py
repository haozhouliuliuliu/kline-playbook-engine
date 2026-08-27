from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import tempfile
import unittest

from src.jianghe_ai_trader import JiangheAITraderIdentity
from src.persistent_deepseek_runtime import (
    CURRENT_MODEL,
    DeepSeekHarnessRuntimeContract,
    PersistentDeepSeekTraderPrototype,
    ProjectToolRegistry,
)
from src.persistent_trader_store import PersistentTraderStore


SYSTEM_PROMPT = "stable-system-prompt"
DECISION_PROMPT = "stable-decision-prompt"


def identity(*, system_hash: str, decision_hash: str, tools: tuple[str, ...]) -> JiangheAITraderIdentity:
    return JiangheAITraderIdentity(
        knowledge_pack_identity="knowledge-v1",
        primary_branch_registry_identity="primary-v1",
        interpretation_set_identity="interpretation-v1",
        model_provider="deepseek",
        model_id_version=CURRENT_MODEL,
        system_prompt_identity=system_hash,
        decision_prompt_identity=decision_hash,
        context_selection_policy_identity="bounded-context-v1",
        memory_policy_identity="persistent-memory-v1",
        chart_renderer_identity="renderer-v1",
        observation_schema_version="JIANGHE_OBSERVATION_V0_1",
        wake_policy_version="wake-v1",
        decision_schema_version="JIANGHE_RUNTIME_RESPONSE_V0_2",
        runtime_normalizer_identity="normalizer-v1",
        hard_execution_envelope_identity="hard-envelope-v1",
        inference_configuration=(("max_retries", "0"),),
        tool_capability_set=tools,
        source_family_scope=("A", "B", "C", "D"),
    )


class RuntimeIdentityBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.contract = DeepSeekHarnessRuntimeContract.from_prompts(
            system_prompt=SYSTEM_PROMPT,
            decision_prompt=DECISION_PROMPT,
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _components(self, trader: JiangheAITraderIdentity, registered_tools: tuple[str, ...]):
        store = PersistentTraderStore(
            Path(self.temp.name) / f"{trader.identity}.sqlite3",
            trader_identity=trader.identity,
        )
        tools = ProjectToolRegistry(store)
        for tool_name in registered_tools:
            tools.register(tool_name, lambda _args: {"ok": True})
        return store, tools

    def test_accepts_exact_prompt_and_tool_identity_binding(self) -> None:
        trader = identity(
            system_hash=sha256(SYSTEM_PROMPT.encode()).hexdigest(),
            decision_hash=sha256(DECISION_PROMPT.encode()).hexdigest(),
            tools=("jianghe_kline_snapshot",),
        )
        store, tools = self._components(trader, ("jianghe_kline_snapshot",))
        try:
            runtime = PersistentDeepSeekTraderPrototype(
                trader_identity=trader,
                store=store,
                retriever=None,  # constructor identity test; retrieval is exercised elsewhere
                tools=tools,
                runtime_contract=self.contract,
            )
            self.assertEqual(runtime.trader_identity.identity, trader.identity)
        finally:
            store.close()

    def test_rejects_system_prompt_identity_drift(self) -> None:
        trader = identity(
            system_hash=sha256(b"different-system").hexdigest(),
            decision_hash=sha256(DECISION_PROMPT.encode()).hexdigest(),
            tools=("jianghe_kline_snapshot",),
        )
        store, tools = self._components(trader, ("jianghe_kline_snapshot",))
        try:
            with self.assertRaisesRegex(ValueError, "system prompt"):
                PersistentDeepSeekTraderPrototype(
                    trader_identity=trader,
                    store=store,
                    retriever=None,
                    tools=tools,
                    runtime_contract=self.contract,
                )
        finally:
            store.close()

    def test_rejects_decision_prompt_identity_drift(self) -> None:
        trader = identity(
            system_hash=sha256(SYSTEM_PROMPT.encode()).hexdigest(),
            decision_hash=sha256(b"different-decision").hexdigest(),
            tools=("jianghe_kline_snapshot",),
        )
        store, tools = self._components(trader, ("jianghe_kline_snapshot",))
        try:
            with self.assertRaisesRegex(ValueError, "decision prompt"):
                PersistentDeepSeekTraderPrototype(
                    trader_identity=trader,
                    store=store,
                    retriever=None,
                    tools=tools,
                    runtime_contract=self.contract,
                )
        finally:
            store.close()

    def test_rejects_tool_capability_identity_drift(self) -> None:
        trader = identity(
            system_hash=sha256(SYSTEM_PROMPT.encode()).hexdigest(),
            decision_hash=sha256(DECISION_PROMPT.encode()).hexdigest(),
            tools=("jianghe_kline_snapshot",),
        )
        store, tools = self._components(trader, ("different_tool",))
        try:
            with self.assertRaisesRegex(ValueError, "tool capability"):
                PersistentDeepSeekTraderPrototype(
                    trader_identity=trader,
                    store=store,
                    retriever=None,
                    tools=tools,
                    runtime_contract=self.contract,
                )
        finally:
            store.close()


if __name__ == "__main__":
    unittest.main()
