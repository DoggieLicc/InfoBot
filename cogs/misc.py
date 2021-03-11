import discord, time, whois, sys, wikipedia
from discord.ext import commands
from custom_funcs import embed_create, get_perms
from typing import Optional
from datetime import timedelta

def sync_wikipedia(ctx, search):
        try:
            page = wikipedia.page(search)
            summary = (page.summary[:1900] + '...') if len(page.summary) > 1900 else page.summary
            embed = embed_create(ctx, title=f"Wikipedia result for {search}", description=f"[**{page.title}**]({page.url})\n\n{summary}")
            embed.set_thumbnail(url=page.images[0])
            return embed
        except wikipedia.exceptions.DisambiguationError as e:
            return embed_create(ctx, title=f"Wikipedia results for {search}", description="\n".join(e.options))
        except wikipedia.exceptions.PageError:
            results = wikipedia.search(search)
            return embed_create(ctx, title=f"**No wikipedia page found for {search}! Did you mean...**", description="\n".join(results), color=0xeb4034)

def sync_whois(ctx, domain):
        try:
            query = whois.query(domain)
        except whois.exceptions.FailedParsingWhoisOutput:
            return embed_create(ctx, title="Error!", description="Can't get WHOIS lookup! (Server down?)", color=0xeb4034)
        if not query:
            return embed_create(ctx, title="Error!", description="Domain not found!", color=0xeb4034)
        embed = embed_create(ctx, title=f"WHOIS Lookup for {domain}")
        embed.add_field(name="Name:", value=query.name, inline=False)
        embed.add_field(name="Registrar:", value=query.registrar, inline=False)
        embed.add_field(name="Name Servers:", value="\n".join(query.name_servers), inline=False)
        embed.add_field(name="Expiration Date:", value=query.expiration_date, inline=False)
        embed.add_field(name="Creation Date:", value=query.creation_date, inline=False)
        return embed

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("MiscCog init")

    def get_uptime(self):
        return round(time.time() - self.bot.start_time)

    @commands.command(help="Shows information for the bot!", aliases=["i"])
    async def info(self, ctx):
        embed = embed_create(ctx, title="Info for InfoBot!", description="This bot gets information of certain objects!")
        embed.add_field(name="Invite this bot!", value=
    "[**Invite**](https://discord.com/api/oauth2/authorize?client_id=818281562042138635&permissions=2048&scope=bot)", inline=False)
        embed.add_field(name="Join support server!", value="[**Support Server**](https://discord.gg/Uk6fg39cWn)", inline=False)
        embed.add_field(name='Bot Creator:',
            value=\
            '[DoggieLicc](https://github.com/DoggieLicc/InfoBot)#1641',
            inline=True)
        embed.add_field(name='Bot Uptime:',
            value=str(timedelta(seconds=self.get_uptime())), inline=False)
        embed.add_field(name='Ping:',
            value='{} ms'.format(round(1000*(self.bot.latency)), inline=False))
        await ctx.send(embed=embed)

    @commands.command(help="Does a WHOIS lookup on a domain!")
    async def whois(self, ctx, domain):
        async with ctx.channel.typing():
            embed = await self.bot.loop.run_in_executor(None, sync_whois, ctx, domain)
        await ctx.send(embed=embed)

    @commands.command(help="Looks up Wikipedia pages!", aliases=["wiki"])
    async def wikipedia(self, ctx, *, search):
        async with ctx.channel.typing():
            embed = await self.bot.loop.run_in_executor(None, sync_wikipedia, ctx, search)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Misc(bot))
