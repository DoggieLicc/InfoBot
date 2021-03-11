import os, sys
try:
    os.chdir(os.path.dirname(sys.argv[0]))
except:
    pass

import discord, traceback, json, time
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.presences = True

initial_extensions = ['cogs.disc', 'cogs.help', 'cogs.errors', 'cogs.dev', 'cogs.misc']
default_prefix = "info$"

def get_prefix(bot, message):
    return default_prefix

bot = commands.Bot(command_prefix=get_prefix, intents=intents, activity=discord.Game(name="info$help for help!"))
bot.start_time = None

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

@bot.event
async def on_ready():
    bot.start_time = time.time() if bot.start_time == None else bot.start_time
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
    print(f'Successfully logged in and booted...!')

bot.run('token_looker noob', bot=True, reconnect=True)
