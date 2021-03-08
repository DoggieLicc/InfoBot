import discord, sys, traceback, json
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True

initial_extensions = ['cogs.disc', 'cogs.help', 'cogs.errors']
default_prefix = "info$"

def get_prefix(bot, message):
    return default_prefix

bot = commands.Bot(command_prefix=get_prefix, intents=intents, activity=discord.Game(name="Hello world!"))

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

@bot.event
async def on_ready():
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
    print(f'Successfully logged in and booted...!')

bot.run('token', bot=True, reconnect=True)
