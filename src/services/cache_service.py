from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import asyncio


class CacheService:
    """
    An asynchronous, in-memory caching service.

    This service provides a simple key-value store with a time-to-live (TTL)
    for each entry. All operations are thread-safe using an asyncio.Lock.
    """

    def __init__(self):
        """Initializes the cache service."""
        logging.info("Initialising cache service...")
        self._cache: Dict[str, Any] = {}
        self._lock = asyncio.Lock()
        logging.info("Cache service initialised successfully.")

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves an item from the cache if it exists and has not expired.

        Args:
            key: The key of the item to retrieve.

        Returns:
            The cached value if found and valid, otherwise None.
        """
        async with self._lock:
            if key not in self._cache:
                return None

            cache_entry = self._cache[key]

            if datetime.now() >= cache_entry["expires"]:
                del self._cache[key]
                return None

            return cache_entry["value"]

    async def set(self, key: str, value: Dict[str, Any], ttl: int = 300):
        """
        Adds or updates an item in the cache with a specific TTL.

        Args:
            key: The key for the item.
            value: The value to store in the cache.
            ttl: The time-to-live for the item in seconds. Defaults to 300.
        """
        async with self._lock:
            self._cache[key] = {
                "value": value,
                "expires": datetime.now() + timedelta(seconds=ttl),
            }

    async def invalidate(self, key: str):
        """
        Removes an item from the cache immediately.

        If the key does not exist, the operation does nothing.

        Args:
            key: The key of the item to remove.
        """
        async with self._lock:
            try:
                del self._cache[key]
            except KeyError:
                pass
