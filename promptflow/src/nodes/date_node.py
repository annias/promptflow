"""
Convenience node for injecting date into state
"""
import datetime
from typing import TYPE_CHECKING
from promptflow.src.nodes.node_base import NodeBase
from promptflow.src.themes import monokai

if TYPE_CHECKING:
    from promptflow.src.flowchart import Flowchart


class DateNode(NodeBase):
    """
    Injects date into state
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

    def run_subclass(self, state) -> str:
        """
        Injects date into state
        """
        date_time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        self.logger.info("Date node %s has state %s", self.label, state)
        return date_time
