"""
Manages writing history to state
"""
import tkinter as tk
from enum import Enum
from typing import TYPE_CHECKING, Optional

from promptflow.src.dialogues.node_options import NodeOptions
from promptflow.src.nodes.node_base import NodeBase

from promptflow.src.state import State

if TYPE_CHECKING:
    from promptflow.src.flowchart import Flowchart

from promptflow.src.themes import monokai


class Role(Enum):
    """Three types of roles for openai chat"""

    USER = "user"
    SYSTEM = "system"
    ASSISTANT = "assistant"


class HistoryNode(NodeBase):
    """
    Injects history into state
    """

    node_color = monokai.PINK

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
        self.role_var = tk.StringVar(value=kwargs.get("role", Role.USER.value))
        self.role_item = self.canvas.create_text(
            center_x,
            center_y + 20,
            text=self.role_var.get(),
            font=("Arial", 10),
            fill="black",
        )
        self.items.append(self.role_item)
        self.bind_drag()

        self.options_popup: Optional[NodeOptions] = None

    def run_subclass(self, state: State) -> str:
        """
        Injects date into state
        """
        state.history.append({"role": self.role_var.get(), "content": state.result})
        return state.result

    def edit_options(self, event):
        self.options_popup = NodeOptions(
            self.canvas,
            {
                "role": self.role_var.get(),
            },
            {
                "role": [Role.USER.value, Role.SYSTEM.value, Role.ASSISTANT.value],
            },
        )
        self.canvas.wait_window(self.options_popup)
        result = self.options_popup.result
        # check if cancel
        if self.options_popup.cancelled:
            return
        self.role_var.set(result["role"])
        self.canvas.itemconfig(self.role_item, text=self.role_var.get())

    def serialize(self):
        return super().serialize() | {
            "role": self.role_var.get(),
        }
