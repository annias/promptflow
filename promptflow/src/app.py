"""
Primary application class. This class is responsible for creating the
window, menu, and canvas. It also handles the saving and loading of
flowcharts.
"""
import json
import logging
import tkinter as tk
from tkinter import ttk
import customtkinter
import tkinter.filedialog
import tkinter.scrolledtext
import tkinter.messagebox
from PIL import Image, ImageTk
import os
from typing import Optional
import zipfile
from PIL import ImageGrab
from promptflow.src.command import (
    CommandManager,
    AddConnectionCommand,
    RemoveConnectionCommand,
    AddNodeCommand,
    RemoveNodeCommand,
)

from promptflow.src.flowchart import Flowchart
from promptflow.src.nodes.date_node import DateNode
from promptflow.src.nodes.env_node import EnvNode, ManualEnvNode
from promptflow.src.nodes.http_node import HttpNode
from promptflow.src.nodes.node_base import NodeBase
from promptflow.src.nodes.db_node import PGMLNode, GenerateNode, SelectNode
from promptflow.src.nodes.regex_node import RegexNode, TagNode
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
from promptflow.src.nodes.test_nodes import AssertNode, LoggingNode
from promptflow.src.options import Options
from promptflow.src.nodes.dummy_llm_node import DummyNode
from promptflow.src.state import State
from promptflow.src.themes import monokai


