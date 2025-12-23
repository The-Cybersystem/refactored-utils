from dotenv import load_dotenv
import logging
import os
import json
import json5
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


# Custom Exception for Configuration Errors
class ConfigurationError(Exception):
    """Custom exception for configuration-related errors."""

    pass


# --- Environment Variable Management ---


def load_and_validate_env_vars(required_vars: List[str]):
    """
    Loads environment variables from .env file and validates the presence of required variables.
    Raises ConfigurationError if any required variable is missing.
    """
    load_dotenv()
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ConfigurationError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )


def get_env_var(key: str, default: Any = None) -> Any:
    """
    Retrieves a single environment variable.
    """
    return os.getenv(key, default)


def get_env_var_as_list(key: str, default: List[str] | None = None) -> List[str]:
    """
    Retrieves a comma-separated environment variable as a list of strings.
    """
    value = get_env_var(key)
    if value is None:
        return default if default is not None else []
    return [item.strip().strip('"') for item in value.split(",") if item.strip()]


# --- JSON File Repository for Command Configuration ---


class CommandConfigRepository:
    """
    Handles all I/O operations for the command_config.json file.
    This class is responsible for reading, writing, and backing up the command configuration.
    """

    def __init__(self, config_path: Path, backup_dir: Path):
        self.config_path = config_path
        self.backup_dir = backup_dir
        self._ensure_config_exists()
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def _ensure_config_exists(self):
        """Ensures the configuration file exists, creating it if necessary."""
        if not self.config_path.exists():
            logging.info(
                f"Creating new command configuration file at {self.config_path}"
            )
            self._write_config({"guilds": {}})

    def _read_config(self) -> Dict[str, Any]:
        """Reads and decodes the JSON configuration file."""
        try:
            with self.config_path.open("r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, TypeError) as e:
            logging.error(f"Error reading command configuration: {e}")
            raise ConfigurationError(
                f"Failed to read or parse {self.config_path}"
            ) from e

    def _write_config(self, data: Dict[str, Any]):
        """Writes data to the JSON configuration file."""
        try:
            with self.config_path.open("w") as f:
                json.dump(data, f, indent=2)
        except (IOError, TypeError) as e:
            logging.error(f"Error writing command configuration: {e}")
            raise ConfigurationError(f"Failed to write to {self.config_path}") from e

    def get_all(self) -> Dict[str, Any]:
        """Returns the entire command configuration."""
        return self._read_config()

    def get_commands_for_guild(self, guild_id: str) -> List[str]:
        """Gets the list of allowed commands for a specific guild."""
        config = self.get_all()
        return config.get("guilds", {}).get(guild_id, [])

    def update_commands_for_guild(self, guild_id: str, commands: List[str]):
        """Updates the command list for a specific guild."""
        if not isinstance(commands, list):
            raise ConfigurationError("Invalid commands list: must be a list.")

        self.backup()  # Backup before making changes

        config = self.get_all()
        if "guilds" not in config:
            config["guilds"] = {}
        config["guilds"][guild_id] = commands
        self._write_config(config)
        logging.info(f"Updated command configuration for guild {guild_id}.")

    def backup(self):
        """Creates a timestamped backup of the current command configuration."""
        try:
            config = self._read_config()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = (
                self.backup_dir / f"{self.config_path.stem}_backup_{timestamp}.json"
            )

            with backup_file.open("w") as f:
                json.dump(config, f, indent=2)
            logging.info(f"Created configuration backup at {backup_file}")
        except Exception as e:
            logging.error(f"Error creating config backup: {e}")
            # Do not re-raise; a backup failure shouldn't halt the main operation.

    def restore(self, backup_path: Path) -> bool:
        """Restores the configuration from a specified backup file."""
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found at {backup_path}")

        try:
            with backup_path.open("r") as f:
                config = json.load(f)

            if "guilds" not in config or not isinstance(config.get("guilds"), dict):
                raise ConfigurationError(
                    "Invalid backup file: missing 'guilds' dictionary."
                )

            self._write_config(config)
            logging.info(f"Restored configuration from {backup_path}")
            return True
        except (json.JSONDecodeError, ConfigurationError, IOError) as e:
            logging.error(f"Error restoring config backup: {e}")
            return False


# --- JSON5 Server Configuration ---


def get_server_config(guild_id: str, config_path: Path) -> Dict[str, Any]:
    """
    Reads a server's configuration from a JSON5 file.
    Returns an empty dictionary if the file doesn't exist or an error occurs.
    """
    if not config_path.exists():
        return {}

    try:
        with config_path.open("r") as f:
            all_configs = json5.load(f)
            return all_configs.get(guild_id, {})
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"Error reading server config for guild {guild_id}: {e}")
        return {}


# --- Main Config Facade ---


class ConfigManager:
    """
    A facade for accessing various configuration sources.
    It provides a single point of entry for configuration needs, delegating
    to specialized functions or classes for handling the details.
    """

    def __init__(self):
        logging.info("Initializing configuration manager...")
        self._setup_env_vars()
        self._setup_command_config_repo()
        self._setup_server_config()
        logging.info("Configuration manager initialized successfully.")

    def _setup_env_vars(self):
        """Loads and validates required environment variables."""
        self.required_env_vars = ["APPROVED_GUILDS", "TOKEN", "DB"]
        load_and_validate_env_vars(self.required_env_vars)
        logging.info("Environment variables validated.")

    def _setup_command_config_repo(self):
        """Initializes the command configuration repository."""
        command_config_file = Path("command_config.json")
        backup_dir = Path("backups/")
        self.command_config_repo = CommandConfigRepository(
            command_config_file, backup_dir
        )

    def _setup_server_config(self):
        """Initializes the server configuration path."""
        self.server_config_file = Path("welcomer_config.json5")

    # --- Environment Variable Access ---
    def get(self, key: str, default: Any = None) -> Any:
        return get_env_var(key, default)

    def get_approved_guilds(self) -> List[int]:
        guild_ids_str = get_env_var_as_list("APPROVED_GUILDS")
        return [int(gid) for gid in guild_ids_str if gid.isdigit()]

    # --- Command Config Access (via Repository) ---
    def get_command_config(self) -> Dict[str, Any]:
        return self.command_config_repo.get_all()

    def get_commands_for_guild(self, guild_id: str) -> List[str]:
        return self.command_config_repo.get_commands_for_guild(guild_id)

    def update_command_config(self, guild_id: str, commands: List[str]):
        self.command_config_repo.update_commands_for_guild(guild_id, commands)

    # --- Server Config Access ---
    def get_server_config(self, guild_id: str) -> Dict[str, Any]:
        return get_server_config(guild_id, self.server_config_file)

