"""
Nodes that get run time input from the user
"""
import tkinter
import customtkinter

from promptflow.src.nodes.node_base import NodeBase


class InputNode(NodeBase):
    """
    Node that prompts the user for input
    """

    def before(self, state, console):
        dialog = customtkinter.CTkInputDialog(
            text="Enter a value for this input:", title=self.label
        )
        return {"input": dialog.get_input()}

    def run_subclass(self, before_result, state, console):
        return before_result["input"]
