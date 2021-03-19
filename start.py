import os, sys
try:
    os.chdir(os.path.dirname(sys.argv[0]))
except:
    pass

import discord, traceback, json, time, logging
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

initial_extensions = ['cogs.discord', 'cogs.help', 'cogs.error', 'cogs.dev', 'cogs.misc', 'cogs.mod']
default_prefix = "info$"

bot = commands.Bot(case_insensitive=True, command_prefix=default_prefix, intents=intents, activity=discord.Game(name="info$help for help!"))
bot.start_time = None
bot.default_prefix = default_prefix
bot.prefixes = {}

def get_prefix(bot, message):
    if isinstance(message.channel, discord.channel.DMChannel):
        return default_prefix
    return bot.prefixes.get(message.guild.id, default_prefix)

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

@bot.event
async def on_message(message):
    if message.author.bot or message.mention_everyone:
        return
    if bot.user.mentioned_in(message):
        set_prefix = get_prefix(bot, message)
        embed = discord.Embed(title=f"Pinged!", description=f"The set prefix is `{set_prefix}`", color=0x46ff2e)
        embed.set_footer(
            text="Command sent by {}".format(message.author),
            icon_url=message.author.avatar_url,
        )
        await message.channel.send(embed=embed)
    await bot.process_commands(message)

bot.run('bu', bot=True, reconnect=True)
