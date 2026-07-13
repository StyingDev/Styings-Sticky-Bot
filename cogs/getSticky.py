import discord
from discord import app_commands
from discord.ext import commands
import datetime

from stickyCommon import respond, DEFAULT_THRESHOLD


class GetStickyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='getsticky', description='Show all active and stopped stickies in this server.')
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.guild_only()
    async def getsticky(self, interaction: discord.Interaction):
        guild_entries = self.bot.db.for_guild(interaction.guild.id)

        if not guild_entries:
            await respond(interaction, "No sticky messages set in this server.", ephemeral=True)
            return

        def field_value(info):
            status = "Active" if info.get('active') else "Inactive"
            kind = "Embed" if info.get('is_embed') else "Text"
            preview = info['message'] if len(info['message']) <= 150 else info['message'][:147] + "..."
            updated_line = ""
            if info.get('updated_at'):
                ts = int(datetime.datetime.fromisoformat(info['updated_at']).timestamp())
                updated_by = f" by <@{info['updated_by']}>" if info.get('updated_by') else ""
                updated_line = f"Last updated: <t:{ts}:R>{updated_by}\n"
            return (f"Status: {status} | Type: {kind} | Threshold: ~{info.get('threshold', DEFAULT_THRESHOLD)} lines\n"
                    f"{updated_line}Message: {preview}")

        chunk_size = 15
        chunks = [guild_entries[i:i + chunk_size] for i in range(0, len(guild_entries), chunk_size)]

        for idx, chunk in enumerate(chunks):
            title = "Sticky Messages"
            if len(chunks) > 1:
                title += f" (page {idx + 1}/{len(chunks)})"
            embed = discord.Embed(title=title, color=discord.Color.blue())
            for info in chunk:
                channel = self.bot.get_channel(info['channel_id'])
                name = f"#{channel.name}" if channel else f"[Deleted or Inaccessible: {info['channel_id']}]"
                embed.add_field(name=name, value=field_value(info), inline=False)
            await respond(interaction, embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(GetStickyCog(bot))
