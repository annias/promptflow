import random
from promptflow.src.nodes.node_base import NodeBase
from promptflow.src.themes import monokai

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from promptflow.src.flowchart import Flowchart


class RandomNode(NodeBase):
    """
    Injects a random number (0-100) into state
    """

    node_color = monokai.pink

    def run_subclass(self, state) -> str:
        r = random.randint(0, 100)
        return str(r)
