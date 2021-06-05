import os
import sys

try:
    os.chdir(os.path.dirname(sys.argv[0]))
except OSError:
    pass

import discord
import json
from discord.ext import commands
from custom_funcs import Emotes

intents = discord.Intents.default()
intents.messages = True

initial_extensions = ['cogs.discord', 'cogs.help', 'cogs.error', 'cogs.dev', 'cogs.misc', 'cogs.mod', 'cogs.game']
default_prefix = "info$"


def get_prefix(_bot, message):
    if isinstance(message.channel, discord.channel.DMChannel):
        return default_prefix
    return _bot.prefixes.get(message.guild.id, default_prefix)


bot = commands.Bot(case_insensitive=True, command_prefix=default_prefix, intents=intents,
                   activity=discord.Game('info$help for help!'), status=discord.Status.dnd, strip_after_prefix=True,
                   max_messages=50)
bot.start_time = None
bot.default_prefix = default_prefix
bot.prefixes = {}

with open("config.json") as config:
    bot.secrets = json.load(config)


@bot.event
async def on_message(message):
    if message.author.bot or (message.guild and not message.channel.permissions_for(message.guild.me).send_messages):
        return
    if message.content == f"<@!{bot.user.id}>" or message.content == f"<@{bot.user.id}>":
        set_prefix = get_prefix(bot, message)
        embed = discord.Embed(title=f"Pinged!", description=f"The set prefix is `{set_prefix}`", color=0x46ff2e)
        embed.set_footer(
            text="Command sent by {}".format(message.author),
            icon_url=message.author.avatar_url,
        )
        await message.channel.send(embed=embed)

    if (await bot.get_context(message)).valid and message.guild:
        if not message.channel.permissions_for(message.guild.me).embed_links:
            return await message.channel.send(f"{Emotes.xmark} This bot needs the ``Embed Links`` "
                                              f"permission to function!")
    await bot.process_commands(message)

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)
    bot.run(bot.secrets["BOT_TOKEN"], bot=True, reconnect=True)



