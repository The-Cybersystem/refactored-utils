import motor.motor_asyncio  # type: ignore
from motor.motor_asyncio import AsyncIOMotorClient  # type: ignore
from src.repositories.database_repository import DatabaseRepository
from typing import Optional, Dict, Any, List
from src.utils.config import ConfigManager
import asyncio
import logging


class MongoDBRepository(DatabaseRepository):
    """Asynchronous MongoDB implementation of DatabaseRepository using motor.

    This class provides async methods to interact with a MongoDB database,
    including finding, updating, and inserting documents.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    _client = None  # MongoDB client instance
    _db = None  # Database instance

    @classmethod
    async def _get_client(cls):
        """Get or create an async MongoDB client with connection pooling.

        Returns:
            AsyncIOMotorClient: The MongoDB client instance.

        Raises:
            Exception: If the connection to MongoDB fails.
        """
        if cls._client is None:
            config = ConfigManager()
            cls._client = AsyncIOMotorClient(
                config.get("DB"),
                maxPoolSize=100,  # Maximum number of connections in the pool
                minPoolSize=10,  # Minimum number of connections in the pool
                connectTimeoutMS=30000,  # Connection timeout in milliseconds
                socketTimeoutMS=30000,  # Socket timeout in milliseconds
            )
            try:
                # Verify connection asynchronously
                await cls._client.admin.command("ping")
            except Exception as e:
                logging.error(f"MongoDB connection failed: {str(e)}")
                raise
        return cls._client

    @classmethod
    async def _get_db(cls):
        """Get the async database instance.

        Returns:
            AsyncIOMotorDatabase: The MongoDB database instance.
        """
        if cls._db is None:
            client = await cls._get_client()
            cls._db = client["psrp"]  # Access the 'psrp' database
        return cls._db

    async def _get_collection(self, collection_path: str):
        """
        Get a collection object from a dot-separated collection path asynchronously.

        Args:
            collection_path (str): Dot-separated path, e.g., 'psrp.economy'.

        Returns:
            AsyncIOMotorCollection: The motor async collection object.

        Raises:
            ValueError: If the collection path is invalid.
        """
        if not collection_path or "." not in collection_path:
            raise ValueError(
                "Invalid collection path. It must be in 'database.collection' format."
            )

        db_name, collection_name = collection_path.split(".", 1)
        client = await self._get_client()
        db = client[db_name]
        return db[collection_name]

    async def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict]:
        """Find a single document in the specified collection asynchronously.

        Args:
            collection (str): The dot-separated collection path.
            query (Dict[str, Any]): The query to filter documents.

        Returns:
            Optional[Dict]: The found document, or None if not found.

        Raises:
            Exception: If an error occurs during the database operation.
        """
        try:
            coll = await self._get_collection(collection)
            document = await coll.find_one(query)
            return document

        except Exception as e:
            logging.error(f"Database find_one error: {str(e)}")
            raise

    async def find_one_with_projection(
        self,
        collection: str,
        query: Dict[str, Any],
        projection: Optional[Dict[str, int]] = None,
    ) -> Optional[Dict]:
        """Find a single document in the specified collection asynchronously with optional field projection.

        Args:
            collection (str): The dot-separated collection path.
            query (Dict[str, Any]): The query to filter documents.
            projection (Optional[Dict[str, int]]): The fields to include or exclude. Defaults to None.

        Returns:
            Optional[Dict]: The found document with only the projected fields, or None if not found.

        Raises:
            Exception: If an error occurs during the database operation.
        """
        try:
            coll = await self._get_collection(collection)
            document = await coll.find_one(query, projection=projection)
            return document

        except Exception as e:
            logging.error(f"Database find_one_with_projection error: {str(e)}")
            raise

    async def update_one(
        self,
        collection: str,
        query: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False,
    ) -> bool:
        """Update a single document in the specified collection asynchronously.

        Args:
            collection (str): The dot-separated collection path.
            query (Dict[str, Any]): The query to filter documents.
            update (Dict[str, Any]): The update operations to apply.
            upsert (bool): If True, insert a new document if no documents match the query.

        Returns:
            bool: True if the document was modified, False otherwise.

        Raises:
            Exception: If an error occurs during the database operation.
        """
        try:
            coll = await self._get_collection(collection)
            result = await coll.update_one(query, update, upsert=upsert)

            return result.modified_count > 0
        except Exception as e:
            logging.error(f"Database update_one error: {str(e)}")
            raise

    async def insert_one(self, collection: str, document: Dict[str, Any]) -> bool:
        """Insert a single document into the specified collection asynchronously.

        Args:
            collection (str): The dot-separated collection path.
            document (Dict[str, Any]): The document to insert.

        Returns:
            bool: True if the document was inserted, False otherwise.

        Raises:
            Exception: If an error occurs during the database operation.
        """
        try:
            coll = await self._get_collection(collection)
            result = await coll.insert_one(document)

            return result.inserted_id is not None
        except Exception as e:
            logging.error(f"Database insert_one error: {str(e)}")
            raise

    async def insert_scheduled_task(self, document: Dict[str, Any]) -> bool:
        """Insert a scheduled task document into the scheduled_sessions collection asynchronously."""
        try:
            coll = await self._get_collection("psrp.scheduled_sessions")
            result = await coll.insert_one(document)
            return result.inserted_id is not None
        except Exception as e:
            logging.error(f"Error inserting scheduled task: {str(e)}")
            raise

    async def update_scheduled_task(
        self, query: Dict[str, Any], update: Dict[str, Any], upsert: bool = False
    ) -> bool:
        """Update a scheduled task document in the scheduled_sessions collection asynchronously."""
        try:
            coll = await self._get_collection("psrp.scheduled_sessions")
            result = await coll.update_one(query, update, upsert=upsert)
            return result.modified_count > 0
        except Exception as e:
            logging.error(f"Error updating scheduled task: {str(e)}")
            raise

    async def find_scheduled_tasks(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find scheduled task documents matching the query in the scheduled_sessions collection asynchronously."""
        try:
            coll = await self._get_collection("psrp.scheduled_sessions")
            cursor = coll.find(query)
            results = []
            async for document in cursor:
                results.append(document)
            return results
        except Exception as e:
            logging.error(f"Error finding scheduled tasks: {str(e)}")
            raise

    async def find_many(
        self, collection: str, query: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Find multiple documents in the specified collection asynchronously.

        Args:
            collection (str): The dot-separated collection path.
            query (Dict[str, Any]): The query to filter documents.

        Returns:
            List[Dict[str, Any]]: The list of found documents.

        Raises:
            Exception: If an error occurs during the database operation.
        """
        try:
            coll = await self._get_collection(collection)
            cursor = coll.find(query)
            results = []
            async for document in cursor:
                results.append(document)
            return results
        except Exception as e:
            logging.error(f"Database find_many error: {str(e)}")
            raise
