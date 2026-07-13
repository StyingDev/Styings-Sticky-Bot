import discord

from database import DEFAULT_THRESHOLD


def estimate_weight(content: str, wrap_width: int = 55) -> float:
    """Rough estimate of how many visual chat lines a message takes up
    (explicit line breaks + estimated text wrapping), used as a proxy for
    'the sticky has scrolled off screen' since we can't see anyone's actual client viewport."""
    if not content:
        return 1
    total = 0
    for line in content.split('\n'):
        total += max(1, -(-len(line) // wrap_width))
    return total


async def respond(interaction: discord.Interaction, content: str = None, *, embed: discord.Embed = None, ephemeral: bool = False):
    if interaction.response.is_done():
        await interaction.followup.send(content=content, embed=embed, ephemeral=ephemeral)
    else:
        await interaction.response.send_message(content=content, embed=embed, ephemeral=ephemeral)


async def post_sticky_message(bot, channel):
    """Delete the old sticky message (if any) and post a fresh one."""
    info = bot.db.get(channel.id)
    if not info or not info.get('active'):
        return

    if info.get('message_id'):
        try:
            old_message = await channel.fetch_message(info['message_id'])
            await old_message.delete()
        except discord.NotFound:
            pass

    if info.get('is_embed'):
        color_hex = info.get('embed_color') or '747c8b'
        embed = discord.Embed(description=info['message'], color=discord.Color(int(color_hex, 16)))
        embed.title = info.get('embed_title') or "Sticky Message"
        if info.get('embed_image'):
            embed.set_image(url=info['embed_image'])
        msg = await channel.send(embed=embed)
    else:
        msg = await channel.send(info['message'])

    await bot.db.set_message_id(channel.id, msg.id)
