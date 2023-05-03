"""
Nodes that get run time input from the user
"""
import tkinter.simpledialog

from promptflow.src.nodes.node_base import NodeBase


class InputNode(NodeBase):
    """
    Node that prompts the user for input
    """

    def run_subclass(self, state, console):
        # since we're multithreaded, we need to send a message to the main thread
        root = tkinter.Tk()
        root.withdraw()
        return tkinter.simpledialog.askstring(
            self.label, "Enter a value for this input:", parent=root
        )
