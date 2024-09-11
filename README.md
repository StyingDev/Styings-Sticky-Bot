# Stying's Sticky Bot 📌📄

A Discord bot that allows server administrators to set, manage, and display sticky messages in channels. This bot provides commands for setting sticky messages, disabling or enabling them, and removing them when no longer needed. [Invite the Bot!](https://discord.com/oauth2/authorize?client_id=1232239465502605352&permissions=277025515584&integration_type=0&scope=bot)

## Features

- Set sticky messages (plain text or embedded) in any channel.
- Manage sticky messages with commands to enable, disable, and remove them.
- Display all active or inactive sticky messages within a server.
- Uses a JSON configuration file to save sticky messages persistently.
- Supports both standard and embedded sticky messages.
- Configurable via environment variables.

## Commands (Slash commands supported)

| Command                 | Description                                                         | Permissions Required       |
|-------------------------|---------------------------------------------------------------------|-----------------------------|
| `C!help`                | Shows the help message with a list of available commands.            | None                        |
| `C!set_sticky`          | Sets a sticky message in the current channel.                        | Manage Messages             |
| `C!set_sticky_embed`    | Sets a sticky message with an embedded format.                       | Manage Messages             |
| `C!remove_sticky`       | Removes the sticky message in the current channel.                   | Manage Messages             |
| `C!get_sticky`          | Displays all active and inactive sticky messages in the server.      | Manage Messages             |
| `C!sticky_disable`      | Disables a sticky message without removing it.                       | Manage Messages             |
| `C!sticky_enable`       | Re-enables a disabled sticky message.                                | Manage Messages             |

## Requirements

- Python 3.8+
- `discord.py` library (v2.4.0 or later)
- `python-dotenv` for environment variable management

## Setup

1. Clone the repository:

    ```sh
    git clone https://github.com/StyingDev/Styings-Sticky-Bot.git
    cd Styings-sticky-bot
    ```

2. Install the required dependencies:

    ```sh
    pip install -r requirements.txt
    ```

3. Create a `.env` file in the root directory of the project and add your Discord bot token:

    ```env
    TOKEN=your_bot_token_here
    ```

4. Run the bot:

    ```sh
    python main.py
    ```

## Usage

The bot provides several commands to manage sticky messages. Only users with the `Manage Messages` permission can use these commands.

### Setting a Sticky Message

To set a sticky message in the current channel:

```sh
C!set_sticky Your message here
```

### Setting an Embedded Sticky Message

To set a sticky message with an embed format:

```sh
C!set_sticky_embed Your embedded message here
```

### Disabling a Sticky Message

To disable a sticky message in the current channel without removing it:

```sh
C!sticky_disable
```

### Enabling a Sticky Message

To re-enable a disabled sticky message:

```sh
C!sticky_enable
```

### Removing a Sticky Message

To remove the sticky message from the current channel:

```sh
C!remove_sticky
```

### Listing All Sticky Messages

To show all active and inactive sticky messages in your server:

```sh
C!get_sticky
```

## Configuration

Sticky messages are saved in a JSON configuration file (`sticky_config.json`) located in the same directory as the bot script. This file stores the sticky messages for each channel and their statuses.


## Contributing

If you want to contribute to this project, please feel free to fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
