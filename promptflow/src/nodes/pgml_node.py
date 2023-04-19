from typing import Optional, TYPE_CHECKING
from promptflow.src.pgml_interface.main import PgMLInterface
from promptflow.src.dialogues.node_options import NodeOptions
from promptflow.src.nodes.node_base import Node
from promptflow.src.themes import monokai

if TYPE_CHECKING:
    from promptflow.src.flowchart import Flowchart


class PGMLConnectionSingleton:
    _instance: Optional["PGMLConnectionSingleton"] = None
    interface: PgMLInterface
    dbname: str
    user: str
    password: str
    host: str
    port: str

    def __new__(cls) -> "PGMLConnectionSingleton":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.dbname = "postgres"
            cls._instance.user = "postgres"
            cls._instance.password = "pass"
            cls._instance.host = "localhost"
            cls._instance.port = "5432"
            cls._instance.interface = PgMLInterface(
                cls._instance.dbname,
                cls._instance.user,
                cls._instance.password,
                cls._instance.host,
                cls._instance.port,
            )
        return cls._instance

    def update(self, dbname: str, user: str, password: str, host: str, port: str):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.interface = PgMLInterface(
            self.dbname, self.user, self.password, self.host, self.port
        )
        self.interface.connect()


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
        **kwargs,
    ):
        self.interface = PGMLConnectionSingleton()
        self.dbname = self.interface.dbname
        self.user = self.interface.user
        self.password = self.interface.password
        self.host = self.interface.host
        self.port = self.interface.port

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
        self.interface.update(
            self.dbname, self.user, self.password, self.host, self.port
        )


class GenerateNode(PGMLNode):
    def run_subclass(self, state) -> str:
        gen = self.interface.interface.generate("gpt2-instruct-dolly", state.result)[0][0]
        return gen
