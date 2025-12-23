import asyncio
import discord
from discord.ext import commands
from typing import Type
from src.core.container import Container
from aiologger import Logger as AsyncLogger  # Import aiologger for type hinting
import logging  # Import standard logging for type hinting
from src.utils.config import ConfigManager

# Import cogs
from src.cogs.utility_commands import UtilityCommands


class Application:
    """
    Main application class for the Discord bot.

    This class orchestrates the bot's lifecycle, including cog loading,
    command synchronization, and event handling.

    Attributes:
        logger: The aiologger instance for the application.
        container: The dependency injection container.
        bot: The Discord bot instance.
        config_manager: The configuration manager.
        admin_user (discord.User | None): The admin user, fetched on startup.
        CUBE (discord.User | None): A special user, fetched on startup.
    """

    def __init__(
        self,
        bot: commands.Bot,
        container: Container,
        async_logger: AsyncLogger,
        sync_logger: logging.Logger,
    ):
        """
        Initializes the Application instance.

        Args:
            bot: The Discord bot instance.
            container: The dependency injection container.
            async_logger: The aiologger instance to use for asynchronous logging.
            sync_logger: The standard logging instance to use for synchronous logging.
        """
        self.async_logger = async_logger
        self.sync_logger = sync_logger
        self.bot = bot
        self.container = container
        self.config_manager = ConfigManager()

        self.admin_user: discord.User | None = None
        self.CUBE: discord.User | None = None

        self.bot.setup_hook = self._async_init

    async def _async_init(self):
        """Performs asynchronous initialization tasks."""
        await self.async_logger.info("Running async initialization...")
        await self._setup_event_handlers()
        try:
            self.admin_user = await self.bot.fetch_user(738434699021778945)
            await self.async_logger.info(f"Admin user: {self.admin_user.name}")
            self.CUBE = await self.bot.fetch_user(730972218355482714)
            await self.async_logger.info(f"CUBE user: {self.CUBE.name}")
        except discord.NotFound:
            await self.async_logger.warning("Could not find admin or CUBE user.")

        await self._setup_cogs()
        await self.async_logger.info("Async initialization complete.")

    async def _load_cog(self, cog_class: Type[commands.Cog]):
        """
        Loads a single cog and logs the result.

        Args:
            cog_class: The class of the cog to load.
        """
        cog_name = cog_class.__name__
        await self.async_logger.debug(f"Loading {cog_name} cog...")
        try:
            await self.bot.add_cog(cog_class(self.bot))
            await self.async_logger.info(f"{cog_name} cog loaded successfully.")
        except Exception as e:
            await self.async_logger.error(f"Failed to load cog {cog_name}: {e}")
            raise

    async def _setup_cogs(self):
        """Loads all application cogs."""
        await self.async_logger.info("Loading cogs...")
        cogs_to_load = [
            UtilityCommands,
        ]
        for cog in cogs_to_load:
            await self._load_cog(cog)
        await self.async_logger.info("All cogs loaded.")

    async def _sync_guild_commands(self, guild: discord.Guild):
        """
        Syncs commands for a specific guild based on the config.

        Args:
            guild: The guild to sync commands for.
        """
        await self.async_logger.info(f"Syncing commands for guild: {guild.name}")
        allowed_commands = self.config_manager.get_commands_for_guild(str(guild.id))

        self.bot.tree.clear_commands(guild=guild)
        if not allowed_commands:
            await self.async_logger.info(
                f"No commands configured for guild {guild.name}."
            )
            await self.bot.tree.sync(guild=guild)
            return

        for name in allowed_commands:
            command = self.bot.tree.get_command(name)
            if command:
                self.bot.tree.add_command(command, guild=guild)

        await self.bot.tree.sync(guild=guild)
        await self.async_logger.info(
            f"Synced {len(allowed_commands)} commands for guild {guild.name}."
        )

    async def _setup_commands(self):
        """Synchronizes all application commands with Discord."""
        await self.async_logger.info("Starting command synchronization...")
        approved_guild_ids = self.config_manager.get_approved_guilds()

        for guild_id in approved_guild_ids:
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                await self.async_logger.warning(
                    f"Could not find guild with ID {guild_id}."
                )
                continue
            await self._sync_guild_commands(guild)

        # Clear global commands
        self.bot.tree.clear_commands(guild=None)
        await self.bot.tree.sync(guild=None)
        await self.async_logger.info("Global commands cleared.")
        await self.async_logger.info("Command synchronization complete.")

    async def _check_approved_guilds(self):
        """Leaves any guilds that are not in the approved list."""
        approved_guilds = self.config_manager.get_approved_guilds()
        for guild in self.bot.guilds:
            if guild.id not in approved_guilds:
                await self.async_logger.warning(
                    f"Leaving unapproved guild: {guild.name}"
                )
                await guild.leave()

    async def on_ready(self):
        """
        Called when the bot is ready.

        Finalizes setup by syncing commands, checking guilds, and setting presence.
        """
        await self._setup_commands()
        await self._check_approved_guilds()
        await self.async_logger.info(f"Logged in as {self.bot.user.name}.")  # type: ignore
        await self.bot.change_presence(
            status=discord.Status.online,
            activity=discord.Game("/help #RTFM"),
        )

    async def on_message(self, message: discord.Message):
        """
        Handles incoming messages.

        Args:
            message: The message that was sent.
        """
        if message.author.bot:
            return
        # The bot will no longer process commands from on_message
        # and will rely on application commands (slashes).

    async def on_member_join(self, member: discord.Member):
        """
        Sends a welcome message when a new member joins.

        Args:
            member: The member who joined.
        """
        guild_id = str(member.guild.id)
        server_config = self.config_manager.get_server_config(guild_id)

        if not server_config or not server_config.get("welcome", {}).get("enabled"):
            return

        welcome_config = server_config["welcome"]
        channel_id = welcome_config.get("channel_id")
        if not channel_id or not (channel := self.bot.get_channel(channel_id)):
            await self.async_logger.warning(
                f"Welcome channel not found for guild {guild_id}."
            )
            return

        message_text = welcome_config.get("message", "").format(user=member.mention)
        embed_config = welcome_config.get("embed")

        embed = None
        if embed_config:
            embed = discord.Embed.from_dict(embed_config)

        try:
            await channel.send_message(content=message_text, embed=embed)  # type: ignore
            await self.async_logger.info(
                f"Sent welcome to {member.name} in {member.guild.name}."
            )
        except discord.Forbidden:
            await self.async_logger.error(
                f"Missing perms to send welcome in {channel.name}."  # type: ignore
            )
        except Exception as e:
            await self.async_logger.error(f"Failed to send welcome message: {e}")

    async def _setup_event_handlers(self):
        """Registers event handlers for the bot."""
        await self.async_logger.debug("Setting up event handlers.")
        self.bot.event(self.on_ready)
        self.bot.event(self.on_message)
        self.bot.event(self.on_member_join)

    def run(self, token: str):
        """
        Starts the bot.

        Args:
            token: The Discord bot token.
        """
        try:
            self.bot.run(token)
        except Exception as e:
            self.sync_logger.error(f"Error starting bot: {e}")
            raise
