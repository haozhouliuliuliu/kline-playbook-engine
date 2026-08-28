from pathlib import Path

path = Path("src/paper_runtime.py")
text = path.read_text(encoding="utf-8")

marker = "    def process_conditional_orders(\n"
if marker not in text:
    raise SystemExit("process_conditional_orders marker missing")
helper = '''    def _recover_pending_observed_wakes(
        self, *, at: datetime
    ) -> tuple[LiveCausalWake, ...]:
        """Recover safely-not-dispatched durable cognition wakes before newer market work."""
        at = _aware(at, "pending paper wake recovery time")
        pending = self.wake_journal.pending_observations()
        if not pending:
            return ()
        complete_five = tuple(
            bar for bar in self.context_builder.complete_bars() if bar.timeframe == "5m"
        )
        recovered: list[LiveCausalWake] = []
        for record in pending:
            if record.trader_identity != self.trader_identity:
                raise RuntimeError("PAPER_PENDING_WAKE_TRADER_IDENTITY_MISMATCH")
            if record.concrete_contract_id != self.concrete_contract_id:
                raise RuntimeError("PAPER_PENDING_WAKE_CONTRACT_IDENTITY_MISMATCH")
            if at < record.observed_at:
                raise RuntimeError("PAPER_PENDING_WAKE_CLOCK_REGRESSION")
            matches: list[LiveCausalWake] = []
            original_observed_at = record.observed_at.astimezone(
                self.context_builder.calendar.timezone
            )
            for bar in complete_five:
                if bar.end != record.bar_end:
                    continue
                candidate = LiveCausalWake(
                    bar=bar,
                    observed_at=original_observed_at,
                    policy_identity=self.context_builder.policy_identity,
                )
                if candidate.bar_identity == record.bar_identity:
                    matches.append(candidate)
            if len(matches) != 1:
                raise RuntimeError("PAPER_PENDING_WAKE_CAUSAL_STATE_MISMATCH")
            wake = matches[0]
            if wake.wake_identity != record.wake_identity:
                raise RuntimeError("PAPER_PENDING_WAKE_IDENTITY_MISMATCH")
            recovered.append(wake)
        return tuple(sorted(recovered, key=lambda item: (item.bar.end, item.wake_identity)))

    def _execute_triggered_conditionals(self, *, at: datetime) -> None:
        """Run already-durable triggered STOP children after wake durability is secured."""
        blockers = self._resume_triggered_conditionals(at=at)
        if blockers:
            raise RuntimeError(
                "PAPER_CONDITIONAL_RECOVERY_BLOCKED:" + ";".join(blockers)
            )
        blockers = self.refresh_broker_truth(at=at)
        if blockers:
            raise RuntimeError(
                "PAPER_CONDITIONAL_RECONCILIATION_BLOCKED:" + ";".join(blockers)
            )

'''
text = text.replace(marker, helper + marker, 1)

old_signature = '''    def process_conditional_orders(
        self, bar: LiveCausalBar, *, observed_at: datetime
    ) -> tuple[str, ...]:
        """Evaluate armed STOP directives from one governed current closed bar."""
        observed_at = _aware(observed_at, "conditional observation time")
'''
new_signature = '''    def process_conditional_orders(
        self, bar: LiveCausalBar, *, observed_at: datetime,
        execute_triggered: bool = True,
    ) -> tuple[str, ...]:
        """Evaluate armed STOP directives from one governed current closed bar."""
        observed_at = _aware(observed_at, "conditional observation time")
        if type(execute_triggered) is not bool:
            raise ValueError("conditional execution flag must be bool")
'''
if old_signature not in text:
    raise SystemExit("conditional signature block missing")
text = text.replace(old_signature, new_signature, 1)

old_trigger = '''        if triggered:
            blockers = self._resume_triggered_conditionals(at=observed_at)
            if blockers:
                raise RuntimeError("PAPER_CONDITIONAL_RECOVERY_BLOCKED:" + ";".join(blockers))
            blockers = self.refresh_broker_truth(at=observed_at)
            if blockers:
                raise RuntimeError("PAPER_CONDITIONAL_RECONCILIATION_BLOCKED:" + ";".join(blockers))
        return tuple(triggered)
'''
new_trigger = '''        if triggered and execute_triggered:
            self._execute_triggered_conditionals(at=observed_at)
        return tuple(triggered)
'''
if old_trigger not in text:
    raise SystemExit("conditional execution block missing")
text = text.replace(old_trigger, new_trigger, 1)

old_entry = '''        results: list[PaperWakeResult] = []
        wakes = self.context_builder.observe(bars, observed_at=observed_at)
        for minute in self.context_builder.newly_admitted_one_minute_bars:
            self.process_conditional_orders(minute, observed_at=observed_at)
        for wake in wakes:
'''
new_entry = '''        results: list[PaperWakeResult] = []
        pending_wakes = self._recover_pending_observed_wakes(at=observed_at)
        pending_recovery = bool(pending_wakes)
        if pending_recovery:
            wakes = pending_wakes
        else:
            wakes = self.context_builder.observe(bars, observed_at=observed_at)
            triggered: list[str] = []
            for minute in self.context_builder.newly_admitted_one_minute_bars:
                triggered.extend(self.process_conditional_orders(
                    minute, observed_at=observed_at, execute_triggered=False
                ))
            # All local 1m STOP evaluations happen before cognition dispatch, but
            # every 5m cognition wake is durable before a triggered external STOP
            # submit can abort this processing cycle.
            for wake in wakes:
                self.context_builder.admit_wake_to_journal(
                    wake, journal=self.wake_journal,
                    trader_identity=self.trader_identity,
                    concrete_contract_id=self.concrete_contract_id,
                )
            if triggered:
                self._execute_triggered_conditionals(at=observed_at)
        for wake in wakes:
'''
if old_entry not in text:
    raise SystemExit("process_closed_minutes entry block missing")
text = text.replace(old_entry, new_entry, 1)

old_tail = '''            results.append(PaperWakeResult(
                wake.wake_identity, decision.decision_identity,
                instruction.client_request_id, confirmed_id))
        return tuple(results)

    def cancel_order'''
new_tail = '''            results.append(PaperWakeResult(
                wake.wake_identity, decision.decision_identity,
                instruction.client_request_id, confirmed_id))
        if pending_recovery:
            return tuple(results) + self.process_closed_minutes(
                bars, observed_at=observed_at
            )
        return tuple(results)

    def cancel_order'''
if old_tail not in text:
    raise SystemExit("process_closed_minutes tail block missing")
text = text.replace(old_tail, new_tail, 1)

path.write_text(text, encoding="utf-8")
