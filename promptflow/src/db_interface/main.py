import json
import uuid
from typing import Any, Optional, Union
import psycopg2
from promptflow.src.db_interface.pgml_constants import (
    Algorithm,
    Sampling,
    Search,
    Task,
    Strategy,
)


class DBInterface:
    def __init__(self, dbname: str, user: str, password: str, host: str, port: str):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port

        self.connection = None
        self.cursor = None

    def connect(self):
        """Connect to the database."""
        self.connection = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )
        self.cursor = self.connection.cursor()

    def _run_query(self, query: str) -> list[tuple[Any, ...]]:
        if self.connection is None or self.cursor is None:
            raise RuntimeError("Not connected to database.")
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            self.connection.commit()
            return result
        except Exception as e:
            self.cursor.execute("ROLLBACK")
            self.connection.commit()
            return []

    def _create_temp_table(
        self, columns: list[str], types: Optional[list[str]] = None
    ) -> bool:
        if types is None:
            types = ["TEXT"] * len(columns)
        table_name = f"temp_{uuid.uuid4().hex}"
        query = f"""CREATE TEMP TABLE {table_name} ("""
        for column, _type in zip(columns, types):
            query += f"{column} {_type},"
        query = query[:-1] + ");"
        self._run_query(query)
        return True

    def select(self, query: str, where: Optional[str] = None) -> list[tuple[Any, ...]]:
        query = f"SELECT * FROM ({query}) AS temp"
        if where:
            query += f" WHERE {where}"
        query += ";"
        return self._run_query(query)


