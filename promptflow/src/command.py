"""
Handles undo, redo, and history of commands.
"""
from abc import ABC, abstractmethod

from promptflow.src.flowchart import Flowchart
from promptflow.src.nodes.node_base import NodeBase
from promptflow.src.connectors.connector import Connector


class Command(ABC):
    """
    Represents a command that can be executed and undone in the GUI.
    """

    @abstractmethod
    def execute(self):
        """
        Handles the execution of the command.
        """

    @abstractmethod
    def undo(self):
        """
        Undoes the command.
        """


class AddNodeCommand(Command):
    """
    Handles the addition of a node to the flowchart.
    """

    def __init__(self, flowchart: Flowchart, node: NodeBase):
        self.flowchart = flowchart
        self.node = node

    def execute(self):
        self.flowchart.add_node(self.node)

    def undo(self):
        self.node.delete()


class RemoveNodeCommand(Command):
    """
    Handles the removal of a node from the flowchart.
    """

    def __init__(self, flowchart: Flowchart, node: NodeBase):
        self.flowchart = flowchart
        self.node = node

    def execute(self):
        self.node.delete()

    def undo(self):
        self.flowchart.add_node(self.node)


class AddConnectionCommand(Command):
    """
    Handles the addition of a connection between nodes to the flowchart
    """

    def __init__(self, flowchart: Flowchart, connector: Connector):
        self.flowchart = flowchart
        self.connector = connector

    def execute(self):
        self.flowchart.add_connector(self.connector)

    def undo(self):
        self.connector.delete()


class RemoveConnectionCommand(Command):
    """
    Handles the removal of a connection between nodes from the flowchart
    """

    def __init__(self, flowchart: Flowchart, connector: Connector):
        self.flowchart = flowchart
        self.connector = connector

    def execute(self):
        self.connector.delete()

    def undo(self):
        self.flowchart.add_connector(self.connector)


class CommandManager:
    """
    Holds the state of the command history acts as an interface for executing, undoing, and
    redoing commands.
    """

    def __init__(self):
        self._history: list[Command] = []
        self._index = 0

    def execute(self, command: Command):
        """
        Executes a command and adds it to the history.
        """
        command.execute()
        self._history.insert(self._index, command)
        self._index += 1

    def undo(self):
        """
        Undoes the last command in the history and moves the history pointer back one.
        """
        if self._index < 0:
            return
        self._history[self._index - 1].undo()
        self._index -= 1

    def redo(self):
        """
        Redoes the last command in the history and moves the history pointer forward one.
        """
        if self._index > len(self._history) - 1:
            return
        self._history[self._index].execute()
        self._index += 1
