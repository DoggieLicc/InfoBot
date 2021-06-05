from datetime import timedelta
from typing import Union

from discord import User, Member, Color, Role
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

import discord
import time
import whois
import wikipedia
import inspect

from io import BytesIO, StringIO
from PIL import Image
from custom_funcs import embed_create


def solid_color_image(color: tuple):
    buffer = BytesIO()
    image = Image.new('RGB', (80, 80), color)
    image.save(buffer, 'png')
    buffer.seek(0)

    return buffer


def sync_wikipedia(ctx, search):
    try:
        page = wikipedia.page(search)
        summary = (page.summary[:1900] + '...') if len(page.summary) > 1900 else page.summary
        embed = embed_create(ctx, title=f"Wikipedia result for {search}",
                             description=f"[**{page.title}**]({page.url})\n\n{summary}")
        embed.set_thumbnail(url=page.images[0])
        return embed
    except wikipedia.exceptions.DisambiguationError as e:
        return embed_create(ctx, title=f"Wikipedia results for {search}", description="\n".join(e.options))
    except wikipedia.exceptions.PageError:
        results = wikipedia.search(search)
        return embed_create(ctx, title=f"**No wikipedia page found for {search}! Did you mean...**",
                            description="\n".join(results), color=0xeb4034)


def sync_whois(ctx, domain):
    if not isinstance(domain, str):
        return embed_create(ctx, title="Error!",
                            description="It seems that you confused this command with ``user``, "
                                        "this command is for [WHOIS](https://www.whois.net) lookup only.",
                            color=0xeb4034)
    try:
        query = whois.query(domain)
    except whois.exceptions.FailedParsingWhoisOutput:
        return embed_create(ctx, title="Error!", description="Can't get WHOIS lookup! (Server down?)", color=0xeb4034)
    except whois.exceptions.UnknownTld:
        return embed_create(ctx, title="Error!", description="Sorry, can't get domains from that TLD!", color=0xeb4034)
    if not query:
        return embed_create(ctx, title="Error!",
                            description="Domain not found! (This command is for website domains, not discord users)",
                            color=0xeb4034)
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

    @commands.command(aliases=["i", "ping"])
    async def info(self, ctx):
        """Shows information for the bot!"""
        embed = embed_create(ctx, title="Info for InfoBot!",
                             description="This bot gets information of certain objects!")
        embed.add_field(name="Invite this bot!", value=
        "[**Invite**](https://discord.com/api/oauth2/authorize?client_id=818281562042138635&permissions=2048&scope=bot)",
                        inline=False)
        embed.add_field(name="Join support server!", value="[**Support Server**](https://discord.gg/Uk6fg39cWn)",
                        inline=False)
        embed.add_field(name='Bot Creator:',
                        value='[Doggie](https://github.com/DoggieLicc/InfoBot)#1641',
                        inline=True)
        embed.add_field(name='Bot Uptime:',
                        value=str(timedelta(seconds=self.get_uptime())), inline=False)
        embed.add_field(name='Ping:',
                        value='{} ms'.format(round(1000 * self.bot.latency), inline=False))
        await ctx.send(embed=embed)

    @commands.command(aliases=['colour'])
    async def color(self, ctx, *, color: Union[Color, Member, Role]):
        """Gets info for a color! You can specify a member, role, or color.
        Use the formats: `0x<hex>`, `#<hex>`, `0x#<hex>`, or `rgb(<num>, <num>, <num>)`"""
        alias = ctx.invoked_with.lower()

        color = color if isinstance(color, Color) else color.color

        buffer = await self.bot.loop.run_in_executor(None, solid_color_image, color.to_rgb())
        file = discord.File(filename="color.png", fp=buffer)

        embed = embed_create(ctx, title=f'Info for {alias}:', color=color)
        embed.add_field(name='Hex:', value=f'`{color}`')
        embed.add_field(name='Int:', value=f'`{str(color.value).zfill(8)}`')
        embed.add_field(name='RGB:', value=f'`{color.to_rgb()}`')
        embed.set_thumbnail(url="attachment://color.png")

        await ctx.send(file=file, embed=embed)

    @commands.cooldown(1, 10, BucketType.user)
    @commands.command()
    async def whois(self, ctx, domain: Union[Member, User, str]):
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

    @commands.cooldown(3, 86_400, BucketType.user)
    @commands.command(aliases=["report"])
    async def suggest(self, ctx, *, suggestion):
        """Send a suggestion or bug report to the bot owner!"""
        owner = self.bot.get_user(203161760297910273)
        owner_embed = embed_create(ctx, title="New suggestion!:", description=suggestion)
        await owner.send(embed=owner_embed)
        user_embed = embed_create(ctx, title="👍 Suggestion has been sent to Doggie! 💖")
        await ctx.send(embed=user_embed)

    @commands.command()
    async def source(self, ctx, *, command: str = None):
        """Look at this shit code lol (usage: source <command>)"""
        if command is None:
            embed = embed_create(ctx, title='Source Code:',
                                 description='[Github for **InfoBot**](https://github.com/DoggieLicc/InfoBot)')
            return await ctx.send(embed=embed)

        if command == 'help':
            src = type(self.bot.help_command)
            filename = inspect.getsourcefile(src)
        else:
            obj = self.bot.get_command(command.replace('.', ' '))
            if obj is None:
                embed = embed_create(ctx, title='Command not found!',
                                     description='This command wasn\'t found in this bot.')
                return await ctx.send(embed=embed)

            src = obj.callback.__code__
            filename = src.co_filename

        lines, _ = inspect.getsourcelines(src)
        code = ''.join(lines)

        buffer = StringIO(code)

        file = discord.File(fp=buffer, filename=filename)

        await ctx.send(f"Here you go, {ctx.author.mention}. (You should view this on a PC)", file=file)


def setup(bot):
    bot.add_cog(Misc(bot))
