import discord
from discord.ext import commands, tasks
import os
import logging
from dotenv import load_dotenv
import json
import datetime

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Configure logging
logging.basicConfig(level=logging.WARNING)  # Change to WARNING to reduce verbosity

# Set up intents and bot
intents = discord.Intents.all()
client = commands.Bot(command_prefix="C!", intents=intents)

# Config file
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'sticky_config.json')

# Load sticky messages configuration
def load_sticky_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"sticky_messages": {}}

# Save sticky messages configuration
def save_sticky_config(config):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        logging.error(f"Error saving config: {e}")

# Load the initial config without clearing
sticky_config = load_sticky_config()

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="🌲linktr.ee/Stying"))
    print(f'Logged in as {client.user.name}')
    await client.tree.sync()
    check_sticky_messages.start()

client.remove_command("help")

@client.hybrid_command(name='help', help='Execute for help.')
async def help(ctx):
    embed = discord.Embed(title="Sticky Bot Help", description="Here are the available commands for the Sticky Bot:", color=discord.Color(0x747c8b))

    embed.add_field(name="C!help", value="Shows this message.", inline=False)
    embed.add_field(name="C!set_sticky", value="Set a sticky message in the current channel.", inline=False)
    embed.add_field(name="C!set_sticky_embed", value="Set a sticky message with an embed.", inline=False)
    embed.add_field(name="C!remove_sticky", value="Remove the sticky message in the current channel.", inline=False)
    embed.add_field(name="C!get_sticky", value="Show all active and stopped stickies in your server.", inline=False)
    embed.add_field(name="C!sticky_disable", value="Disable a sticky message without removing it.", inline=False)
    embed.add_field(name="C!sticky_enable", value="Re-enable a disabled sticky message.", inline=False)
    

    embed.set_footer(text="📌 Commands require 'Manage Messages' permission.")

    await ctx.send(embed=embed)

@client.hybrid_command(name='set_sticky')
@commands.has_permissions(manage_messages=True)
async def set_sticky(ctx, *, message: str):
    """Set a sticky message in the current channel."""
    guild_id = str(ctx.guild.id)
    channel_id = str(ctx.channel.id)

    if guild_id not in sticky_config["sticky_messages"]:
        sticky_config["sticky_messages"][guild_id] = {}

    sticky_config["sticky_messages"][guild_id][channel_id] = {
        "message": message,
        "message_id": None,
        "active": True  # Set the sticky message to active by default
    }
    save_sticky_config(sticky_config)
    await post_sticky_message(ctx.channel)
    await ctx.send("Sticky message set!")

@client.hybrid_command(name='get_sticky')
@commands.has_permissions(manage_messages=True)
async def get_sticky(ctx):
    """Show all active and stopped stickies in your server."""
    guild_id = str(ctx.guild.id)
    sticky_messages = sticky_config.get("sticky_messages", {}).get(guild_id, {})
    
    if not sticky_messages:
        await ctx.send("No sticky messages set in this server.")
        return

    embed = discord.Embed(title="Sticky Messages", description="Here are the sticky messages for this server:", color=discord.Color.blue())
    for channel_id, sticky_info in sticky_messages.items():
        channel = client.get_channel(int(channel_id))
        if channel is None:
            embed.add_field(name=f"Channel: [Deleted or Inaccessible: {channel_id}]", 
                            value=f"Status: Unknown\nMessage: {sticky_info['message']}", inline=False)
            continue
        status = "Active" if sticky_info.get("active") else "Inactive"
        embed.add_field(name=f"Channel: {channel.name}", 
                        value=f"Status: {status}\nMessage: {sticky_info['message']}", inline=False)

    
    await ctx.send(embed=embed)

@client.hybrid_command(name='set_sticky_embed')
@commands.has_permissions(manage_messages=True)
async def set_sticky_embed(ctx, *, message: str):
    """Set a sticky message with an embed."""
    guild_id = str(ctx.guild.id)
    channel_id = str(ctx.channel.id)
    
    if guild_id not in sticky_config["sticky_messages"]:
        sticky_config["sticky_messages"][guild_id] = {}

    sticky_config["sticky_messages"][guild_id][channel_id] = {
        "message": message,
        "message_id": None,
        "embed": True,
        "active": True  # Set the sticky embed to active by default
    }
    save_sticky_config(sticky_config)
    await post_sticky_message(ctx.channel)
    await ctx.send("Sticky embed message set!")

