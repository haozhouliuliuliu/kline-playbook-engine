from pathlib import Path

path = Path("tests/test_jianghe_prespend_repair.py")
text = path.read_text(encoding="utf-8")
old = '''            evidence = transport.invoke(
                _request(), authorization=auth, budget=ledger,
                rate_card=_rate(KIMI_K3_SPEC), bounds=InvocationBounds(1500, 500, 200),
                fx=None, now=NOW,
            )
'''
new = '''            bounds = InvocationBounds(1500, 500, 200)
            rate = conservative_builtin_rate_card(
                KIMI_K3_SPEC, bounds,
                effective_at=NOW - timedelta(hours=1),
                expires_at=NOW + timedelta(hours=1),
            )
            fx = FxAuthority(
                usd_to_cny=Decimal("8"),
                authority_uri="https://example.invalid/fx-test-snapshot",
                effective_at=NOW - timedelta(hours=1),
                expires_at=NOW + timedelta(hours=1),
            )
            evidence = transport.invoke(
                _request(), authorization=auth, budget=ledger,
                rate_card=rate, bounds=bounds, fx=fx, now=NOW,
            )
'''
count = text.count(old)
if count != 1:
    raise SystemExit(f"expected one synthetic authorized transport fixture, found {count}")
path.write_text(text.replace(old, new), encoding="utf-8")
