"""
Node to run arbitrary Python code.
"""

from typing import TYPE_CHECKING, Optional
from abc import ABC
import tkinter as tk

from promptflow.src.nodes.node_base import Node
from promptflow.src.state import State
from promptflow.src.text_data import TextData
from promptflow.src.dialogues.code_input import CodeInput
from promptflow.src.themes import monokai

if TYPE_CHECKING:
    from promptflow.src.flowchart import Flowchart


DEFAULT_FUNC_TEMPLATE = """def main(state):
\treturn True
"""


class FuncNode(Node, ABC):
    """
    Run arbitrary Python code.
    """

    node_color = monokai.yellow

    def __init__(
        self,
        flowchart: "Flowchart",
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        label: str,
        func: Optional[TextData] = None,
        **kwargs,
    ):
        super().__init__(flowchart, x1, y1, x2, y2, label, **kwargs)
        self.func = func
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2 + 10
        if not self.func:
            self.func = TextData("func", DEFAULT_FUNC_TEMPLATE, flowchart)
        if isinstance(func, dict):
            self.func = TextData.deserialize(func, self.flowchart)
        if self.func.text == "":
            self.func.text = DEFAULT_FUNC_TEMPLATE
        # convert function to string
        self.functext = self.func.label
        self.func_item = self.canvas.create_text(center_x, center_y, text=self.functext)
        self.items.append(self.func_item)
        self.canvas.tag_bind(self.func_item, "<Double-Button-1>", self.edit_func)
        self.bind_drag()
        self.text_window: Optional[CodeInput] = None

    def run_subclass(self, state: State):
        """
        Evaluate the Python function and return the result.
        """
        loc = state.copy() | {"result": None}
        try:
            exec(self.func.text, dict(globals()), loc.snapshot)
        except Exception as node_exception:
            raise RuntimeError(
                f"Error in function: {node_exception}"
            ) from node_exception
        if "main" not in loc.snapshot:
            raise NameError("Function must have a main() function")
        # todo make this less hacky
        result = loc.snapshot["main"](state)  # type: ignore
        return result

    def serialize(self):
        return super().serialize() | {
            "func": {
                "label": self.func.label,
                "text": self.func.text,
            }
        }

    @classmethod
    def deserialize(cls, flowchart: "Flowchart", data: dict):
        node = super().deserialize(flowchart, data)
        node.func = TextData(data["func"]["label"], data["func"]["text"], flowchart)
        return node

    def edit_func(self, _: tk.Event):
        """Start editing the function."""
        self.text_window = CodeInput(self.canvas, self.flowchart, self.func)
        self.text_window.set_callback(self.save_func)

    def save_func(self):
        """Save the function."""
        if self.text_window is None:
            self.logger.warning("No text window to save")
            return
        self.func = self.text_window.get_text()
        self.canvas.itemconfig(self.func_item, text=self.func.label)
        self.canvas.update()

    def draw_shape(self, x1, y1, x2, y2):
        """
        Diamond shape
        """
        return self.canvas.create_polygon(
            [
                x1,
                (y1 + y2) / 2,
                (x1 + x2) / 2,
                y2,
                x2,
                (y1 + y2) / 2,
                (x1 + x2) / 2,
                y1,
            ],
            fill=self.node_color,
            outline="black",
        )
