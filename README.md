# Stying's Sticky Bot 📌📎

A Discord bot that allows server administrators to set, manage, and display sticky messages in channels. This bot provides commands for setting sticky messages, disabling or enabling them, and removing them when no longer needed. 

## Features

- Set sticky messages (plain text or embedded, with custom color/title/image) in any channel.
- Sticky reposts automatically based on chat activity: it tracks message length and line breaks
  and reposts once roughly a "screen's worth" of chat has passed (configurable per channel), instead
  of reposting instantly on every single message.
- Edit an existing sticky's text in place without removing and recreating it.
- Manage sticky messages with commands to enable, disable, and remove them (optionally targeting
  another channel by mention).
- Display all active or inactive sticky messages within a server, including who last updated them.
- Persists sticky messages in a local SQLite database (`sticky.db`).
- A background safety-net check reposts a sticky if its message was ever deleted or missed.

## Commands (slash commands only — no message-prefix commands)

| Command                                          | Description                                                                 | Permissions Required |
|---------------------------------------------------|------------------------------------------------------------------------------|-----------------------|
| `/help`                                          | Shows the help message with a list of available commands.                    | None                  |
| `/setsticky <message>`                           | Sets a sticky message in the current channel.                                | Manage Messages       |
| `/setstickyembed <message> [color] [title] [image]` | Sets a sticky message with an embedded format, optionally customized.     | Manage Messages       |
| `/stickyedit <message>`                          | Edits the text of the existing sticky, keeping its other settings.           | Manage Messages       |
| `/removesticky [channel]`                        | Removes the sticky message in the current or specified channel.              | Manage Messages       |
| `/getsticky`                                     | Displays all active and inactive sticky messages in the server.              | Manage Messages       |
| `/stickydisable [channel]`                       | Disables a sticky message without removing it.                               | Manage Messages       |
| `/stickyenable [channel]`                        | Re-enables a disabled sticky message.                                        | Manage Messages       |
| `/setstickythreshold <lines>`                    | Sets how many lines of chat activity occur before the sticky reposts.        | Manage Messages       |

When inviting the bot, make sure to include the `applications.commands` OAuth2 scope (in addition to
`bot`) so its slash commands can register in your server.

## Requirements

- Python 3.8+
- `discord.py` library (v2.4.0 or later)
- `python-dotenv` for environment variable management
- `aiosqlite` for persistent storage

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

The bot is controlled entirely through Discord's slash commands (type `/` in a channel to see them).
Only users with the `Manage Messages` permission can use the management commands.

### Setting a Sticky Message

To set a sticky message in the current channel:

```
/setsticky message: Your message here
```

### Setting an Embedded Sticky Message

To set a sticky message with an embed format (color, title, and image are optional):

```
/setstickyembed message: Your embedded message here color: #5865F2 title: Read Me First
```

### Editing a Sticky Message

To update the text of an existing sticky without recreating it (keeps its embed/color/threshold settings):

```
/stickyedit message: Your updated message here
```

### Disabling a Sticky Message

To disable a sticky message in the current (or another) channel without removing it:

```
/stickydisable
/stickydisable channel: #announcements
```

### Enabling a Sticky Message

To re-enable a disabled sticky message:

```
/stickyenable
/stickyenable channel: #announcements
```

### Removing a Sticky Message

To remove the sticky message from the current (or another) channel:

```
/removesticky
/removesticky channel: #announcements
```

### Listing All Sticky Messages

To show all active and inactive sticky messages in your server:

```
/getsticky
```

### Adjusting the Repost Threshold

Stickies repost once roughly this many lines of chat activity have passed, instead of on every
message:

```
/setstickythreshold lines: 20
```

## Configuration

Sticky messages are saved in a local SQLite database (`sticky.db`) located in the same directory as the
bot script. If an older `sticky_config.json` is found on first run (and no `sticky.db` exists yet), it is
automatically imported into the database.


## Contributing

If you want to contribute to this project, please feel free to fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
