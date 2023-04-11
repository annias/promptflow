"""
Special node that prompts the user for input
Also signals the start of the flowchart
"""
from typing import TYPE_CHECKING
import uuid
from promptflow.src.nodes.node_base import Node

if TYPE_CHECKING:
    from promptflow.src.flowchart import Flowchart


class StartNode(Node):
    """
    First node in the flowchart
    """

    node_color = "light blue"

    def __init__(
        self,
        flowchart: "Flowchart",
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        label: str,
        **kwargs,
    ):
        # make sure there is only one start node
        for node in flowchart.nodes:
            if isinstance(node, StartNode):
                raise ValueError("Only one start node is allowed")
        
        super().__init__(flowchart, x1, y1, x2, y2, label, **kwargs)

    @staticmethod
    def deserialize(flowchart: "Flowchart", data: dict):
        return StartNode(
            flowchart,
            data["x1"],
            data["y1"],
            data["x2"],
            data["y2"],
            data["label"],
            id=data.get("id", str(uuid.uuid4())),
        )

    def run_subclass(self, state):
        return ""
        
    def draw_shape(self, x1, y1, x2, y2):
        return self.canvas.create_oval(
            x1, y1, x2, y2, fill=self.node_color, outline="black"
        )


