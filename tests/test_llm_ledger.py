"""M1.5: usage ledger + per-family cost caps (cap breach raises BEFORE the call)."""

import sqlite3

import pytest

from llm import (
    CostCapExceeded,
    CostCaps,
    InMemoryLedger,
    LLMClient,
    LLMServerError,
    SqliteLedger,
    UsageContext,
)
from migrations import apply_migrations
from tests.llm_provider_fakes import ScriptedProvider

MSGS = [{"role": "user", "content": "SECRET PROMPT TEXT about Ada"}]
FAM = UsageContext(family_id="fam_a", student_id="stu_1")


def test_every_call_is_recorded_without_prompt_text():
    ledger = InMemoryLedger()
    c = LLMClient(ScriptedProvider("SECRET REPLY"), env={}, ledger=ledger)
    c.complete("judge", MSGS, usage=FAM)
    (row,) = ledger.rows
    assert (row["family_id"], row["student_id"], row["task"]) == ("fam_a", "stu_1", "judge")
    assert row["prompt_tokens"] == 10 and row["cost_usd"] == pytest.approx(0.001)
    assert row["status"] == "ok" and row["latency_ms"] >= 0
    assert "SECRET" not in repr(row)


def test_cap_stops_the_call_before_it_is_made():
    ledger = InMemoryLedger()
    provider = ScriptedProvider("one", "two", cost=0.6)
    c = LLMClient(provider, env={}, ledger=ledger, caps=CostCaps(family_month_usd=1.0))
    c.complete("judge", MSGS, usage=FAM)  # spent 0.6 < 1.0
    c.complete("judge", MSGS, usage=FAM)  # spent 1.2 now (one call may overshoot)
    with pytest.raises(CostCapExceeded) as info:
        c.complete("judge", MSGS, usage=FAM)
    assert len(provider.requests) == 2  # the third request was never sent
    assert info.value.family_id == "fam_a" and info.value.cap == 1.0 and info.value.attempts == 0


def test_cap_is_per_family():
    ledger = InMemoryLedger()
    provider = ScriptedProvider("a", "b", cost=2.0)
    c = LLMClient(provider, env={}, ledger=ledger, caps=CostCaps(family_month_usd=1.0))
    c.complete("judge", MSGS, usage=FAM)
    c.complete("judge", MSGS, usage=UsageContext(family_id="fam_b"))  # other family unaffected
    with pytest.raises(CostCapExceeded):
        c.complete("judge", MSGS, usage=FAM)


def test_unlimited_by_default_for_self_hosters():
    ledger = InMemoryLedger()
    provider = ScriptedProvider(*["x"] * 5, cost=100.0)
    c = LLMClient(provider, env={}, ledger=ledger)
    for _ in range(5):
        c.complete("judge", MSGS, usage=FAM)
    assert len(provider.requests) == 5
    assert CostCaps.from_env({}).family_month_usd is None


def test_cap_from_env():
    ledger = InMemoryLedger()
    provider = ScriptedProvider("x", cost=0.5)
    c = LLMClient(provider, env={"LLM_CAP_FAMILY_MONTH_USD": "0.25"}, ledger=ledger)
    c.complete("judge", MSGS, usage=FAM)
    with pytest.raises(CostCapExceeded):
        c.complete("judge", MSGS, usage=FAM)


def test_failed_calls_are_recorded_as_errors():
    ledger = InMemoryLedger()
    c = LLMClient(
        ScriptedProvider(*[LLMServerError("x")] * 3),
        env={"LLM_FALLBACK_MODEL_JUDGE": ""},
        ledger=ledger,
        sleep=lambda s: None,
    )
    with pytest.raises(LLMServerError):
        c.complete("judge", MSGS, usage=FAM)
    assert ledger.rows[0]["status"] == "error" and ledger.rows[0]["cost_usd"] is None


def test_ledger_fault_never_fails_the_call(caplog):
    class Broken(InMemoryLedger):
        def record(self, *a, **k):
            raise sqlite3.OperationalError("no such table")

    c = LLMClient(ScriptedProvider("fine"), env={}, ledger=Broken())
    assert c.complete("judge", MSGS, usage=FAM).text == "fine"
    assert "ledger write failed" in caplog.text


def test_sqlite_ledger_roundtrip_with_migration(tmp_path):
    db = str(tmp_path / "t.db")
    assert 3 in apply_migrations(db)
    ledger = SqliteLedger(lambda: db)
    c = LLMClient(ScriptedProvider("a", "b", cost=0.4), env={}, ledger=ledger)
    c.complete("author", MSGS, usage=FAM)
    c.complete("author", MSGS, usage=UsageContext(family_id="fam_b"))
    conn = sqlite3.connect(db)
    cols = [r[1] for r in conn.execute("PRAGMA table_info(llm_usage)")]
    assert not {"prompt", "content", "response", "text"} & set(cols)
    rows = conn.execute("SELECT family_id, cost_usd FROM llm_usage ORDER BY family_id").fetchall()
    assert rows == [("fam_a", 0.4), ("fam_b", 0.4)]
    assert ledger.spent_usd("fam_a", "2000-01-01") == pytest.approx(0.4)
    assert ledger.spent_usd("fam_a", "2999-01-01") == 0.0


def test_sqlite_cap_enforced(tmp_path):
    db = str(tmp_path / "t.db")
    apply_migrations(db)
    provider = ScriptedProvider("a", cost=5.0)
    c = LLMClient(
        provider, env={}, ledger=SqliteLedger(lambda: db), caps=CostCaps(family_month_usd=1.0)
    )
    c.complete("judge", MSGS, usage=FAM)
    with pytest.raises(CostCapExceeded):
        c.complete("judge", MSGS, usage=FAM)
    assert len(provider.requests) == 1
