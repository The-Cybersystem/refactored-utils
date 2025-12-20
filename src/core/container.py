from discord.ext import commands
import discord
import logging
from sys import stdout
from src.utils.validator import Validator
from src.services.security_service import SecurityService


class Container:
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler("main.log"),
                logging.StreamHandler(stdout),
            ],
        )
        self.__logger: logging.Logger = logging.getLogger(__name__)

        # Initialise core services
        self._validator = Validator()
        self._security_service = SecurityService()
        # self._cache_service = CacheService()

        # Initialise database layer
        # self._repository = Repository()

        # dicsord economy abstraction not implemented

        # Initialise bot and related services
        intents = discord.Intents.all()
        self.__logger.debug("Creating bot...\nIntents: " + str(intents))
        self._bot = commands.Bot(command_prefix="/", intents=intents)
        self.__logger.debug("Bot created successfully.")

        # minecraft server service not implemented

    @property
    async def bot(self) -> commands.Bot:
        """Provices access to the Discord bot instance."""
        return self._bot

    @property
    async def validator(self) -> Validator:
        """Provides access to the validator service."""
        return self._validator
