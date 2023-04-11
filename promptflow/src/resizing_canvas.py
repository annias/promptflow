"""
Dealing with resizing of windows
"""
import tkinter as tk


class ResizingCanvas(tk.Canvas):
    """
    A subclass of Canvas for dealing with resizing of windows
    """

    def __init__(self, parent, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self, event):
        """
        Resize the canvas when the window is resized
        """
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width) / self.width
        hscale = float(event.height) / self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("grid_line", 0, 0, wscale, hscale)
