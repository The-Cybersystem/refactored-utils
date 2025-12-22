from discord.ext import commands
import discord
import logging
from src.utils.validator import Validator
from src.services.security_service import SecurityService
from src.services.cache_service import CacheService
from src.repositories.mongodb_repository import MongoDBRepository


class Container:
    def __init__(self):
        # Initialise core services
        self._validator = Validator()
        self._security_service = SecurityService()
        self._cache_service = CacheService()

        # Initialise database layer
        self._repository = MongoDBRepository()

        # dicsord economy abstraction not implemented

        # Initialise bot and related services
        intents = discord.Intents.all()
        logging.debug("Creating bot...\nIntents: " + str(intents))
        self._bot = commands.Bot(command_prefix="/", intents=intents)
        logging.debug("Bot created successfully.")

        # minecraft server service not implemented

    @property
    def bot(self) -> commands.Bot:
        """Provices access to the Discord bot instance."""
        return self._bot

    @property
    def cache_service(self) -> CacheService:
        """Provides access to the cache service."""
        return self._cache_service

    @property
    def repository(self) -> MongoDBRepository:
        """Provides access to the mongo database repository."""
        return self._repository

    @property
    def security_service(self) -> SecurityService:
        """Provides access to the security service."""
        return self._security_service

    @property
    def validator(self) -> Validator:
        """Provides access to the validator service."""
        return self._validator
