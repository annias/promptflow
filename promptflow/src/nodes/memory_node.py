"""
Handles state history and memory nodes
"""
from typing import TYPE_CHECKING
from promptflow.src.nodes.node_base import NodeBase
from promptflow.src.state import State
from promptflow.src.dialogues.node_options import NodeOptions
from promptflow.src.themes import monokai

if TYPE_CHECKING:
    from promptflow.src.flowchart import Flowchart


class MemoryNode(NodeBase):
    """
    Stores messages in a list
    """

    node_color = monokai.BLUE

    def __init__(
        self,
        flowchart: "Flowchart",
        center_x: float,
        center_y: float,
        label: str,
        **kwargs,
    ):
        super().__init__(
            flowchart,
            center_x,
            center_y,
            label,
            **kwargs,
        )
        self.canvas.tag_bind(self.item, "<Double-Button-1>", self.edit_options)
        self.options_popup = None

    def memory(self, state: State) -> list[dict[str, str]]:
        """
        Update state history
        """
        state.history = state.history
        return state.history

    def run_subclass(self, state) -> str:
        history_string = "\n".join(
            [
                *[
                    f"{message['role']}: {message['content']}"
                    for message in self.memory(state)
                ],
            ]
        )
        return history_string


class WindowedMemoryNode(MemoryNode):
    """
    Like MemoryNode, but only returns the last n messages
    """

    def __init__(
        self,
        flowchart: "Flowchart",
        center_x: float,
        center_y: float,
        label: str,
        window: int = 100,
        **kwargs,
    ):
        super().__init__(
            flowchart,
            center_x,
            center_y,
            label,
            **kwargs,
        )
        self.window = window

    def memory(self, state):
        state.history = state.history[-self.window :]
        return state.history

    def edit_options(self, event):
        self.options_popup = NodeOptions(
            self.canvas,
            {"window": self.window},
        )
        self.canvas.wait_window(self.options_popup)
        result = self.options_popup.result
        # check if cancel
        if self.options_popup.cancelled:
            return
        self.window = int(result["window"])

    def serialize(self):
        return super().serialize() | {"window": self.window}


class DynamicWindowedMemoryNode(MemoryNode):
    """
    Given a string, will return the last n messages until the string is found
    """

    def __init__(
        self,
        flowchart: "Flowchart",
        center_x: float,
        center_y: float,
        label: str,
        target: str = "",
        **kwargs,
    ):
        super().__init__(
            flowchart,
            center_x,
            center_y,
            label,
            **kwargs,
        )
        self.target = target

    def memory(self, state: State) -> list[dict[str, str]]:
        """
        Update state history
        """
        history = state.history
        for i, message in enumerate(history):
            if eval(self.target, {}, message):
                history = history[i:]
                break
        return history

    def edit_options(self, event):
        self.options_popup = NodeOptions(
            self.canvas,
            {"target": self.target},
        )
        self.canvas.wait_window(self.options_popup)
        result = self.options_popup.result
        # check if cancel
        if self.options_popup.cancelled:
            return
        self.target = result["target"]

    def serialize(self):
        return super().serialize() | {"target": self.target}
