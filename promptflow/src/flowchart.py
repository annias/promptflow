"""
This module contains the Flowchart class, which manages the nodes and connectors of a flowchart.
"""
from __future__ import annotations
import logging
import tkinter as tk
import tkinter.scrolledtext
import threading
from queue import Queue
from typing import Any, Optional
from promptflow.src.nodes.node_base import NodeBase
from promptflow.src.nodes.start_node import InitNode, StartNode
from promptflow.src.nodes.input_node import InputNode
from promptflow.src.nodes.func_node import FuncNode
from promptflow.src.nodes.llm_node import LLMNode
from promptflow.src.nodes.date_node import DateNode
from promptflow.src.nodes.random_number import RandomNode
from promptflow.src.nodes.history_node import HistoryNode
from promptflow.src.nodes.dummy_llm_node import DummyNode
from promptflow.src.nodes.prompt_node import PromptNode
from promptflow.src.nodes.memory_node import (
    MemoryNode,
    WindowedMemoryNode,
    DynamicWindowedMemoryNode,
)
from promptflow.src.nodes.embedding_node import (
    EmbeddingInNode,
    EmbeddingQueryNode,
    EmbeddingsIngestNode,
)
from promptflow.src.nodes.test_nodes import AssertNode
from promptflow.src.nodes.env_node import EnvNode, ManualEnvNode
from promptflow.src.nodes.audio_node import WhispersNode, ElevenLabsNode
from promptflow.src.connectors.connector import Connector
from promptflow.src.connectors.partial_connector import PartialConnector
from promptflow.src.state import State
from promptflow.src.text_data import TextData


