"""
Interface for http requests
"""
from enum import Enum
from typing import Any, Callable
import json
import requests
from promptflow.src.dialogues.node_options import NodeOptions

from promptflow.src.nodes.node_base import NodeBase
from promptflow.src.state import State


class RequestType(Enum):
    """
    Types of http requests- for dropdown
    """

    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"


request_functions: dict[str, Callable[[Any], requests.Response]] = {
    RequestType.GET.value: requests.get,
    RequestType.POST.value: requests.post,
    RequestType.PUT.value: requests.put,
    RequestType.DELETE.value: requests.delete,
}


class HttpNode(NodeBase):
    """
    Makes a http request
    """

    url: str
    request_type: str
    options_popup: NodeOptions

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )
        self.url = kwargs.get("url", "")
        self.request_type = kwargs.get("request_type", RequestType.GET.value)
        self.options_popup: NodeOptions = None
        self.request_type_item = self.canvas.create_text(
            self.center_x,
            self.center_y + 20,
            text=self.request_type.upper(),
            font=("Arial", 10),
            fill="black",
        )
        self.items.append(self.request_type_item)
        self.bind_drag()

    def run_subclass(self, state: State) -> str:
        """
        Sends a http request
        """
        try:
            data = json.loads(state.result)
        except json.decoder.JSONDecodeError:
            return "Invalid JSON"
        response = request_functions[self.request_type](self.url, json=data)
        state.result = response.text
        return response.text

    def edit_options(self, event):
        self.options_popup = NodeOptions(
            self.canvas,
            {
                "url": self.url,
                "request_type": self.request_type,
            },
            {
                "request_type": [
                    RequestType.GET.value,
                    RequestType.POST.value,
                    RequestType.PUT.value,
                    RequestType.DELETE.value,
                ],
            },
        )
        self.canvas.wait_window(self.options_popup)
        result = self.options_popup.result
        # check if cancel
        if self.options_popup.cancelled:
            return
        self.url = result["url"]
        self.request_type = result["request_type"]
        self.canvas.itemconfig(self.request_type_item, text=self.request_type.upper())