class PgMLInterface(DBInterface):
    def train(
        self,
        project_name: str,
        task: Optional[Task] = None,
        relation_name: Optional[str] = None,
        y_column_name: Optional[str] = None,
        algorithm: str = Algorithm.LINEAR,
        hyperparameters: Optional[dict[str, Any]] = None,
        search: Optional[Search] = None,
        search_params: Optional[dict[str, Any]] = None,
        search_args: Optional[dict[str, Any]] = None,
        test_size: float = 0.25,
        test_sampling: str = Sampling.RANDOM,
        preprocessing: Optional[dict[str, Any]] = None,
    ) -> list[tuple[Any, ...]]:
        if hyperparameters is None:
            hyperparameters = {}
        if search_params is None:
            search_params = {}
        if search_args is None:
            search_args = {}
        query = f"""SELECT * from pgml.train(
                        project_name => '{project_name}',
                """
        args = []
        if task is not None:
            args.append(f"task => '{task}',")
        if relation_name is not None:
            args.append(f"relation_name => '{relation_name}',")
        if y_column_name is not None:
            args.append(f"y_column_name => '{y_column_name}',")
        args.append(f"algorithm => '{algorithm}',")
        if len(hyperparameters) > 0:
            args.append(f"hyperparameters => '{hyperparameters}'::JSONB,")
        if search is not None:
            args.append(f"search => '{search}',")
        if len(search_params) > 0:
            args.append(f"search_params => '{search_params}'::JSONB,")
        if len(search_args) > 0:
            args.append(f"search_args => '{search_args}'::JSONB,")
        args.append(f"test_size => {test_size},")
        args.append(f"test_sampling => '{test_sampling}'")
        if preprocessing is not None:
            args.append(f"preprocessing => '{preprocessing}'::JSONB")
        args.append(");")
        query += "\n".join(args)
        return self._run_query(query)

    def train_joint(
        self,
        project_name: str,
        task: Optional[Task] = None,
        relation_name: Optional[str] = None,
        y_column_name: Optional[list[str]] = None,
        algorithm: str = Algorithm.LINEAR,
        hyperparameters: Optional[dict[str, Any]] = None,
        search: Optional[Search] = None,
        search_params: Optional[dict[str, Any]] = None,
        search_args: Optional[dict[str, Any]] = None,
        test_size: float = 0.25,
        test_sampling: str = Sampling.RANDOM,
        preprocessing: Optional[dict[str, Any]] = None,
    ):
        """
        Some algorithms support joint optimization of the task across
        multiple outputs, which can improve results compared to using
        multiple independent models.
        """
        if hyperparameters is None:
            hyperparameters = {}
        if search_params is None:
            search_params = {}
        if search_args is None:
            search_args = {}
        query = f"""SELECT * from pgml.train(
                        project_name => '{project_name}',
                """
        args = []
        if task is not None:
            args.append(f"task => '{task}',")
        if relation_name is not None:
            args.append(f"relation_name => '{relation_name}',")
        if y_column_name is not None:
            y_column_str = ""
            for y in y_column_name:
                y_column_str += f"'{y}',"
            y_column_str = y_column_str[:-1]
            args.append(f"y_column_name => ARRAY[{y_column_str}],")
        args.append(f"algorithm => '{algorithm}',")
        if len(hyperparameters) > 0:
            args.append(f"hyperparameters => '{hyperparameters}'::JSONB,")
        if search is not None:
            args.append(f"search => '{search}',")
        if len(search_params) > 0:
            args.append(f"search_params => '{search_params}'::JSONB,")
        if len(search_args) > 0:
            args.append(f"search_args => '{search_args}'::JSONB,")
        args.append(f"test_size => {test_size},")
        args.append(f"test_sampling => '{test_sampling}'")
        if preprocessing is not None:
            args.append(f"preprocessing => '{preprocessing}'::JSONB")
        args.append(");")
        query += "\n".join(args)
        return self._run_query(query)

    def load_dataset(
        self, datset: str, kwargs: Optional[dict[str, str]] = None
    ) -> list[tuple[Any, ...]]:
        query = f"""
            SELECT * from pgml.load_dataset('{datset}'
            """
        if kwargs is not None:
            query += f", kwargs => '{kwargs}'"
        query += ");"
        return self._run_query(query)

    def overview(self):
        query = "SELECT * FROM pgml.overview;"
        return self._run_query(query)

    def predict(self, project_name: str, features: Union[str, list[float]]):
        query = f"SELECT pgml.predict('{project_name}', "
        if isinstance(features, str):
            query += f"'{features}'"
        else:
            query += f"ARRAY{features}"
        query += ") AS prediction;"
        return self._run_query(query)

    def deployed_models(self):
        query = "SELECT * FROM pgml.deployed_models;"
        return self._run_query(query)

    def deploy(
        self,
        project_name: str,
        strategy: str = Strategy.BEST_SCORE,
        algorithm: Optional[str] = None,
    ):
        query = f"""pgml.deploy(
            project_name => '{project_name}',
            strategy => '{strategy}',"""
        if algorithm is not None:
            query += f"algorithm => '{algorithm}',"
        query += ");"
        return self._run_query(query)

    def predict_batch(
        self, project_name: str, features: list[float], relation_name: str
    ):
        query = f"SELECT pgml.predict_batch('{project_name}', array_agg(ARRAY{features})) AS prediction FROM {relation_name};"
        return self._run_query(query)

    def transform(
        self,
        task: Union[str, dict[str, Any]],
        inputs: Union[list[str], list[bytearray]],
        cache: bool = False,
    ):
        query = """SELECT pgml.transform(
        """
        if isinstance(task, str):
            query += f"'{task}',"
        else:
            query += f"'{json.dumps(task)}'::JSONB,"
        input_txt = ""
        for i in inputs:
            input_txt += f"'{i}',"
        input_txt = input_txt[:-1]
        query += input_txt
        if cache:
            query += ", cache => TRUE"
        query += ") AS prediction;"
        return self._run_query(query)

    def tune(
        self,
        project_name: str,
        task: str,
        relation_name: str,
        y_column_name: str,
        model_name: str,
        hyperparameters: dict[str, Any],
        test_size: float = 0.5,
        test_sampling: str = Sampling.LAST,
    ):
        query = f"""SELECT pgml.tune(
            '{project_name}',
            task => '{task}',
            relation_name => '{relation_name}',
            y_column_name => '{y_column_name}',
            model_name => '{model_name}',
            hyperparams => '{hyperparameters}',
            test_size => {test_size},
            test_sampling => '{test_sampling}
            );"""
        return self._run_query(query)

    def generate(self, project_name: str, string: str):
        query = f"SELECT pgml.generate('{project_name}', '{string}') AS result;"
        return self._run_query(query)

    def predict_proba(self, project_name: str, features: Union[str, list[float]]):
        query = f"SELECT pgml.predict_proba({project_name}, "
        if isinstance(features, str):
            query += f"'{features}'"
        else:
            query += f"ARRAY{features}"
        query += ") AS prediction;"
        return self._run_query(query)

    def embed(
        self, transformer: str, text: str, kwargs: Optional[dict[str, Any]] = None
    ):
        query = f"""SELECT pgml.embed('{transformer}', '{text}'"""
        if kwargs is not None:
            query += f", kwargs => '{kwargs}'"
        query += ");"
        return self._run_query(query)

    def cosine_similarity(self, vec1: list[float], vec2: list[float]):
        query = f"""SELECT pgml.cosine_similarity(ARRAY{vec1}, ARRAY{vec2});"""
        return self._run_query(query)

    def add(self, vec1: list[float], vec2: list[float]):
        query = f"""SELECT pgml.add(ARRAY{vec1}, ARRAY{vec2});"""
        return self._run_query(query)

    def subtract(self, vec1: list[float], vec2: list[float]):
        query = f"""SELECT pgml.subtract(ARRAY{vec1}, ARRAY{vec2});"""
        return self._run_query(query)

    def multiply(self, vec1: list[float], vec2: list[float]):
        query = f"""SELECT pgml.multiply(ARRAY{vec1}, ARRAY{vec2});"""
        return self._run_query(query)

    def divide(self, vec1: list[float], vec2: list[float]):
        query = f"""SELECT pgml.divide(ARRAY{vec1}, ARRAY{vec2});"""
        return self._run_query(query)

    def norm_l0(self, vec: list[float]):
        """Dimensions not at origin"""
        query = f"""SELECT pgml.norm_l0(ARRAY{vec});"""
        return self._run_query(query)

    def norm_l1(self, vec: list[float]):
        """Manhattan distance from origin"""
        query = f"""SELECT pgml.norm_l1(ARRAY{vec});"""
        return self._run_query(query)

    def norm_l2(self, vec: list[float]):
        """Euclidean distance from origin"""
        query = f"""SELECT pgml.norm_l2(ARRAY{vec});"""
        return self._run_query(query)

    def norm_max(self, vec: list[float]):
        """Absolute value of largest element"""
        query = f"""SELECT pgml.norm_max(ARRAY{vec});"""
        return self._run_query(query)

    def normalize_l1(self, vec: list[float]):
        """Unit Vector"""
        query = f"""SELECT pgml.normalize_l1(ARRAY{vec});"""
        return self._run_query(query)

    def normalize_l2(self, vec: list[float]):
        """Squared Unit Vector"""
        query = f"""SELECT pgml.normalize_l2(ARRAY{vec});"""
        return self._run_query(query)

    def normalize_max(self, vec: list[float]):
        """-1:1 Values"""
        query = f"""SELECT pgml.normalize_max(ARRAY{vec});"""
        return self._run_query(query)

    def distance_l1(self, vec1: list[float], vec2: list[float]):
        """Manhattan distance between vectors"""
        query = f"""SELECT pgml.distance_l1(ARRAY{vec1}, ARRAY{vec2});"""
        return self._run_query(query)

    def distance_l2(self, vec1: list[float], vec2: list[float]):
        """Euclidean distance between vectors"""
        query = f"""SELECT pgml.distance_l2(ARRAY{vec1}, ARRAY{vec2});"""
        return self._run_query(query)

    def dot_product(self, vec1: list[float], vec2: list[float]):
        """Projection"""
        query = f"""SELECT pgml.dot_product(ARRAY{vec1}, ARRAY{vec2});"""
        return self._run_query(query)

    def projects(self):
        query = "SELECT * from pgml.projects;"
        return self._run_query(query)