class Flowchart:
    """
    Holds the nodes and connectors of a flowchart.
    """

    def __init__(self, canvas: tk.Canvas, init_nodes: bool = True):
        self.canvas = canvas
        self.nodes: list[NodeBase] = []
        self.connectors: list[Connector] = []
        self.text_data_registry: dict[str, TextData] = {}
        self.logger = logging.getLogger(__name__)

        self._selected_element: Optional[NodeBase | Connector] = None
        self._partial_connector: Optional[PartialConnector] = None
        self.is_dirty = False
        self.is_running = False

        if init_nodes:
            self.add_node(InitNode(self, 70, 100, "Init"))
            self.add_node(StartNode(self, 70, 300, "Start"))

    @classmethod
    def deserialize(cls, canvas: tk.Canvas, data: dict[str, Any]):
        """
        Deserialize a flowchart from a dict onto a canvas
        """
        flowchart = cls(canvas, init_nodes=False)
        for node_data in data["nodes"]:
            node = eval(node_data["classname"]).deserialize(flowchart, node_data)
            flowchart.add_node(node)
        for connector_data in data["connectors"]:
            node1 = flowchart.find_node(connector_data["node1"])
            node2 = flowchart.find_node(connector_data["node2"])
            connector = Connector(
                canvas, node1, node2, connector_data.get("condition", "")
            )
            flowchart.add_connector(connector)
        flowchart.reset_node_colors()
        canvas.update()
        flowchart.is_dirty = False
        return flowchart

    @property
    def selected_element(self) -> Optional[NodeBase | Connector]:
        """
        Return last touched node
        """
        return self._selected_element

    @selected_element.setter
    def selected_element(self, elem: Optional[NodeBase | Connector]):
        self.logger.info("Selected element changed to %s", elem.label if elem else None)
        # deselect previous node
        if self._selected_element:
            # configure to have solid border
            self.canvas.itemconfig(self._selected_element.item, width=2)
        # select new node
        if elem:
            self.canvas.itemconfig(elem.item, width=4)
        self._selected_element = elem

    @property
    def start_node(self) -> StartNode:
        """
        Find and return the node with the class StartNode
        """
        start_nodes = [node for node in self.nodes if isinstance(node, StartNode)]
        if len(start_nodes) == 0:
            raise ValueError("No start node found")

        if len(start_nodes) == 1:
            return start_nodes[0]

        # sort by number of input connectors
        start_nodes.sort(key=lambda node: len(node.input_connectors))
        return start_nodes[0]

    @property
    def init_node(self) -> Optional[InitNode]:
        """
        Find and returns the single-run InitNode
        """
        try:
            return [node for node in self.nodes if isinstance(node, InitNode)][0]
        except IndexError:
            return None

    def find_node(self, node_id: str) -> NodeBase:
        """
        Given a node uuid, find and return the node
        """
        for node in self.nodes:
            if node.id == node_id:
                return node
        raise ValueError(f"No node with id {node_id} found")

    def add_node(self, node: NodeBase):
        """
        Safely insert a node into the flowchart
        """
        while node in self.nodes:
            self.logger.debug("Duplicate node found, adding (copy) to label...")
            node.label += " (copy)"
        self.nodes.append(node)
        self.selected_element = node
        self.is_dirty = True

    def add_connector(self, connector: Connector):
        """
        Safely insert a connector into the flowchart
        """
        # check for duplicate connectors
        self.logger.debug(f"Adding connector {connector}")
        self.connectors.append(connector)
        self.selected_element = connector
        self.is_dirty = True

    def initialize(
        self, state: State, console: tkinter.scrolledtext.ScrolledText
    ) -> State:
        """
        Initialize the flowchart
        """
        self.is_running = True
        init_node: Optional[InitNode] = self.init_node
        if not init_node or init_node.run_once:
            console.insert(tk.END, "\n[System: Already initialized]\n")
            console.see(tk.END)
            return state
        queue: list[NodeBase] = Queue()
        queue.put(init_node)
        return self.run(state, console, queue)

    def run(
        self,
        state: State,
        console: tkinter.scrolledtext.ScrolledText,
        queue: Queue[NodeBase] = None,
    ) -> State:
        """
        Given a state, run the flowchart and update the state
        """
        self.logger.info("Running flowchart")
        if not queue:
            queue = Queue()
            queue.put(self.start_node)
            self.is_running = True
        if queue.empty() and not self.is_running:
            queue.put(self.start_node)
            self.is_running = True
        state = state or State()

        if not queue.empty():
            if not self.is_running:
                self.reset_node_colors()
                console.insert(tk.END, "\n[System: Stopped]\n")
                console.see(tk.END)
                self.is_running = False
                return state
            cur_node: NodeBase = queue.get()
            # turn node light yellow while running
            cur_node.canvas.itemconfig(cur_node.item, fill="#ffffcc")
            cur_node.canvas.update()
            self.logger.info(f"Running node {cur_node.label}")
            before_result = cur_node.before(state, console)
            try:
                thread = threading.Thread(
                    target=cur_node.run_node,
                    args=(before_result, state, console),
                    daemon=True,
                )
                thread.start()
                while thread.is_alive():
                    self.canvas.update()
                thread.join()
                output = state.result
            except Exception as node_err:
                self.logger.error(f"Error running node {cur_node.label}: {node_err}")
                if console:
                    console.insert(
                        tk.END, f"[ERROR]{cur_node.label}: {node_err}" + "\n"
                    )
                    console.see(tk.END)
                return state
            if console:
                console.insert(tk.END, f"{cur_node.label}: {output}" + "\n")
                console.see(tk.END)
            self.logger.info(f"Node {cur_node.label} output: {output}")
            # turn node light green
            cur_node.canvas.itemconfig(cur_node.item, fill="#ccffcc")
            cur_node.canvas.update()

            if output is None:
                self.logger.info(
                    f"Node {cur_node.label} output is None, stopping execution"
                )
                self.reset_node_colors()
                console.insert(tk.END, "\n[System: Done]\n")
                console.see(tk.END)
                return state

            for connector in cur_node.output_connectors:
                if connector.condition.text.strip():
                    # evaluate condition and only add node2 to queue if condition is true
                    exec(
                        connector.condition.text.strip(),
                        dict(globals()),
                        state.snapshot,
                    )
                    try:
                        cond = state.snapshot["main"](state)  # type: ignore
                    except Exception as node_err:
                        self.logger.error(f"Error evaluating condition: {node_err}")
                        if console:
                            console.insert(
                                tk.END, f"[ERROR]{cur_node.label}: {node_err}" + "\n"
                            )
                            console.see(tk.END)
                        break
                    self.logger.info(
                        f"Condition {connector.condition} evaluated to {cond}"
                    )
                else:
                    cond = True
                if cond:
                    # if connector.node2 not in queue:
                    if queue.queue.count(connector.node2) == 0:
                        queue.put(connector.node2)
                        self.canvas.master.after(0, self.run, state, console, queue)
                    self.logger.info(f"Added node {connector.node2.label} to queue")

        if queue.empty():
            self.reset_node_colors()
            console.insert(tk.END, "\n[System: Done]\n")
            console.see(tk.END)
            self.is_running = False
            return state

    def begin_add_connector(self, node: NodeBase):
        """
        Start adding a connector from the given node.
        """
        if self._partial_connector:
            self._partial_connector.delete(None)
        self._partial_connector = PartialConnector(self, node)
        self.canvas.bind("<Motion>", self._partial_connector.update)
        self.canvas.bind("<Button-1>", self._partial_connector.finish)
        self.canvas.bind("<Escape>", self._partial_connector.delete)

    def serialize(self):
        """
        Write the flowchart to a dictionary
        """
        data: dict[str, Any] = {}
        data["nodes"] = []
        for node in self.nodes:
            data["nodes"].append(node.serialize())
        data["connectors"] = []
        for connector in self.connectors:
            data["connectors"].append(connector.serialize())
        return data

    def remove_node(self, node: NodeBase):
        """
        Remove a node and all connectors connected to it.
        """
        self.logger.info("Removing node {node}")
        if node in self.nodes:
            self.nodes.remove(node)
        # remove all connectors connected to this node
        for other_node in self.nodes:
            for connector in other_node.connectors:
                if connector.node1 == node or connector.node2 == node:
                    connector.delete()
                    if connector in other_node.input_connectors:
                        other_node.input_connectors.remove(connector)
                    if connector in other_node.output_connectors:
                        other_node.output_connectors.remove(connector)
        for connector in self.connectors:
            if connector.node1 == node or connector.node2 == node:
                connector.delete()
        self.is_dirty = True

    def clear(self):
        """
        Clear the flowchart.
        """
        self.logger.info("Clearing")
        for node in self.nodes:
            node.delete()
        self.nodes = []
        for connector in self.connectors:
            connector.delete()
        self.connectors = []
        self.canvas.delete("all")
        self.canvas.update()
        self.is_dirty = True

    def reset_node_colors(self):
        """
        Set all node colors to their default color.
        """
        for node in self.nodes:
            self.canvas.itemconfig(node.item, fill=node.node_color)

    def register_text_data(self, text_data: TextData):
        """
        On creation of a TextData object, register it with the flowchart.
        """
        if text_data.label:
            self.logger.debug(f"Registering text data {text_data.label}")
            self.text_data_registry[text_data.label] = text_data

    def cost(self, state: State):
        """
        Return the cost of the flowchart.
        """
        cost = 0
        for node in self.nodes:
            cost += node.cost(state)
        return cost

    def to_mermaid(self):
        """
        Return a mermaid string representation of the flowchart.
        """
        mermaid_str = "graph TD\n"
        for node in self.nodes:
            mermaid_str += f"{node.id}({node.label})\n"
        for connector in self.connectors:
            if connector.condition_label:
                mermaid_str += f"{connector.node1.id} -->|{connector.condition_label}| {connector.node2.id}\n"
            else:
                mermaid_str += f"{connector.node1.id} --> {connector.node2.id}\n"

        return mermaid_str
