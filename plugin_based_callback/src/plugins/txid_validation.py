import logging
from src import settings
from typing import Dict, Any
from src.plugins.interface import PluginInterface
from src.databases.interface import DatabaseInterface
from src.exceptions import PluginError, DatabaseUnsupportedError


logger = logging.getLogger(__name__)


class TxidValidation(PluginInterface):

    async def init(self, *args, **kwargs):
        await self._create_db_instance(settings.DB_TYPE)

    async def process_request(self, data: Dict[str, Any]) -> bool:
        """Entry point - Validates the transaction ID against the Database"""
        tx_id = data.get("txId")
        if tx_id is None:
            raise PluginError("Transaction ID (txId) is missing.")
        try:
            result = await self._validate_txid(tx_id)
            logger.info(f"Approval result from TX ID Validation Plugin is: {result}")
            return result
        except Exception as e:
            raise PluginError(f"Unexpected error in TxID Validation plugin: {e}")

    async def _validate_txid(self, tx_id: str) -> bool:
        """Checks the database for the existence of a transaction ID."""
        logger.info(f"Validating that {tx_id} exists in the DB")
        query_result = await self.db.build_query(
            tx_id,
            method="find_one",
            db_table=settings.DB_TABLE,
            db_column=settings.DB_COLUMN,
        )
        logger.info(f"Query result is: {query_result}")
        exists = await self.db.execute_query(query_result)
        return bool(exists)

    async def _create_db_instance(self, db_type: str) -> DatabaseInterface:
        """Create a DB instance based on the provided DB_TYPE and DB_CLASS_MAP"""
        db_class = settings.DB_CLASS_MAP.get(db_type)
        if db_class is None:
            raise DatabaseUnsupportedError(f"Unsupported database type: {db_type}")
        return await self.set_db_instance(db_class)

    def __repr__(self) -> str:
        return "<Transaction ID Validation Plugin>"
