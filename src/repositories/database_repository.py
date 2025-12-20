from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class DatabaseRepository(ABC):
    """Abstract base class for database repositories."""

    @abstractmethod
    async def find_one(
        self, collection: str, query: Dict[str, Any], guild_id: Optional[str] = None
    ) -> Optional[Dict]:
        """Find a single document in a collection."""
        raise NotImplementedError

    @abstractmethod
    async def update_one(
        self,
        collection: str,
        query: Dict[str, Any],
        update: Dict[str, Any],
        guild_id: Optional[str] = None,
        upsert: bool = False,
    ) -> bool:
        """Update one document in collection"""
        raise NotImplementedError

    @abstractmethod
    async def insert_one(self, collection: str, document: Dict[str, Any]) -> bool:
        """Insert one document into collection"""
        raise NotImplementedError