@client.hybrid_command(name='sticky_disable')
@commands.has_permissions(manage_messages=True)
async def sticky_disable(ctx):
    """Disable the sticky message in the current channel."""
    guild_id = str(ctx.guild.id)
    channel_id = str(ctx.channel.id)

    if guild_id in sticky_config["sticky_messages"] and channel_id in sticky_config["sticky_messages"][guild_id]:
        sticky_info = sticky_config["sticky_messages"][guild_id][channel_id]
        sticky_info["active"] = False
        save_sticky_config(sticky_config)
        if sticky_info.get("message_id"):
            try:
                old_message = await ctx.channel.fetch_message(sticky_info["message_id"])
                await old_message.delete()
            except discord.NotFound:
                pass
        await ctx.send("Sticky message disabled!")
    else:
        await ctx.send("No sticky message set in this channel.")

@client.hybrid_command(name='sticky_enable')
@commands.has_permissions(manage_messages=True)
async def sticky_enable(ctx):
    """Re-enable the sticky message in the current channel."""
    guild_id = str(ctx.guild.id)
    channel_id = str(ctx.channel.id)

    if guild_id in sticky_config["sticky_messages"] and channel_id in sticky_config["sticky_messages"][guild_id]:
        sticky_info = sticky_config["sticky_messages"][guild_id][channel_id]
        sticky_info["active"] = True
        save_sticky_config(sticky_config)
        await post_sticky_message(ctx.channel)
        await ctx.send("Sticky message re-enabled!")
    else:
        await ctx.send("No sticky message set in this channel.")

async def post_sticky_message(channel):
    """Post the sticky message and save the message ID."""
    guild_id = str(channel.guild.id)
    channel_id = str(channel.id)
    sticky_info = sticky_config["sticky_messages"].get(guild_id, {}).get(channel_id)
    
    if sticky_info and sticky_info.get("active"):  # Check if sticky message is active
        # Delete old sticky message if exists
        if sticky_info.get("message_id"):
            try:
                old_message = await channel.fetch_message(sticky_info["message_id"])
                await old_message.delete()
            except discord.NotFound:
                pass
        
        if sticky_info.get("embed"):
            embed = discord.Embed(description=sticky_info["message"], color=discord.Color(0x747c8b))
            embed.title = "Sticky Message"  # Add title here
            msg = await channel.send(embed=embed)
        else:
            msg = await channel.send(sticky_info["message"])
        
        sticky_info["message_id"] = msg.id
        save_sticky_config(sticky_config)

@tasks.loop(minutes=1)
async def check_sticky_messages():
    """Check and maintain sticky messages."""
    now = datetime.datetime.now(datetime.timezone.utc)  # Use timezone-aware UTC datetime
    for guild_id, channels in sticky_config["sticky_messages"].items():
        if not isinstance(channels, dict):
            logging.warning(f"Invalid structure for guild {guild_id}: expected dictionary, got {type(channels)}")
            continue

        for channel_id, sticky_info in list(channels.items()):
            if not channel_id.isdigit():
                logging.warning(f"Invalid channel ID in sticky config: {channel_id}")
                continue
            if not isinstance(sticky_info, dict) or 'message' not in sticky_info or 'message_id' not in sticky_info:
                logging.warning(f"Invalid sticky info for guild {guild_id}, channel {channel_id}: {sticky_info}")
                continue

            channel = client.get_channel(int(channel_id))
            if channel:
                try:
                    last_message = await channel.fetch_message(channel.last_message_id)
                    if last_message.id != sticky_info["message_id"]:
                        await post_sticky_message(channel)
                except discord.NotFound:
                    await post_sticky_message(channel)
                except Exception as e:
                    logging.error(f"Error in check_sticky_messages for guild {guild_id}, channel {channel_id}: {e}")

@client.hybrid_command(name='remove_sticky')
@commands.has_permissions(manage_messages=True)
async def remove_sticky(ctx):
    """Remove the sticky message in the current channel."""
    guild_id = str(ctx.guild.id)
    channel_id = str(ctx.channel.id)

    if guild_id in sticky_config["sticky_messages"] and channel_id in sticky_config["sticky_messages"][guild_id]:
        sticky_info = sticky_config["sticky_messages"][guild_id].pop(channel_id, None)
        save_sticky_config(sticky_config)
        if sticky_info and sticky_info.get("message_id"):
            try:
                old_message = await ctx.channel.fetch_message(sticky_info["message_id"])
                await old_message.delete()
            except discord.NotFound:
                pass
        await ctx.send("Sticky message removed!")
    else:
        await ctx.send("No sticky message set in this channel.")

@client.event
async def on_command_error(ctx, error):
    """Handle command errors."""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "You do not have the required permissions to run this command.",
            ephemeral=True
        )
    else:
        # Handle other exceptions as needed
        logging.error(f"Error occurred: {error}")

client.run(TOKEN)
