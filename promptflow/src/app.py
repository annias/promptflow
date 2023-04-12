"""
Primary application class. This class is responsible for creating the
window, menu, and canvas. It also handles the saving and loading of
flowcharts.
"""
import json
import logging
import tkinter as tk
from tkinter import ttk
import sv_ttk
import tkinter.filedialog
import tkinter.scrolledtext
import tkinter.messagebox
import os
from typing import Optional
import zipfile
from PIL import ImageGrab

from promptflow.src.flowchart import Flowchart
from promptflow.src.nodes.date_node import DateNode
from promptflow.src.nodes.node_base import Node
from promptflow.src.nodes.start_node import InitNode, StartNode
from promptflow.src.nodes.prompt_node import PromptNode
from promptflow.src.nodes.func_node import FuncNode
from promptflow.src.nodes.llm_node import LLMNode
from promptflow.src.nodes.random_number import RandomNode
from promptflow.src.nodes.history_node import HistoryNode
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
from promptflow.src.nodes.input_node import InputNode
from promptflow.src.nodes.test_nodes import AssertNode
from promptflow.src.options import Options
from promptflow.src.resizing_canvas import ResizingCanvas
from promptflow.src.nodes.dummy_llm_node import DummyNode
from promptflow.src.state import State


class App:
    """
    Primary application class. This class is responsible for creating the
    window, menu, and canvas. It also handles the saving and loading of
    flowcharts.
    """

    def __init__(self, initial_state: State, options: Options):
        self.root = tk.Tk()
        # self.style = ttk.Style(self.root)
        # self.style.theme_use("clam")
        sv_ttk.set_theme("dark")

        self.loading_popup = self.show_loading_popup("Starting app...")

        self.initial_state = initial_state
        self.logging_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.DEBUG, format=self.logging_fmt)
        self.logger.info("Creating app")

        # Build the core components

        self.paned_window = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.canvas = ResizingCanvas(
            self.paned_window,
            width=options.width,
            height=options.height,
        )
        self.flowchart = Flowchart(self.canvas)
        self.current_file = "Untitled"

        # scrolling text meant to simulate a console
        self.output_console = tkinter.scrolledtext.ScrolledText(
            self.paned_window, height=8, width=100
        )

        # register on close behavior
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # create the menu
        self.menu = tk.Menu(self.canvas)
        self.menubar = tk.Menu(self.menu, tearoff=0)

        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(label="Save Flowchart...", command=self.save_as)
        self.file_menu.add_command(label="Load Flowchart...", command=self.load_from)
        self.export_menu = tk.Menu(self.file_menu, tearoff=0)
        self.export_menu.add_command(label="To Mermaid", command=self.export_to_mermaid)
        self.file_menu.add_cascade(label="Export", menu=self.export_menu)
        self.menubar.add_cascade(label="File", menu=self.file_menu)

        # create an add menu for each type of node
        self.add_menu = tk.Menu(self.menubar, tearoff=0)
        self.add_menu.add_command(
            label="Start - First node in main loop", command=self.create_add_node_function(StartNode, "Start")
        )
        self.add_menu.add_command(
            label="Initialize - Run this subchart once", command=self.create_add_node_function(InitNode, "Initialize")
        )
        self.add_menu.add_command(
            label="Input - Pause for user input", command=self.create_add_node_function(InputNode, "Input")
        )
        self.add_menu.add_command(
            label="Prompt - Format custom text", command=self.create_add_node_function(PromptNode, "Prompt")
        )
        self.add_menu.add_command(
            label="Function - Custom Python Function",
            command=self.create_add_node_function(FuncNode, "Function"),
        )
        self.add_menu.add_command(
            label="LLM - Pass text to LLM of choice", command=self.create_add_node_function(LLMNode, "LLM")
        )
        self.add_menu.add_command(
            label="History - Save result to chat history",
            command=self.create_add_node_function(HistoryNode, "History"),
        )
        self.add_memory_menu = tk.Menu(self.add_menu, tearoff=0)
        self.add_memory_menu.add_command(
            label="Memory - Save to longer running memory", command=self.create_add_node_function(MemoryNode, "Memory")
        )
        self.add_memory_menu.add_command(
            label="Windowed Memory - Save to memory with a window",
            command=self.create_add_node_function(
                WindowedMemoryNode, "Windowed Memory"
            ),
        )
        self.add_memory_menu.add_command(
            label="Dynamic Windowed Memory - Save to memory based on last occurance of text",
            command=self.create_add_node_function(
                DynamicWindowedMemoryNode, "Dynamic Windowed Memory"
            ),
        )
        self.add_menu.add_cascade(label="Memory", menu=self.add_memory_menu)
        self.embedding_menu = tk.Menu(self.add_menu, tearoff=0)
        self.embedding_menu.add_command(
            label="Embedding In - Embed result and save to hnswlib",
            command=self.create_add_node_function(EmbeddingInNode, "Embedding In"),
        )
        self.embedding_menu.add_command(
            label="Embedding Query - Query HNSW index",
            command=self.create_add_node_function(
                EmbeddingQueryNode, "Embedding Query"
            ),
        )
        self.embedding_menu.add_command(
            label="Embedding Ingest - Read embeddings from file. Use with init node.",
            command=self.create_add_node_function(
                EmbeddingsIngestNode, "Embedding Ingest"
            ),
        )
        self.add_menu.add_cascade(label="Embedding", menu=self.embedding_menu)
        self.add_menu.add_command(
            label="Date - Insert current datetime", command=self.create_add_node_function(DateNode, "Date")
        )
        self.add_menu.add_command(
            label="Random - Insert a random number", command=self.create_add_node_function(RandomNode, "Random")
        )
        self.menubar.add_cascade(label="Add", menu=self.add_menu)
        self.test_menu = tk.Menu(self.add_menu, tearoff=0)
        self.test_menu.add_command(
            label="Dummy LLM - For testing",
            command=self.create_add_node_function(DummyNode, "Dummy LLM"),
        )
        self.test_menu.add_command(
            label="Assert - Assert certain condition is true", command=self.create_add_node_function(AssertNode, "Assert")
        )
        self.add_menu.add_cascade(label="Test", menu=self.test_menu)

        # create a help menu
        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.help_menu.add_command(label="About PromptFlow...", command=self.show_about)
        self.menubar.add_cascade(label="Help", menu=self.help_menu)

        # create the toolbar
        self.toolbar = tk.Frame(self.root, bg="grey")
        self.run_button = tk.Button(
            self.toolbar, text="Run", command=self.run_flowchart
        )
        self.stop_button = tk.Button(
            self.toolbar, text="Stop", command=self.stop_flowchart
        )
        self.serialize_button = tk.Button(
            self.toolbar, text="Serialize", command=self.serialize_flowchart
        )
        self.screenshot_button = tk.Button(
            self.toolbar, text="Screenshot", command=self.save_image
        )
        self.clear_button = tk.Button(
            self.toolbar, text="Clear", command=self.clear_flowchart
        )
        self.cost_button = tk.Button(
            self.toolbar, text="Cost", command=self.cost_flowchart
        )
        self.toolbar_buttons = [
            self.run_button,
            self.stop_button,
            self.serialize_button,
            self.screenshot_button,
            self.clear_button,
            self.cost_button,
        ]

        # pack the components
        for button in self.toolbar_buttons:
            button.pack(side=tk.LEFT, padx=2, pady=2)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        self.paned_window.pack(fill=tk.BOTH, expand=True)
        self.paned_window.add(self.canvas)
        self.paned_window.add(self.output_console)

        # key bindings
        self.root.bind("<Control-s>", lambda e: self.save_as())
        self.root.bind("<Control-o>", lambda e: self.load_from())
        self.root.bind("<F5>", lambda e: self.run_flowchart())
        self.root.bind("<Control-r>", lambda e: self.run_flowchart())
        self.root.bind("<Delete>", lambda e: self.delete_selected_element())
        self.canvas.bind("<MouseWheel>", self.handle_zoom)  # Windows
        self.canvas.bind("<Button-4>", self.handle_zoom)  # Linux (wheel up)
        self.canvas.bind("<Button-5>", self.handle_zoom)  # Linux (wheel down)
        self.canvas.bind("<4>", self.handle_zoom)  # MacOS (wheel up)
        self.canvas.bind("<5>", self.handle_zoom)  # MacOS (wheel down)
        self.canvas.bind("<ButtonPress-2>", self.start_pan)  # Middle mouse button press
        self.canvas.bind("<B2-Motion>", self.pan)  # Middle mouse button drag

        self.draw_grid()

        # add the menu
        self.root.config(menu=self.menubar)
        self.logger.debug("App created")
        self.loading_popup.destroy()

    @property
    def current_file(self) -> str:
        """The current file being edited."""
        return self._current_file

    @current_file.setter
    def current_file(self, value: str):
        self.root.title(f"PromptFlow - {value}")
        self._current_file = value

    def run_flowchart(self) -> State:
        """Execute the flowchart."""
        self.logger.info("Running flowchart")
        init_state = self.initial_state.copy()
        init_state = self.flowchart.initialize(init_state, self.output_console)
        final_state = self.flowchart.run(init_state, self.output_console)
        self.logger.info("Finished running flowchart")
        return final_state

    def stop_flowchart(self):
        """Stop the flowchart."""
        self.logger.info("Stopping flowchart")
        self.flowchart.is_running = False

    def serialize_flowchart(self):
        """Serialize the flowchart to JSON."""
        self.logger.info("Serializing flowchart")
        chart_json = json.dumps(self.flowchart.serialize(), indent=4)
        self.logger.info(chart_json)
        self.output_console.insert(tk.INSERT, chart_json)
        self.output_console.see(tk.END)
        return chart_json

    def clear_flowchart(self):
        """Clear the flowchart."""
        self.logger.info("Clearing flowchart")
        self.flowchart.clear()

    def cost_flowchart(self):
        """Get the approx cost to run the flowchart"""
        self.logger.info("Getting cost of flowchart")
        state = self.initial_state.copy()
        cost = self.flowchart.cost(state)
        self.output_console.insert(tk.INSERT, f"Estimated Cost: {cost}\n")
        self.output_console.see(tk.END)

    def run(self):
        """Run the app."""
        self.logger.info("Running app")
        tk.mainloop()

    def save_image(self):
        """
        Render the canvas as a png file and save it to image.png
        """
        self.logger.info("Saving image to image.png")
        x = self.canvas.winfo_rootx() + self.canvas.winfo_x()
        y = self.canvas.winfo_rooty() + self.canvas.winfo_y()
        x1 = x + self.canvas.winfo_width()
        y1 = y + self.canvas.winfo_height()
        ImageGrab.grab().crop((x, y, x1, y1)).save("image.png")

    def save_as(self):
        """
        Serialize the flowchart and save it to a json file
        """
        filename = tkinter.filedialog.asksaveasfilename(defaultextension=".promptflow")
        if filename:
            self.loading_popup = self.show_loading_popup("Saving flowchart...")
            with zipfile.ZipFile(filename, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.writestr(
                    "flowchart.json", json.dumps(self.flowchart.serialize(), indent=4)
                )
                # if there's an embedding ingest node, save the embedding
                for node in self.flowchart.nodes:
                    if isinstance(node, EmbeddingsIngestNode):
                        # write the embedding to the archive
                        archive.write(node.filename, arcname=node.filename)
                        archive.write(node.label_file, arcname=node.label_file)
                self.logger.info("Saved flowchart to %s", filename)
                self.current_file = filename
                self.loading_popup.destroy()
        else:
            self.logger.info("No file selected to save to")
        self.flowchart.is_dirty = False

    def load_from(self):
        """
        Read a json file and deserialize as a flowchart
        """
        filename = tkinter.filedialog.askopenfilename()
        if filename:
            self.loading_popup = self.show_loading_popup("Loading flowchart...")
            with zipfile.ZipFile(filename, "r") as archive:
                with archive.open("flowchart.json") as loadfile:
                    data = json.load(loadfile)
                    # load the embedding if there is one
                    for node in data["nodes"]:
                        if node["classname"] == "EmbeddingsIngestNode":
                            # load the embedding
                            embed_file = archive.extract(
                                node["filename"], path=os.getcwd()
                            )
                            node["filename"] = embed_file
                            # load the labels
                            label_file = archive.extract(
                                node["label_file"], path=os.getcwd()
                            )
                            node["label_file"] = label_file
                    self.clear_flowchart()
                    self.flowchart = Flowchart.deserialize(self.canvas, data)
                    self.current_file = filename
                    self.loading_popup.destroy()
        else:
            self.logger.info("No file selected to load from")

    def create_add_node_function(self, node_class, name="New Node"):
        """
        Create a function that adds a node to the flowchart
        """

        def add_node():
            node = node_class(self.flowchart, 100, 100, 200, 200, name)
            self.flowchart.add_node(node)

        return add_node

    def on_close(self):
        """
        Called when the user tries to close the app
        Checks if the flowchart is dirty and gives the user the option to save
        """
        self.logger.info("Closing app")
        if self.flowchart.nodes and self.flowchart.is_dirty:
            # give user option to save file before closing
            dialog = tkinter.messagebox.askyesnocancel(
                "Quit", "Do you want to save your work?"
            )
            if dialog is True:
                self.save_as()
            elif dialog is None:
                return  # don't close
        self.root.destroy()

    def show_about(self):
        """
        Show the about dialog
        """
        self.logger.info("Showing about")
        tkinter.messagebox.showinfo("About", "PromptFlow")

    def delete_selected_element(self):
        """
        When the user presses delete, delete the selected node if there is one
        """
        if self.flowchart.selected_element:
            self.logger.info(f"Deleting selected element {self.flowchart.selected_element.label}")
            self.flowchart.selected_element.delete()

    def handle_zoom(self, event):
        """
        Zoom in or out when the user scrolls
        """
        zoom_scale = 1.0

        # Check the platform
        if (
            event.num == 4 or event.delta > 0
        ):  # Linux (wheel up) or Windows (positive delta)
            zoom_scale = 1.1
        elif (
            event.num == 5 or event.delta < 0
        ):  # Linux (wheel down) or Windows (negative delta)
            zoom_scale = 0.9
        else:  # MacOS
            delta = event.delta
            if delta > 0:
                zoom_scale = 1.1
            elif delta < 0:
                zoom_scale = 0.9

        self.canvas.scale("all", event.x, event.y, zoom_scale, zoom_scale)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def start_pan(self, event):
        """Begining drag to scroll canvas"""
        self.canvas.scan_mark(event.x, event.y)

    def pan(self, event):
        """Dragging to scroll canvas"""
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def draw_grid(self, grid_size=20, grid_color="#cccccc", grid_dash=(2, 4)):
        """Draw a grid on the canvas"""
        self.canvas.delete("grid_line")  # Will only remove the grid_line
        width = self.canvas.winfo_reqwidth()
        height = self.canvas.winfo_reqheight()

        for x in range(0, width, grid_size):
            self.canvas.create_line(
                x, 0, x, height, fill=grid_color, dash=grid_dash, tags="grid_line"
            )

        for y in range(0, height, grid_size):
            self.canvas.create_line(
                0, y, width, y, fill=grid_color, dash=grid_dash, tags="grid_line"
            )

    def show_loading_popup(self, message: str):
        """Show the loading popup"""
        # Create a new Toplevel widget for the loading popup
        popup = tk.Toplevel(self.root)
        popup.title("Please wait...")

        # Set the popup to be a transient window of the main application
        popup.transient(self.root)

        # Center the popup on the screen
        popup.geometry(
            "+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50)
        )

        # Create a label with the loading message
        label = tk.Label(popup, text=message)
        label.pack(padx=10, pady=10)

        # Force Tkinter to draw the popup and process pending events
        popup.update_idletasks()

        return popup

    def export_to_mermaid(self):
        self.logger.info("Exporting flowchart")
        self.output_console.insert(tk.END, self.flowchart.to_mermaid())
