"""
Worlds worst code editor
"""
import keyword
import re
from typing import TYPE_CHECKING, Optional
import tkinter as tk

from promptflow.src.text_data import TextData
from promptflow.src.dialogues.text_input import TextInput
from promptflow.src.themes import monokai

if TYPE_CHECKING:
    from promptflow.src.flowchart import Flowchart


class CodeInput(TextInput):
    """
    Simple text editor for editing TextData with syntax highlighting
    """

    def __init__(
        self,
        parent,
        flowchart: "Flowchart",
        text_data: Optional[TextData | dict] = None,
    ):
        self.python_keywords = keyword.kwlist
        if text_data is None:
            text_data = {"label": "Untitled", "text": ""}
        super().__init__(parent, flowchart, text_data)

        # self.text_entry._text_color("Keyword", foreground=monokai.blue)

        # self.text_entry.tag_configure("Keyword", foreground=monokai.blue)
        # self.text_entry.tag_configure("String", foreground=monokai.green)
        # self.text_entry.tag_configure("Comment", foreground=monokai.comments)

        self.text_entry.bind("<KeyRelease>", self.on_text_modified)

        self.syntax_highlighting(None)

    def on_text_modified(self, event: Optional[tk.Event]):
        super().on_text_modified(event)
        self.syntax_highlighting(event)

    def syntax_highlighting(self, _: Optional[tk.Event]):
        """
        Highlights comments, strings, and Python keywords
        """
        data = self.text_entry.get("1.0", "end-1c")

        for tag in self.text_entry.tag_names():
            self.text_entry.tag_remove(tag, "1.0", "end")

        for word in self.python_keywords:
            start = 0
            word_pattern = r"\b" + word + r"\b"
            for match in re.finditer(word_pattern, data):
                pos = match.start()
                start, end = pos, pos + len(word)
                self.text_entry.mark_set("range_start", f"1.0 + {start} chars")
                self.text_entry.mark_set("range_end", f"1.0 + {end} chars")
                self.text_entry.tag_add("Keyword", "range_start", "range_end")

        # highlight strings
        string_pattern = r"\".*?\"|\'.*?\'"
        for match in re.findall(string_pattern, data):
            pos = data.find(match)
            start, end = pos, pos + len(match)
            self.text_entry.mark_set("range_start", f"1.0 + {start} chars")
            self.text_entry.mark_set("range_end", f"1.0 + {end} chars")
            self.text_entry.tag_add("String", "range_start", "range_end")

        # highlight comments
        comment_pattern = r"#[^\n]*"
        for match in re.findall(comment_pattern, data):
            pos = data.find(match)
            start, end = pos, pos + len(match)
            self.text_entry.mark_set("range_start", f"1.0 + {start} chars")
            self.text_entry.mark_set("range_end", f"1.0 + {end} chars")
            self.text_entry.tag_add("Comment", "range_start", "range_end")
