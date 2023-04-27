from abc import ABC
from typing import Optional, TYPE_CHECKING
from promptflow.src.db_interface.main import DBInterface, PgMLInterface
from promptflow.src.dialogues.node_options import NodeOptions
from promptflow.src.nodes.node_base import NodeBase
from promptflow.src.themes import monokai

if TYPE_CHECKING:
    from promptflow.src.flowchart import Flowchart


class DBConnectionSingleton:
    _instance: Optional["DBConnectionSingleton"] = None
    interface_factory: DBInterface
    interface: DBInterface
    dbname: str
    user: str
    password: str
    host: str
    port: str

    def __new__(cls, interface=DBInterface) -> "DBConnectionSingleton":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.dbname = "postgres"
            cls._instance.user = "postgres"
            cls._instance.password = "pass"
            cls._instance.host = "localhost"
            cls._instance.port = "5432"
            cls._instance.interface_factory = interface
            cls._instance.interface = interface(
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
        self.interface = self.interface_factory(
            self.dbname, self.user, self.password, self.host, self.port
        )
        print("connecting")
        self.interface.connect()
        print("connected")


class DBNode(NodeBase, ABC):
    node_color = monokai.GREEN

    def __init__(
        self,
        flowchart: "Flowchart",
        center_x: float,
        center_y: float,
        label: str,
        **kwargs,
    ):
        self.interface = DBConnectionSingleton(DBInterface)
        self.dbname = self.interface.dbname
        self.user = self.interface.user
        self.password = self.interface.password
        self.host = self.interface.host
        self.port = self.interface.port

        super().__init__(flowchart, center_x, center_y, label, **kwargs)

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


class PGMLNode(DBNode):
    node_color = monokai.GREEN

    def __init__(
        self,
        flowchart: "Flowchart",
        center_x: float,
        center_y: float,
        label: str,
        **kwargs,
    ):
        self.interface = DBConnectionSingleton(PgMLInterface)
        super().__init__(flowchart, center_x, center_y, label, **kwargs)
        self.model = "gpt2-instruct-dolly"

    def edit_options(self, event):
        self.options_popup = NodeOptions(
            self.canvas,
            {
                "dbname": self.dbname,
                "user": self.user,
                "password": self.password,
                "host": self.host,
                "port": self.port,
                "model": self.model,
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
        self.model = result["model"]
        self.interface.update(
            self.dbname, self.user, self.password, self.host, self.port
        )


class SelectNode(DBNode):
    def run_subclass(self, state) -> str:
        select = self.interface.interface.select(state.result)[0][0]
        return select


class GenerateNode(PGMLNode):
    def run_subclass(self, state) -> str:
        gen = self.interface.interface.generate(self.model, state.result)[0][0]
        return gen
