"""
Convenience node for injecting date into state
"""
import datetime
from typing import TYPE_CHECKING
from promptflow.src.nodes.node_base import Node

if TYPE_CHECKING:
    from promptflow.src.flowchart import Flowchart


class DateNode(Node):
    """
    Injects date into state
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
        """
        Injects date into state
        """
        date_time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        self.logger.info("Date node %s has state %s", self.label, state)
        return date_time
