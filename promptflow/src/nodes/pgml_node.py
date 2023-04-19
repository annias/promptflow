from typing import Optional, TYPE_CHECKING
from promptflow.src.pgml_interface.main import PgMLInterface
from promptflow.src.dialogues.node_options import NodeOptions
from promptflow.src.nodes.node_base import Node
from promptflow.src.themes import monokai

if TYPE_CHECKING:
    from promptflow.src.flowchart import Flowchart


class PGMLNode(Node):
    node_color = monokai.green

    def __init__(
        self,
        flowchart: "Flowchart",
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        label: str,
        interface: Optional[PgMLInterface] = None,
        **kwargs,
    ):
        if interface is None:
            self.dbname = "postgres"
            self.user = "postgres"
            self.password = "pass"
            self.host = "localhost"
            self.port = "5432"
            self.interface = PgMLInterface(
                self.dbname, self.user, self.password, self.host, self.port
            )
        else:
            self.dbname = interface.dbname
            self.user = interface.user
            self.password = interface.password
            self.host = interface.host
            self.port = interface.port
            self.interface = interface
            self.interface.connect()
            


        super().__init__(flowchart, x1, y1, x2, y2, label, **kwargs)

        self.options_popup: Optional[NodeOptions] = None

    def edit_options(self, event):
        self.options_popup = NodeOptions(
            self.canvas,
            {
                "dbname": self.dbname,
                "user": self.user,
                "password": self.password,
                "host": self.host,
                "port": self.port,
            },
        )
        self.canvas.wait_window(self.options_popup)
        result = self.options_popup.result
        if self.options_popup.cancelled:
            return
        self.dbname = result["dbname"]
        self.user = result["user"]
        self.password = result["password"]
        self.host = result["host"]
        self.port = result["port"]  # maybe make an int?
        self.interface = PgMLInterface(
            self.dbname,
            self.user,
            self.password,
            self.host,
            self.port
        )
        self.interface.connect()