"""
Edit node options
"""
import tkinter as tk
from typing import Any, Optional
import customtkinter

class NodeOptions(customtkinter.CTkToplevel):
    """
    Allow quick editing of node option parameters
    """

    def __init__(
        self,
        master,
        options_dict: dict[str, Any],
        dropdown_options: Optional[dict[str, Any]] = None,
    ):
        super().__init__(master)
        self.title("Node Options")
        self.options_dict = options_dict
        self.result = options_dict.copy()
        self.entries = {}

        if dropdown_options is None:
            dropdown_options = {}

        for index, (key, value) in enumerate(self.options_dict.items()):
            label = customtkinter.CTkLabel(self, text=key)
            label.grid(row=index, column=0, padx=(10, 5), pady=(5, 5), sticky="e")

            if key in dropdown_options:
                var = tk.StringVar(self)
                var.set(value)
                option_menu = customtkinter.CTkOptionMenu(self, variable=var, values=dropdown_options[key])
                option_menu.grid(
                    row=index, column=1, padx=(5, 10), pady=(5, 5), sticky="w"
                )
                self.entries[key] = var
            else:
                entry = customtkinter.CTkEntry(self)
                entry.insert(0, value)
                entry.grid(row=index, column=1, padx=(5, 10), pady=(5, 5), sticky="w")
                self.entries[key] = entry

        save_button = customtkinter.CTkButton(self, text="Save", command=self.save)
        save_button.grid(
            row=len(self.options_dict),
            column=0,
            padx=(10, 5),
            pady=(10, 10),
            sticky="e",
        )

        cancel_button = customtkinter.CTkButton(self, text="Cancel", command=self.cancel)
        cancel_button.grid(
            row=len(self.options_dict),
            column=1,
            padx=(5, 10),
            pady=(10, 10),
            sticky="w",
        )

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.cancelled = False

    def save(self):
        """
        Write the values from the entries back to the result dict
        """
        for key, entry in self.entries.items():
            self.result[key] = entry.get()
        self.destroy()

    def cancel(self):
        """
        Cancel the editing, setting the flag
        """
        self.cancelled = True
        self.destroy()
