from abc import ABC, abstractmethod
from src.databases.interface import DatabaseInterface


class PluginInterface(ABC):
    def __init__(self):
        self.db: DatabaseInterface = None

    @abstractmethod
    async def init(self, *args, **kwargs):
        """Your plugin initialization"""
        raise NotImplementedError()

    async def set_db_instance(self, db):
        self.db = db()

    @abstractmethod
    async def process_request(self, data):
        """Plugin logic entrypoint"""
        raise NotImplementedError()

    @abstractmethod
    async def _create_db_instance(self, db_type: str):
        """Create your DB instance"""
        raise NotImplementedError()

    @abstractmethod
    def __repr__(self):
        raise NotImplementedError()
