"""
Handles reusable text data in the flowchart
"""
from typing import TYPE_CHECKING
from promptflow.src.serializable import Serializable

if TYPE_CHECKING:
    from promptflow.src.flowchart import Flowchart


class TextData(Serializable):
    """
    Class for storing reusable text data in the flowchart
    """

    def __init__(self, label: str, text: str, flowchart: "Flowchart"):
        self.logger = flowchart.logger
        if label == "":
            label = "Untitled"
            self.logger.error(
                "TextData label cannot be empty; will be an Exception in the future"
            )
        self._label = label
        self._text = text
        self.flowchart = flowchart
        self.flowchart.register_text_data(self)

    @property
    def label(self) -> str:
        """
        The name of the text data; used to reference it in the flowchart
        """
        return self._label

    @label.setter
    def label(self, value: str):
        self._label = value
        self.flowchart.register_text_data(self)

    @property
    def text(self) -> str:
        """
        The text data itself; can be formatted with state data
        """
        return self._text

    @text.setter
    def text(self, value: str):
        self._text = value
        self.flowchart.register_text_data(self)

    def serialize(self) -> dict[str, str]:
        return {
            "label": self.label,
            "text": self.text,
        }

    @classmethod
    def deserialize(cls, data: dict[str, str], flowchart: "Flowchart") -> "TextData":
        return cls(data["label"], data.get("text", ""), flowchart)
