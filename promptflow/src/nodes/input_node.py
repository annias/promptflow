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

    def run_subclass(self, state, console):
        # since we're multithreaded, we need to send a message to the main thread
        root = tkinter.Tk()
        root.withdraw()
        # dialog = customtkinter.CTkInputDialog(text="Enter a value for this input:", title=self.label)
        dialog = tkinter.simpledialog.askstring(
            prompt="Enter a value for this input:", title=self.label, parent=root
        )
        # response = dialog.get_input()
        # dialog.after(1, dialog.destroy)
        return dialog