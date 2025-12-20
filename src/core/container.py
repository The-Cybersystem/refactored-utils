from discord.ext import commands
import discord
import logging
from sys import stdout


class Container:
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler("container.log"),
                logging.StreamHandler(stdout),
            ],
        )
        self.__logger: logging.Logger = logging.getLogger(__name__)

        # Initialise core services
        # self._validator = Validator()
        # self._security_service = SecurityService()
        # self._cache_service = CacheService()

        # Initialise database layer
        # self._repository = Repository()

        # economy abstraction not implemented

        # Initialise bot and related services
        intents = discord.Intents.all()
        self.__logger.debug("Creating bot...\nIntents: " + str(intents))
        self._bot = commands.Bot(command_prefix="/", intents=intents)
        self.__logger.debug("Bot created successfully.")
