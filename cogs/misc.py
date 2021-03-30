import discord, time, whois, sys, wikipedia, json
from discord.ext import commands
from custom_funcs import embed_create, Emotes
from typing import Optional, Union
from datetime import timedelta
from discord.ext.commands.cooldowns import BucketType

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
        if not isinstance(domain, str):
            return embed_create(ctx, title="Error!", description="It seems that you confused this command with ``user``, this command is for [WHOIS](https://www.whois.net) lookup only.", color=0xeb4034)
        try:
            query = whois.query(domain)
        except whois.exceptions.FailedParsingWhoisOutput:
            return embed_create(ctx, title="Error!", description="Can't get WHOIS lookup! (Server down?)", color=0xeb4034)
        except whois.exceptions.UnknownTld:
            return embed_create(ctx, title="Error!", description="Sorry, can't get domains from that TLD!", color=0xeb4034)
        if not query:
            return embed_create(ctx, title="Error!", description="Domain not found! (This command is for website domains, not discord users)", color=0xeb4034)
        embed = embed_create(ctx, title=f"WHOIS Lookup for {domain}")
        embed.add_field(name="Name:", value=query.name, inline=False)
        embed.add_field(name="Registrar:", value=(query.registrar or "Unknown"), inline=False)
        embed.add_field(name="Name Servers:", value=(("\n".join(query.name_servers)) or "Unknown"), inline=False)
        embed.add_field(name="Expiration Date:", value=(query.expiration_date or "Unknown"), inline=False)
        embed.add_field(name="Creation Date:", value=(query.creation_date or "Unknown"), inline=False)
        return embed

class Misc(commands.Cog, name="Misc Commands"):
    def __init__(self, bot):
        self.bot = bot
        print("MiscCog init")

    def get_uptime(self):
        return round(time.time() - self.bot.start_time)

    @commands.command(aliases=["i", "ping", "source"])
    async def info(self, ctx):
        """Shows information for the bot!"""
        embed = embed_create(ctx, title="Info for InfoBot!", description="This bot gets information of certain objects!")
        embed.add_field(name="Invite this bot!", value=
    "[**Invite**](https://discord.com/api/oauth2/authorize?client_id=818281562042138635&permissions=2048&scope=bot)", inline=False)
        embed.add_field(name="Join support server!", value="[**Support Server**](https://discord.gg/Uk6fg39cWn)", inline=False)
        embed.add_field(name='Bot Creator:',
            value=\
            '[Doggie](https://github.com/DoggieLicc/InfoBot)#1641',
            inline=True)
        embed.add_field(name='Bot Uptime:',
            value=str(timedelta(seconds=self.get_uptime())), inline=False)
        embed.add_field(name='Ping:',
            value='{} ms'.format(round(1000*(self.bot.latency)), inline=False))
        await ctx.send(embed=embed)

    @commands.cooldown(1, 10, BucketType.user)
    @commands.command()
    async def whois(self, ctx, domain: Union[discord.Member, discord.User, str]):
        """Does a WHOIS lookup on a domain!"""
        async with ctx.channel.typing():
            embed = await self.bot.loop.run_in_executor(None, sync_whois, ctx, domain)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 10, BucketType.user)
    @commands.command(aliases=["wiki"])
    async def wikipedia(self, ctx, *, search):
        """Looks up Wikipedia articles by their title!"""
        async with ctx.channel.typing():
            embed = await self.bot.loop.run_in_executor(None, sync_wikipedia, ctx, search)
        await ctx.send(embed=embed)

    @commands.cooldown(10, 86_400, BucketType.user)
    @commands.command(aliases=["report"])
    async def suggest(self, ctx, *, suggestion):
        """Send a suggestion or bug report to the bot owner!"""
        owner = self.bot.get_user(203161760297910273)
        owner_embed = embed_create(ctx, title="New suggestion!:", description=suggestion)
        await owner.send(embed=owner_embed)
        user_embed = embed_create(ctx, title="👍 Suggestion has been sent to Doggie! 💖")
        await ctx.send(embed=user_embed)

def setup(bot):
    bot.add_cog(Misc(bot))
