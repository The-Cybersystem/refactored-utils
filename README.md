# Refactored Utils - Discord Bot

This repository provides a robust and well-structured foundation for building Python-based Discord bots. It features a clean architecture that separates concerns, making it easy to extend and maintain. The framework is designed for developers looking for a scalable starting point for their own Discord bot projects.

This project is intended as a base for others to use and adapt under the terms of the `LICENSE.md` file.

## Features

- **Modular Cogs:** Commands are organized into "cogs," allowing for easy management and scaling of bot features.
- **Clean Architecture:** A clear separation between application logic, data repositories, and services.
- **Asynchronous from the Ground Up:** Built with `asyncio`, `motor` for non-blocking database operations, and `aiologger` for async logging.
- **Configuration-driven:** Bot settings are managed through environment variables and dedicated JSON configuration files.
- **Repository Pattern:** Decouples the application from the database, making it easier to manage data logic and potentially swap database backends.
- **Production Ready:** Includes a configuration for the PM2 process manager to run the bot in a production environment.
- **Error Handling & Logging:** Comes with pre-configured logging and centralized error handling.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/the-cybersystem/refactored-utils.git
    cd refactored-utils
    ```

2.  **Set up a Python virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
    *(On Windows, use `.\.venv\Scripts\activate`)*

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

The bot is configured through a combination of a `.env` file for secrets and JSON files for public or dynamic settings.

1.  **Create the environment file:**

    Create a file named `.env` in the root of the project directory.

2.  **Add environment variables:**

    Open the `.env` file and add the following required variables.

    ```env
    # Your Discord Bot's authentication token
    TOKEN="YOUR_DISCORD_BOT_TOKEN"

    # The connection string for your MongoDB database
    DB="mongodb://localhost:27017/your_db_name"

    # A comma-separated list of Guild (Server) IDs where the bot is approved to run
    APPROVED_GUILDS="GUILD_ID_1,GUILD_ID_2"
    ```

3.  **Review other configuration files:**

    -   `welcomer_config.json5`: Contains settings for the "welcomer" cog, such as welcome messages or channels. You can modify this file to change the behavior of the welcome feature on a per-guild basis.
    -   `command_config.json`: Used to manage which commands are enabled or disabled for specific guilds. This is managed dynamically by the bot but can be pre-configured.

## Usage

### Running in Development Mode

To run the bot directly for development and testing:

```bash
python3 main.py
```

### Running in Production with PM2

The included `ecosystem.config.js` file is configured to run the bot using [PM2](https://pm2.keymetrics.io/), a process manager for Node.js applications that can also manage Python scripts. This is the recommended way to run the bot in production.

1.  **Install PM2** (if you haven't already):
    ```bash
    npm install pm2 -g
    ```

2.  **Start the bot:**
    ```bash
    pm2 start ecosystem.config.js
    ```

3.  **Manage the process:**
    -   To view logs: `pm2 logs`
    -   To stop the bot: `pm2 stop ecosystem.config.js`
    -   To restart the bot: `pm2 restart ecosystem.config.js`

## Modifying and Extending the Bot

The project's structure is designed to be modular and easy to extend.

-   **`src/`**: The main source code directory.
    -   **`cogs/`**: This is where you should add new commands. Create a new Python file in this directory and define a class that inherits from `discord.ext.commands.Cog`. The bot will automatically discover and load it.
    -   **`core/`**: Contains the core application logic, including the main `Application` class and the dependency injection `Container`.
    -   **`repositories/`**: Handles all database interactions. If you need to change how data is stored or retrieved, this is the place to do it.
    -   **`services/`**: Contains higher-level business logic that uses repositories and other services.
    -   **`utils/`**: Houses utility modules for configuration, logging, error handling, etc.