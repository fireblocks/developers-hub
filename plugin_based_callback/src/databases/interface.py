from abc import ABC, abstractmethod


class DatabaseInterface(ABC):
    def __init__(self):
        self.supported_methods = {
            "find",
            "find_one",
            "insert_one",
            "insert_many"
        }

    @abstractmethod
    async def _connect(self, *args, **kwargs):
        """DB connection method to implement"""
        raise NotImplementedError("DB connection method was not implemented")

    async def _disconnect(self, *args, **kwargs):
        """DB disconnect method to implement"""
        raise NotImplementedError("DB disconnect method was not implemented")

    @abstractmethod
    async def execute_query(self, *args, **kwargs):
        """DB Query execution to implement"""
        raise NotImplementedError("Execute query was not implemented")

    @abstractmethod
    async def build_query(self, *args, **kwargs):
        """Build DB query"""
        raise NotImplementedError("Build Query was not implemented")
