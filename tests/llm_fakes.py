"""In-process fake of the OpenAI client for testing agent.generate_weekly_plan.

It answers from the same fixture files the E2E stub (frontend/e2e/llm-stub) serves, so pytest and
Playwright agree on what a "canned" scaffold and lesson look like. Classification mirrors the
stub: by prompt content, and anything unrecognised raises (never guesses).
"""

from __future__ import annotations

import json
import re
import threading
from pathlib import Path
from types import SimpleNamespace
from typing import Callable

FIXTURES = Path(__file__).resolve().parents[1] / "frontend" / "e2e" / "llm-stub" / "fixtures"
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


def _render(text: str, **values: str) -> str:
    return re.sub(r"\{\{(\w+)\}\}", lambda m: values.get(m.group(1), m.group(0)), text)


class _Response:
    def __init__(self, content: str) -> None:
        self._content = content
        self.choices = [SimpleNamespace(message=SimpleNamespace(content=content))]

    def model_dump(self) -> dict:
        return {"choices": [{"message": {"role": "assistant", "content": self._content}}]}


class FakeOpenAI:
    """Drop-in for ``openai.OpenAI``: ``client.chat.completions.create(**payload)``.

    Args:
        scaffold: raw string to return for the scaffold call (default: canned fixture built
            from the standards list in the prompt). Pass invalid JSON to test the fallback.
        broken_days: weekdays whose lesson reply is the invalid-JSON fixture.
        failing_days: weekdays whose lesson call raises (as a network/API error would).
        fail_scaffold / fail_everything: make those calls raise.
    """

    def __init__(
        self,
        *,
        scaffold: str | None = None,
        broken_days: set[str] | None = None,
        failing_days: set[str] | None = None,
        fail_scaffold: bool = False,
        fail_everything: bool = False,
        on_call: Callable[[dict], None] | None = None,
    ) -> None:
        self.scaffold = scaffold
        self.broken_days = broken_days or set()
        self.failing_days = failing_days or set()
        self.fail_scaffold = fail_scaffold
        self.fail_everything = fail_everything
        self.calls: list[dict] = []
        self._lock = threading.Lock()
        self._on_call = on_call
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    # -- helpers for assertions -------------------------------------------------------------
    def calls_of(self, kind: str) -> list[dict]:
        return [c for c in self.calls if c["kind"] == kind]

    # -- the fake API -----------------------------------------------------------------------
    def _create(self, **payload) -> _Response:
        prompt = "\n".join(str(m.get("content", "")) for m in payload["messages"])
        subject = (re.search(r"^Subject: (.+)$", prompt, re.M) or [None, "Unknown"])[1].strip()
        grade = (re.search(r"^Grade Level: (\d+)", prompt, re.M) or [None, "?"])[1]

        if "weekly lesson plan scaffold" in prompt:
            record = {"kind": "scaffold", "payload": payload}
            self._record(record)
            if self.fail_everything or self.fail_scaffold:
                raise RuntimeError("fake LLM: scaffold unavailable")
            if self.scaffold is not None:
                return _Response(self.scaffold)
            return _Response(self._canned_scaffold(prompt, subject, grade))

        if "Create a lesson plan for the following educational standard" in prompt:
            # The scaffold's focus ("Stub Monday focus") names the day. When the scaffold fell
            # back ("Day 1 focus") the label is just the focus text.
            match = re.search(r"^Day Focus: (.+)$", prompt, re.M)
            focus = match.group(1).strip() if match else ""
            named = re.fullmatch(r"Stub (\w+) focus", focus)
            day = named.group(1) if named else focus
            self._record({"kind": "day", "day": day, "payload": payload})
            if self.fail_everything or day in self.failing_days:
                raise RuntimeError(f"fake LLM: {day} unavailable")
            name = "invalid-day.txt" if day in self.broken_days else "day.json"
            raw = (FIXTURES / name).read_text(encoding="utf-8")
            return _Response(_render(raw, day=day, subject=subject, grade=grade))

        self._record({"kind": "unrecognised", "payload": payload})
        raise AssertionError("fake LLM: unrecognised prompt")

    def _record(self, record: dict) -> None:
        with self._lock:
            self.calls.append(record)
        if self._on_call:
            self._on_call(record)

    @staticmethod
    def _canned_scaffold(prompt: str, subject: str, grade: str) -> str:
        listing = re.search(
            r"Available Standards \(may use 1 or more\):\n(.*?)\n\nParent Constraints", prompt, re.S
        )
        standards = json.loads(listing.group(1))
        template = json.loads((FIXTURES / "scaffold.json").read_text(encoding="utf-8"))
        values = {"subject": subject, "grade": grade}
        return json.dumps(
            {
                "weekly_overview": _render(template["weekly_overview"], **values),
                "daily_assignments": [
                    {
                        "day": day,
                        "standard_ids": [standards[i % len(standards)]["id"]],
                        "focus": _render(template["focus"][day], **values),
                    }
                    for i, day in enumerate(DAYS)
                ],
            }
        )
