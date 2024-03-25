import logging
import asyncpg
from asyncpg import InvalidAuthorizationSpecificationError
from src import settings
from typing import Dict, List, Tuple
from src.databases.interface import DatabaseInterface
from src.exceptions import DatabaseConnectionError

logger = logging.getLogger(__name__)


class PostgresDB(DatabaseInterface):
    def __init__(self):
        self.conn = None
        super().__init__()

    async def _connect(
        self, host: str, port: int, user: str, password: str, database: str
    ) -> None:
        """Connect to the DB"""
        try:
            self.conn = await asyncpg.connect(
                host=host, port=port, user=user, password=password, database=database
            )
        except (InvalidAuthorizationSpecificationError, ConnectionRefusedError, Exception) as e:
            raise DatabaseConnectionError(f"PostgresDB Connection has failed: {e}")

    async def _disconnect(self) -> None:
        try:
            if self.conn:
                await self.conn.close()
        except Exception as e:
            raise Exception(e)

    async def build_query(self, *args, **kwargs) -> Tuple:
        param = args[0]
        method = kwargs.get('method')
        db_table = kwargs.get('db_table')
        db_column = kwargs.get('db_column')

        if method == "find_one" or method == "find":
            query = f"SELECT * FROM {db_table} WHERE {db_column} = $1"
        else:
            raise ValueError(f"Unsupported method: {method}")

        params = [param]
        return query, params

    async def execute_query(self, *args, **kwargs) -> Dict | List | None:
        try:
            await self._connect(**settings.DB_CONFIG)
            query_info = args[0]
            query, params = query_info
            if "find_one" in query:
                result = await self.conn.fetchrow(query, *params)
                return dict(result) if result else None
            elif "find" in query:
                results = await self.conn.fetch(query, *params)
                return [dict(result) for result in results]
        finally:
            await self._disconnect()
