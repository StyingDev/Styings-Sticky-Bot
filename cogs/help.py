import discord
from discord import app_commands
from discord.ext import commands

from stickyCommon import respond


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='help', description='Show available Sticky Bot commands.')
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Sticky Bot Help", description="Here are the available commands for the Sticky Bot:", color=discord.Color(0x747c8b))

        embed.add_field(name="/help", value="Shows this message.", inline=False)
        embed.add_field(name="/setsticky <message>", value="Set a sticky message in the current channel.", inline=False)
        embed.add_field(name="/setstickyembed <message> [color] [title] [image]", value="Set a sticky message with an embed. Optional hex color, title, and image URL.", inline=False)
        embed.add_field(name="/stickyedit <message>", value="Edit the text of the existing sticky (keeps its embed/color/threshold settings).", inline=False)
        embed.add_field(name="/removesticky [channel]", value="Remove the sticky message in the current or specified channel.", inline=False)
        embed.add_field(name="/getsticky", value="Show all active and stopped stickies in your server.", inline=False)
        embed.add_field(name="/stickydisable [channel]", value="Disable a sticky message without removing it.", inline=False)
        embed.add_field(name="/stickyenable [channel]", value="Re-enable a disabled sticky message.", inline=False)
        embed.add_field(name="/setstickythreshold <lines>", value="Set how many lines of chat activity happen before the sticky reposts (default 20).", inline=False)

        embed.set_footer(text="Commands require 'Manage Messages' permission.")

        await respond(interaction, embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))
