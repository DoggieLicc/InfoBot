from discord.ext import commands

import asqlite
import discord
import time
from custom_funcs import embed_create, load_prefixes


class ModCog(commands.Cog, name="Mod Commands"):
    def __init__(self, bot):
        self.bot = bot
        self.bot.prefixes = {}
        bot.command_prefix = self.get_prefix
        print("PrefixCog init")

    def get_prefix(self, bot, message):
        if isinstance(message.channel, discord.channel.DMChannel):
            return self.bot.default_prefix
        return bot.prefixes.get(message.guild.id, self.bot.default_prefix)

    @commands.Cog.listener()
    async def on_ready(self):
        await load_prefixes(self.bot)
        self.bot.start_time = self.bot.start_time or time.time()
        print(f'\n\nLogged in as: {self.bot.user.name} - {self.bot.user.id}\nVersion: {discord.__version__}\n')
        print(f'Successfully logged in and booted...!')

    @commands.command(aliases=["setprefix"])
    @commands.guild_only()
    @commands.check_any(commands.has_permissions(manage_guild=True), commands.is_owner())
    async def prefix(self, ctx, *, prefix=None):
        """Sets a custom prefix for a server! You need **Manage Server** permissions for this!"""
        if not prefix:
            set_prefix = self.get_prefix(self.bot, ctx.message)
            embed = embed_create(ctx, title=f"Prefix for {ctx.guild.name}", description=f"The prefix is `{set_prefix}`")
            await ctx.send(embed=embed)
            return
        async with asqlite.connect('data.db', check_same_thread=False) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("REPLACE INTO prefixes VALUES(?, ?)", (ctx.guild.id, prefix))
            await conn.commit()
        embed = embed_create(ctx, title="Custom prefix set!",
                             description=f"Custom prefix `{prefix}` has been set for {ctx.guild.name}!")
        await ctx.send(embed=embed)
        await load_prefixes(self.bot)


def setup(bot):
    bot.add_cog(ModCog(bot))
