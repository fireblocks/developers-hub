import motor.motor_asyncio
from typing import List, Tuple
from pymongo.database import Database
import logging
from src import settings
from src.databases.interface import DatabaseInterface

logger = logging.getLogger(__name__)


class MongoDB(DatabaseInterface):
    """Mongo DB connection class.
    Using async python mongo driver `Motor`: https://motor.readthedocs.io/en/stable/
    """

    def __init__(self):
        super().__init__()
        self.client = None
        self.db: Database = None

    async def _connect(
        self, host: str, port: int, user: str, password: str, database: str
    ) -> None:
        # Construct MongoDB connection URI
        uri = f"mongodb+srv://{user}:{password}@{host}/{database}"
        self.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self.client[database]

    async def _disconnect(self) -> None:
        if self.client:
            self.client.close()
            self.client = None
            self.db = None

    async def execute_query(self, *args, **kwargs) -> List | None:
        """Execute MongoDB query"""

        try:
            await self._connect(**settings.DB_CONFIG)
            params = args[0]
            method = params[0]
            db_table = params[2].get("db_table")
            query_param = params[1]
            collection = self.db[db_table]

            if method == "find_one":
                return await collection.find_one(query_param) is not None
            elif method == "find":
                documents = collection.find(query_param)
                return list(documents)
        finally:
            await self._disconnect()

    async def build_query(self, *args, **kwargs) -> Tuple:
        param = args[0]
        method = kwargs.get('method')
        db_table = kwargs.get('db_table')
        db_column = kwargs.get('db_column')

        if method not in ["find_one", "find"]:
            raise ValueError(f"Unsupported method: {method}")

        query = method
        params = {db_column: param}
        return (query, params, {'db_table': db_table})

