"""
Base class for all nodes
"""
from typing import TYPE_CHECKING, Optional
import tkinter as tk
import os
from abc import ABC, abstractmethod
import logging
import uuid
import openai
from promptflow.src.state import State
from promptflow.src.serializable import Serializable
from promptflow.src.themes import monokai
import customtkinter

if TYPE_CHECKING:
    from promptflow.src.flowchart import Flowchart
    from promptflow.src.connectors.connector import Connector

openai.api_key = os.environ["OPENAI_API_KEY"]


class NodeBase(Serializable, ABC):
    """
    Represents a node in the flowchart, which could be a prompt, an llm, traditional code, etc.
    """

    node_color = monokai.WHITE
    size_px: int = 50  # arbitrary default size

    def __init__(
        self,
        flowchart: "Flowchart",
        center_x: float,
        center_y: float,
        label: str,
        **kwargs,
    ):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Creating node %s", label)
        self.flowchart = flowchart
        self.id: str = kwargs.get("id") or str(uuid.uuid1())
        self.canvas = flowchart.canvas

        self.item = self.draw_shape(center_x, center_y)
        self.canvas.tag_bind(self.item, "<ButtonPress-1>", self.start_drag)
        self.canvas.tag_bind(self.item, "<ButtonRelease-1>", self.stop_drag)
        self.canvas.tag_bind(self.item, "<B1-Motion>", self.on_drag)
        # right click menu
        self.canvas.tag_bind(self.item, "<Button-3>", self.show_menu)
        self._label = label
        self.input_connectors: list[Connector] = []
        self.output_connectors: list[Connector] = []
        self.visited = False  # Add a visited attribute to keep track of visited nodes

        # create the label
        self.center_x = center_x
        self.center_y = center_y
        self.label_item = self.canvas.create_text(center_x, center_y, text=label)
        self.canvas.tag_bind(self.label_item, "<Double-Button-1>", self.edit_label)

        self.add_connector_button = customtkinter.CTkButton(
            self.canvas, text="+", command=self.begin_add_connector, width=38,
            corner_radius=4, border_width=2, border_color="black",
        )
        self.add_connector_item = self.canvas.create_window(
            center_x + 23, center_y + 68, window=self.add_connector_button
        )

        self.delete_button = customtkinter.CTkButton(
            self.canvas, text="x", command=self.delete, width=38,
            corner_radius=4, border_width=2, border_color="black", 
        )
        self.delete_item = self.canvas.create_window(
            center_x - 23, center_y + 68, window=self.delete_button
        )

        self.items = [
            self.label_item,
            self.delete_item,
            self.add_connector_item,
            self.item,
        ]

        self.bind_drag()
        self.canvas.tag_bind(self.item, "<Double-Button-1>", self.edit_options)

        self.buttons = [self.delete_button, self.add_connector_button]

        self.label_entry: Optional[customtkinter.CTkEntry] = None

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, NodeBase):
            return self.id == __o.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def connectors(self) -> list["Connector"]:
        """All connectors attached to this node"""
        return self.input_connectors + self.output_connectors

    @classmethod
    def deserialize(cls, flowchart: "Flowchart", data: dict):
        return cls(
            flowchart,
            **data,
        )

    @property
    def label(self) -> str:
        """Name of the node. Used for snapshotting."""
        return self._label

    @label.setter
    def label(self, label: str):
        self._label = label
        self.canvas.itemconfig(self.label_item, text=label)

    def get_center(
        self, offset_x: float = 0, offset_y: float = 0
    ) -> tuple[float, float]:
        """
        Node is defined by its top left and bottom right coordinates.
        This function returns the center of the node based on those coordinates.
        """
        center_x = (
            self.canvas.coords(self.item)[0] + self.canvas.coords(self.item)[2]
        ) / 2 + offset_x
        center_y = (
            self.canvas.coords(self.item)[1] + self.canvas.coords(self.item)[3]
        ) / 2 + offset_y
        return center_x, center_y

    def edit_label(self, _: tk.Event):
        """
        Start editing the label of the node.
        """
        self.canvas.delete(self.label_item)
        self.items.remove(self.label_item)
        center_x, center_y = self.get_center()
        self.label_entry = customtkinter.CTkEntry(self.canvas)
        self.label_entry.insert(0, self.label)
        self.label_entry.bind("<Return>", self.finish_edit_label)
        self.label_entry.bind("<FocusOut>", self.finish_edit_label)
        self.canvas.create_window(center_x, center_y, window=self.label_entry)

    def finish_edit_label(self, _: tk.Event):
        """
        Called when the user is done editing the label.
        Creates a new label item and destroys the entry.
        """
        if self.label_entry is None:
            return
        self.label = self.label_entry.get()
        self.label_entry.destroy()
        center_x, center_y = self.get_center()
        self.label_item = self.canvas.create_text(center_x, center_y, text=self.label)
        self.items.append(self.label_item)
        self.canvas.tag_bind(self.label_item, "<Double-Button-1>", self.edit_label)
        self.bind_drag()

    def begin_add_connector(self):
        """
        Start adding a connector to this node.
        Creates a temporary connector that follows the mouse.
        """
        self.flowchart.begin_add_connector(self)

    def start_drag(self, event: tk.Event):
        """
        Update the flowchart's selected node and start dragging the node by
        updating the node's x and y coordinates.
        """
        self.flowchart.selected_element = self
        self.center_x = event.x
        self.center_y = event.y

    def on_drag(self, event: tk.Event):
        """
        Continuously update the node's position while dragging.
        Update all connectors to follow the node.
        """
        delta_x = event.x - self.center_x
        delta_y = event.y - self.center_y
        for item in self.items:
            self.canvas.move(item, delta_x, delta_y)
        self.center_x = event.x
        self.center_y = event.y
        for connector in self.connectors:
            connector.update()

    def stop_drag(self, _: tk.Event):
        """
        Required to be able to drag the node.
        """

    @abstractmethod
    def run_subclass(self, state) -> str:
        """
        Code that will be run when the node is executed.
        """

    def run_node(self, state: State) -> str:
        """
        Run the node and all nodes connected to it
        Handles setting the snapshot and returning the output.
        """
        state.snapshot[self.label] = state.snapshot.get(self.label, "")
        output: str = self.run_subclass(state)
        state.snapshot[self.label] = output
        return output

    def serialize(self):
        return {
            "id": self.id,
            "label": self.label,
            "center_x": self.center_x,
            "center_y": self.center_y,
            "classname": self.__class__.__name__,
        }

    def delete(self):
        """
        Delete the node and all connectors attached to it.
        """
        self.logger.info(f"Deleting node {self.label}")
        self.flowchart.remove_node(self)
        for item in self.items:
            self.logger.debug(f"Deleting item {item}")
            self.canvas.delete(item)

        for button in self.buttons:
            button.destroy()

    def copy(self) -> "NodeBase":
        """
        Create a copy of the node, without copying the connectors.
        """
        self.logger.info(f"Copying node {self.label}")
        data = self.serialize()
        data["id"] = uuid.uuid4()
        data["label"] = f"{data['label']} copy"
        new_node = self.deserialize(self.flowchart, data)
        return new_node

    def show_menu(self, event: tk.Event):
        """
        Right-click convenience menu.
        """
        menu = tk.Menu(self.canvas, tearoff=0)
        menu.add_command(label="Delete", command=self.delete)
        menu.add_command(label="Copy", command=self.copy)
        menu.post(event.x_root, event.y_root)

    def get_children(self) -> list["NodeBase"]:
        """
        Return all child nodes of this node.
        """
        return [connector.node2 for connector in self.output_connectors]

    def draw_shape(self, center_x: float, center_y: float):
        """
        Takes the coordinates of the top left and bottom right corners of the node
        Draws the shape of the node
        Rectangles by default
        """
        return self.canvas.create_rectangle(
            center_x - self.size_px,
            center_y - self.size_px,
            center_x + self.size_px,
            center_y + self.size_px,
            fill=self.node_color,
            outline="black",
            tags="node",
        )

    def bind_drag(self):
        """
        Binds the drag events to all the node's items
        Allows behavior like dragging the node by its label
        """
        for item in self.items:
            self.canvas.tag_bind(item, "<ButtonPress-1>", self.start_drag)
            self.canvas.tag_bind(item, "<ButtonRelease-1>", self.stop_drag)
            self.canvas.tag_bind(item, "<B1-Motion>", self.on_drag)

    def edit_options(self, event):
        """
        Callback for the edit options button.
        Doesn't do anything by default.
        """

    def cost(self, state: State) -> float:
        """
        The cost of running this node in dollars.
        Adds the label to the snapshot as well for
        prompt formatting.
        """
        state.snapshot[self.label] = ""
        return 0.0
