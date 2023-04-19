"""
Nodes for performing tests on the model.
"""
from typing import TYPE_CHECKING, Optional
from promptflow.src.dialogues.node_options import NodeOptions
from promptflow.src.dialogues.text_input import TextInput

from promptflow.src.state import State
from promptflow.src.nodes.node_base import Node
from promptflow.src.text_data import TextData
from promptflow.src.themes import monokai

if TYPE_CHECKING:
    from promptflow.src.flowchart import Flowchart


class AssertNode(Node):
    """
    Runs an assertion on the result of the previous node
    """

    node_color = monokai.comments

    def __init__(
        self,
        flowchart: "Flowchart",
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        label: str,
        assertion: Optional[TextData] = None,
        **kwargs
    ):
        super().__init__(flowchart, x1, y1, x2, y2, label, **kwargs)
        if assertion is None:
            assertion = TextData("Assertion", "True", self.flowchart)
        self.assertion = assertion
        self.options_popup: Optional[NodeOptions] = None

    def run_subclass(self, state: State) -> str:
        assert eval(self.assertion.text, globals(), state.snapshot), "Assertion failed"
        return state.result

    def edit_options(self, event):
        self.options_popup = NodeOptions(
            self.canvas, {"Assertion": self.assertion.text}
        )
        self.canvas.wait_window(self.options_popup)
        result = self.options_popup.result
        # check if cancel
        if self.options_popup.cancelled:
            return
        self.assertion.text = result["Assertion"]


class LoggingNode(Node):
    """
    Logs user-defined string to the console.
    """

    text_window: Optional[TextInput] = None

    def __init__(
        self,
        flowchart: "Flowchart",
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        label: str,
        debug_str: Optional[TextData] = None,
        **kwargs
    ):
        super().__init__(flowchart, x1, y1, x2, y2, label, **kwargs)
        if debug_str is None:
            debug_str = TextData("Debug String", "{state.result}", self.flowchart)
        self.debug_str = debug_str
        self.canvas.tag_bind(self.item, "<Double-Button-1>", self.edit_string)

    def run_subclass(self, state: State) -> str:
        debug_str = self.debug_str.text.format(state=state)
        self.logger.info(debug_str)
        return state.result  # return the result of the previous node

    def edit_string(self, event):
        self.text_window = TextInput(self.canvas, self.flowchart, self.debug_str)
        self.text_window.set_callback(self.save_prompt)

    def save_prompt(self, text):
        self.debug_str.text = text
        self.text_window.destroy()
        self.text_window = None
