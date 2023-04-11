import random
from promptflow.src.nodes.node_base import Node
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from promptflow.src.flowchart import Flowchart


class RandomNode(Node):
    """
    Injects a random number (0-100) into state
    """

    node_color = "pink"

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
        super().__init__(
            flowchart,
            x1,
            y1,
            x2,
            y2,
            label,
            **kwargs,
        )

    def run_subclass(self, state) -> str:
        r = random.randint(0, 100)
        return str(r)
