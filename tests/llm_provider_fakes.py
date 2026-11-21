"""Scriptable in-memory Provider for tests of the model layer."""

from llm import Completion, CompletionRequest, Usage


class ScriptedProvider:
    """Returns/raises the scripted items in order; records every request."""

    def __init__(self, *script, cost=0.001):
        self.script = list(script)
        self.requests: list[CompletionRequest] = []
        self.cost = cost

    def complete(self, request: CompletionRequest) -> Completion:
        self.requests.append(request)
        item = self.script.pop(0)
        if isinstance(item, BaseException):
            raise item
        return Completion(
            text=item,
            model=request.model,
            usage=Usage(prompt_tokens=10, completion_tokens=5, total_tokens=15, cost_usd=self.cost),
            latency_s=0.01,
        )
