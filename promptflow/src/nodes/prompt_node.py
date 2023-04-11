"""
Holds text which gets formatted with state data
"""
from typing import TYPE_CHECKING, Optional
import tkinter as tk
from promptflow.src.dialogues.text_input import TextInput
from promptflow.src.nodes.node_base import Node
from promptflow.src.state import State

from promptflow.src.text_data import TextData

if TYPE_CHECKING:
    from promptflow.src.flowchart import Flowchart


class PromptNode(Node):
    """
    Formats TextData with state data
    """

    node_color = "purple"

    def __init__(
        self,
        flowchart: "Flowchart",
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        label: str,
        prompt: Optional[TextData | dict] = None,
        **kwargs,
    ):
        super().__init__(
            flowchart,
            x1,
            y1,
            x2,
            y2,
            label,
            **kwargs,
        )
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2 + 10
        if prompt is None:
            prompt = TextData("Prompt", "", self.flowchart)
        if isinstance(prompt, dict):
            prompt = TextData.deserialize(prompt, self.flowchart)
        self.prompt = prompt
        self.prompt_item = self.canvas.create_text(
            center_x, center_y - 20, text=self.prompt.label
        )
        self.items.extend([self.prompt_item])
        self.canvas.tag_bind(self.prompt_item, "<Double-Button-1>", self.edit_prompt)

        self.text_window: Optional[TextInput] = None
        self.bind_drag()

    def run_subclass(self, state: State) -> str:
        """
        Formats TextData with state data
        """
        prompt = self.prompt.text.format(state=state)
        state.result = prompt
        return prompt

    def edit_prompt(self, _: tk.Event):
        """
        Create a text input window to edit the prompt.
        """
        self.text_window = TextInput(self.canvas, self.flowchart, self.prompt)
        self.text_window.set_callback(self.save_prompt)

    def save_prompt(self):
        """
        Write the prompt to the canvas.
        """
        if self.text_window is None:
            self.logger.warning("No text window to save")
            return
        self.prompt = self.text_window.get_text()
        self.canvas.itemconfig(self.prompt_item, text=self.prompt.label)
        self.text_window.destroy()

    def serialize(self) -> dict:
        return super().serialize() | {
            "prompt": self.prompt.serialize(),
        }

    @classmethod
    def deserialize(cls, flowchart: "Flowchart", data: dict) -> "PromptNode":
        return cls(
            flowchart,
            data["x1"],
            data["y1"],
            data["x2"],
            data["y2"],
            data["label"],
            prompt=data["prompt"],
            id=data["id"],
        )

    def cost(self, state: State):
        state.result = self.prompt.text
        return 0
