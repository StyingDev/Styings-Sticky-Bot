import discord
from discord import app_commands
from discord.ext import commands

from stickyCommon import respond


class SetStickyThresholdCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='setstickythreshold', description="Set how many lines of chat activity happen before the sticky reposts.")
    @app_commands.describe(lines="Approx. lines of chat activity before reposting (1-500)")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.guild_only()
    async def setstickythreshold(self, interaction: discord.Interaction, lines: app_commands.Range[int, 1, 500]):
        if self.bot.db.get(interaction.channel.id) is None:
            await respond(interaction, "No sticky message set in this channel yet. Use `/setsticky` first.", ephemeral=True)
            return

        await self.bot.db.upsert_sticky(interaction.channel.id, interaction.guild.id, threshold=lines)
        await respond(interaction, f"Sticky repost threshold set to ~{lines} lines of chat activity.")


async def setup(bot: commands.Bot):
    await bot.add_cog(SetStickyThresholdCog(bot))
