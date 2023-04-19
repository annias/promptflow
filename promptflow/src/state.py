"""
State class definition
"""

from __future__ import annotations
from typing import Any
from promptflow.src.serializable import Serializable


class State(Serializable):
    """
    Holds state for flowchart flow
    Wraps a dict[str, str]
    """

    def __init__(self, **kwargs):
        self.snapshot: dict[str, str] = kwargs.get("state", {})
        self.history: list[dict[str, str]] = kwargs.get("history", [])
        self.result: str = kwargs.get("result", "")

    def __or__(self, __t: dict | State) -> "State":
        if isinstance(__t, dict):
            self.snapshot.update(__t)
        elif isinstance(__t, State):
            self.snapshot.update(__t.snapshot)
        return self

    def copy(self) -> State:
        """
        Create a new State object with a copy of the snapshot and history
        """
        return State(
            state=self.snapshot.copy(),
            history=self.history.copy(),
            result=self.result,
        )

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> State:
        return cls(**data)

    def serialize(self) -> dict[str, Any]:
        return {
            "snapshot": self.snapshot,
            "history": self.history,
            "result": self.result,
        }

    def __getitem__(self, key: str) -> str:
        """
        Makes access in f-strings easy
        """
        return self.snapshot.get(key, "")