class App:
    """
    Primary application class. This class is responsible for creating the
    window, menu, and canvas. It also handles the saving and loading of
    flowcharts.
    """

    def __init__(self, initial_state: State, options: Options):
        self.root = customtkinter.CTk()
        self.root.title("PromptFlow")
        customtkinter.set_appearance_mode("dark")
        ico_dir = os.path.dirname(__file__)
        ico_path = os.path.join(ico_dir, "../res/Logo_2.png")
        ico = Image.open(ico_path)
        photo = ImageTk.PhotoImage(ico)
        self.root.wm_iconphoto(False, photo)

        self.command_manager = CommandManager()  # todo

        self.zoom_level = 1.0

        self.loading_popup = self.show_loading_popup("Starting app...")

        self.initial_state = initial_state
        self.logging_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.DEBUG, format=self.logging_fmt)
        self.logger.info("Creating app")

        # Build the core components

        self.paned_window = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashwidth=5)
        self.canvas = tk.Canvas(
            self.paned_window,
            width=options.width,
            height=options.height,
            background=monokai.BACKGROUND,
        )
        self.flowchart = Flowchart(self.canvas)
        self.current_file = "Untitled"

        # scrolling text meant to simulate a console
        self.output_console = customtkinter.CTkTextbox(
            self.paned_window, height=8, width=400
        )

        # register on close behavior
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # create the menu
        self.menu = tk.Menu(self.canvas)
        self.menubar = tk.Menu(self.menu, tearoff=0)

        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(label="Save Flowchart...", command=self.save_as)
        self.file_menu.add_command(label="Load Flowchart...", command=self.load_from)
        self.file_menu.add_command(label="Save Console...", command=self.export_console)
        self.export_menu = tk.Menu(self.file_menu, tearoff=0)
        self.export_menu.add_command(label="To Mermaid", command=self.export_to_mermaid)
        self.file_menu.add_cascade(label="Export", menu=self.export_menu)
        self.menubar.add_cascade(label="File", menu=self.file_menu)

        # edit menu for common actions
        self.edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.edit_menu.add_command(
            label="Undo", command=self.command_manager.undo, accelerator="Ctrl+Z"
        )
        self.edit_menu.add_command(
            label="Redo", command=self.command_manager.redo, accelerator="Ctrl+Y"
        )
        self.edit_menu.add_command(
            label="Clear",
            command=self.clear_flowchart,
        )
        self.menubar.add_cascade(label="Edit", menu=self.edit_menu)

        # create an add menu for each type of node
        self.add_menu = tk.Menu(self.menubar, tearoff=0)
        self.add_menu.add_command(
            label="Start - First node in main loop",
            command=self.create_add_node_function(StartNode, "Start"),
        )
        self.add_menu.add_command(
            label="Initialize - Run this subchart once",
            command=self.create_add_node_function(InitNode, "Initialize"),
        )
        self.envvars_menu = tk.Menu(self.add_menu, tearoff=0)
        self.envvars_menu.add_command(
            label=".env - Load environment variables from .env file",
            command=self.create_add_node_function(EnvNode, ".env"),
        )
        self.envvars_menu.add_command(
            label="Manual - Manually set environment variables",
            command=self.create_add_node_function(ManualEnvNode, "Manual"),
        )
        self.add_menu.add_cascade(label="Environment Variables", menu=self.envvars_menu)
        self.add_menu.add_command(
            label="Input - Pause for user input",
            command=self.create_add_node_function(InputNode, "Input"),
        )
        self.add_menu.add_command(
            label="Prompt - Format custom text",
            command=self.create_add_node_function(PromptNode, "Prompt"),
        )
        self.add_menu.add_command(
            label="Function - Custom Python Function",
            command=self.create_add_node_function(FuncNode, "Function"),
        )
        self.add_menu.add_command(
            label="LLM - Pass text to LLM of choice",
            command=self.create_add_node_function(LLMNode, "LLM"),
        )
        self.add_menu.add_command(
            label="History - Save result to chat history",
            command=self.create_add_node_function(HistoryNode, "History"),
        )
        self.add_menu.add_command(
            label="HTTP - Send HTTP request",
            command=self.create_add_node_function(HttpNode, "HTTP"),
        )
        self.add_memory_menu = tk.Menu(self.add_menu, tearoff=0)
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
        self.regex_menu = tk.Menu(self.add_menu, tearoff=0)
        self.regex_menu.add_command(
            label="Regex - Match text with regex",
            command=self.create_add_node_function(RegexNode, "Regex"),
        )
        self.regex_menu.add_command(
            label="Tag - Extract text between tags",
            command=self.create_add_node_function(TagNode, "Tag"),
        )
        self.add_menu.add_cascade(label="Regex", menu=self.regex_menu)
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
        self.db_menu = tk.Menu(self.add_menu, tearoff=0)
        self.db_menu.add_command(
            label="Select - Query the PGML database",
            command=self.create_add_node_function(SelectNode, "Select"),
        )
        self.db_menu.add_command(
            label="Generate - Generate next text from PGML model",
            command=self.create_add_node_function(GenerateNode, "Generate"),
        )
        self.add_menu.add_cascade(label="Database", menu=self.db_menu)
        self.add_menu.add_command(
            label="Date - Insert current datetime",
            command=self.create_add_node_function(DateNode, "Date"),
        )
        self.add_menu.add_command(
            label="Random - Insert a random number",
            command=self.create_add_node_function(RandomNode, "Random"),
        )
        self.menubar.add_cascade(label="Add", menu=self.add_menu)
        self.test_menu = tk.Menu(self.add_menu, tearoff=0)
        self.test_menu.add_command(
            label="Logging - Print string to log",
            command=self.create_add_node_function(LoggingNode, "Logging"),
        )
        self.test_menu.add_command(
            label="Dummy LLM - For testing",
            command=self.create_add_node_function(DummyNode, "Dummy LLM"),
        )
        self.test_menu.add_command(
            label="Assert - Assert certain condition is true",
            command=self.create_add_node_function(AssertNode, "Assert"),
        )
        self.add_menu.add_cascade(label="Test", menu=self.test_menu)

        # create a help menu
        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.help_menu.add_command(label="About PromptFlow...", command=self.show_about)
        self.menubar.add_cascade(label="Help", menu=self.help_menu)

        # create the toolbar
        self.toolbar = customtkinter.CTkFrame(self.root)
        self.run_button = customtkinter.CTkButton(
            self.toolbar,
            text="Run",
            command=self.run_flowchart,
            border_width=2,
            border_color="black",
        )
        self.stop_button = customtkinter.CTkButton(
            self.toolbar,
            text="Stop",
            command=self.stop_flowchart,
            border_width=2,
            border_color="black",
        )
        self.serialize_button = customtkinter.CTkButton(
            self.toolbar,
            text="Serialize",
            command=self.serialize_flowchart,
            border_width=2,
            border_color="black",
        )
        self.screenshot_button = customtkinter.CTkButton(
            self.toolbar,
            text="Screenshot",
            command=self.save_image,
            border_width=2,
            border_color="black",
        )
        self.cost_button = customtkinter.CTkButton(
            self.toolbar,
            text="Cost",
            command=self.cost_flowchart,
            border_width=2,
            border_color="black",
        )
        self.toolbar_buttons = [
            self.run_button,
            self.stop_button,
            self.serialize_button,
            self.screenshot_button,
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
        self._create_key_bindings()

        # add the menu
        self.root.config(menu=self.menubar)
        self.logger.debug("App created")
        self.loading_popup.destroy()

    def _create_key_bindings(self):
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
        self.canvas.bind("<Button-1>", self.print_coords)  # Left mouse button click
        
    def print_coords(self, event):
        """Print the coordinates of the mouse click"""
        self.logger.debug(str((self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))))

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
        # ask the user if they want to save
        if self.flowchart.nodes and not self.flowchart.is_running:
            save = tk.messagebox.askyesnocancel(
                "Save?",
                "Would you like to save before clearing?",
                parent=self.root,
            )
            if save is None:
                return
            elif save:
                self.save_as()
        self.logger.info("Clearing flowchart")
        self.flowchart.clear()
        self.output_console.delete("1.0", tk.END)

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
            self.clear_flowchart()
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
            node = node_class(self.flowchart, 100, 100, name)
            self.flowchart.add_node(node)
            # scale node
            for item in node.items:
                self.canvas.scale(item, 0, 0, self.zoom_level, self.zoom_level)

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
            self.logger.info(
                f"Deleting selected element {self.flowchart.selected_element.label}"
            )
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
        self.zoom_level *= zoom_scale

    def start_pan(self, event):
        """Begining drag to scroll canvas"""
        self.canvas.scan_mark(event.x, event.y)

    def pan(self, event):
        """Dragging to scroll canvas"""
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def show_loading_popup(self, message: str):
        """Show the loading popup"""
        # Create a new Toplevel widget for the loading popup
        popup = customtkinter.CTkToplevel(self.root)
        popup.title("Please wait...")

        # Set the popup to be a transient window of the main application
        popup.transient(self.root)

        # Center the popup on the screen
        popup.geometry(
            "+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50)
        )

        # Create a label with the loading message
        label = customtkinter.CTkLabel(popup, text=message)
        label.pack(padx=10, pady=10)

        # Force Tkinter to draw the popup and process pending events
        popup.update_idletasks()

        return popup

    def export_to_mermaid(self):
        """
        Print the flowchart in the mermaid flowchart language
        """
        self.logger.info("Exporting flowchart")
        self.output_console.insert(tk.END, self.flowchart.to_mermaid())

    def export_console(self):
        """
        Write the contents console to a file
        """
        self.logger.info("Exporting console")
        # create file dialog
        filedialog = tkinter.filedialog.asksaveasfile(mode="w", defaultextension=".txt")
        if filedialog:
            filedialog.write(self.output_console.get("1.0", tk.END))
            filedialog.close()
