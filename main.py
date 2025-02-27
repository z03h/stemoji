import tracemalloc

import discord
import starlight
from discord import app_commands
from discord.ext import commands

from core.client import StellaEmojiBot
from core.converter import PersonalEmojiModel, FavouriteEmojiModel, SearchEmojiModel
from core.errors import UserInputError
from core.typings import EContext
from utils.general import inline_pages, describe
from utils.parsers import env, TOKEN_REGEX, FuzzyInsensitive

tracemalloc.start()
bot = StellaEmojiBot()

@bot.hybrid_command()
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.allowed_installs(guilds=True, users=True)
@describe()
async def e(ctx: EContext, emoji: PersonalEmojiModel):
    """Emoji slash shortcut to send an emoji."""
    await ctx.send(f"{emoji:u}")

@bot.hybrid_command()
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.allowed_installs(guilds=True, users=True)
@describe()
async def ef(ctx: EContext, emoji: FavouriteEmojiModel):
    """Emoji Favourite shortcut to send your favourite emoji."""
    await ctx.send(f"{emoji:u}")


@bot.hybrid_command()
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.allowed_installs(guilds=True, users=True)
@describe()
async def el(ctx: EContext, emoji: PersonalEmojiModel):
    """Get emoji link shortcut."""
    emoji.used(ctx.author)
    await ctx.send(f"{emoji.url}")


@bot.hybrid_command()
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.allowed_installs(guilds=True, users=True)
@describe()
async def ee(ctx: EContext, emoji: SearchEmojiModel):
    """Get the closest emoji shortcut."""
    if isinstance(emoji, str):
        name = emoji
        ranked = starlight.search(ctx.bot.emojis_users.values(), name=FuzzyInsensitive(name), sort=True)
        try:
            emoji = next(iter(ranked))
        except StopIteration:
            raise UserInputError(f'No emoji found with "{emoji}" as emoji.')

    await ctx.send(f"{emoji:u}")


@bot.command()
@commands.is_owner()
async def sync(ctx: EContext, guild: discord.Guild | None = None):
    """Run this command to register your slash commands on discord."""
    if guild is not None:
        bot.tree.copy_global_to(guild=guild)

    synced = await bot.tree.sync(guild=guild)
    await ctx.send(f"Synced {len(synced)} commands.")


@bot.command()
@commands.is_owner()
async def profiler(ctx: EContext):
    """Profiler for developers."""
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    async for page in inline_pages(top_stats, ctx):
        desc = "\n".join(map(str, page.item.data))
        page.embed.description = f"```\n{desc}\n```"


token = env("BOT_TOKEN")
if not token:
    raise RuntimeError("BOT_TOKEN was not filled. Did you forget to fill it in? This is required.")
elif TOKEN_REGEX.match(token) is None:
    raise RuntimeError("BOT_TOKEN has an incorrect token pattern. Is this the correct token you copied? "
                       "The format of your bot's token should be XXXXXXXXXXXXXXXXXXX.XXXXXX.XXXXXX")


bot.starter(token)
