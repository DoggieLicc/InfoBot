from contextlib import redirect_stdout
from typing import Optional, Union

from discord.ext import commands

import asqlite
import copy
import discord
import io
import textwrap
import traceback
from custom_funcs import embed_create, load_prefixes


def cleanup_code(content):
    if content.startswith('```') and content.endswith('```'):
        return '\n'.join(content.split('\n')[1:-1])
    return content.strip('` \n')


class DevCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        print("DevCog init")

    @commands.group(invoke_without_command=False, hidden=True, case_insensitive=True)
    @commands.is_owner()
    async def dev(self, ctx):
        pass

    @dev.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *cogs: str):
        for cog in cogs:
            try:
                self.bot.load_extension(f'cogs.{cog}')
            except Exception as e:
                embed = discord.Embed(title='Error!', description=f'{type(e).__name__} - {e}', color=0xeb4034)
                return await ctx.send(embed=embed)

        embed = discord.Embed(title='Success!', description=f'Cogs `{", ".join(cogs)}` has been loaded!')
        await ctx.send(embed=embed)

    @dev.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *cogs: str):
        for cog in cogs:
            try:
                self.bot.unload_extension(f'cogs.{cog}')
            except Exception as e:
                embed = discord.Embed(title='Error!', description=f'{type(e).__name__} - {e}', color=0xeb4034)
                return await ctx.send(embed=embed)

        embed = discord.Embed(title='Success!', description=f'Cogs `{", ".join(cogs)}` has been unloaded!')
        await ctx.send(embed=embed)

    @dev.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, *cogs: str):
        for cog in cogs:
            try:
                self.bot.reload_extension(f'cogs.{cog}')
            except Exception as e:
                embed = discord.Embed(title='Error!', description=f'{type(e).__name__} - {e}', color=0xeb4034)
                return await ctx.send(embed=embed)

        embed = discord.Embed(title='Success!', description=f'Cog `{", ".join(cogs)}` has been reloaded!')
        await ctx.send(embed=embed)

    @dev.command(hidden=True)
    @commands.is_owner()
    async def list(self, ctx):
        embed = embed_create(ctx, title="Showing all loaded cogs...", description="\n".join(self.bot.cogs))
        embed.add_field(name="Number of cogs loaded:", value=len(self.bot.cogs), inline=False)
        await ctx.send(embed=embed)

    @dev.command(hidden=True)
    @commands.is_owner()
    async def eval(self, ctx, *, code):
        async with ctx.channel.typing():
            env = {
                'bot': self.bot,
                'ctx': ctx,
                'channel': ctx.channel,
                'author': ctx.author,
                'guild': ctx.guild,
                'message': ctx.message,
                '_': self._last_result
            }
            env.update(globals())
            code = cleanup_code(code)
            to_compile = f'async def func():\n{textwrap.indent(code, "  ")}'
            stdout = io.StringIO()
            try:
                exec(to_compile, env)
            except Exception as e:
                embed = embed_create(ctx, title="Error!", description=f'```py\n{e.__class__.__name__}: {e}\n```',
                                     color=0xeb4034)
                return await ctx.send(embed=embed)
            func = env['func']
            try:
                with redirect_stdout(stdout):
                    ret = await func()
            except Exception as e:
                value = stdout.getvalue()
                embed = embed_create(ctx, title="Error!", description=f'```py\n{value}{traceback.format_exc()}\n```',
                                     color=0xeb4034)
                return await ctx.send(embed=embed)
            else:
                value = stdout.getvalue()
                if ret is None:
                    if value:
                        if len(value) < 2000:
                            embed = embed_create(ctx, title="Exec result:", description=f'```py\n{value}\n```')
                        else:
                            for long_val in [value[i:i + 2000] for i in range(0, len(value), 2000)]:
                                embed = embed_create(ctx, title="Exec result:", description=f'```py\n{long_val}\n```')
                                await ctx.send(embed=embed)
                            return
                    else:
                        embed = embed_create(ctx, title="Eval code executed!")
                else:
                    value = stdout.getvalue()
                    self._last_result = ret
                    if len(value) + len(ret) < 2000:
                        embed = embed_create(ctx, title="Exec resultt:", description=f'```py\n{value}{ret}\n```')
                    else:
                        for long_val in [ret[i:i + 2000] for i in range(0, len(ret), 2000)]:
                            embed = embed_create(ctx, title="Exec results:", description=f'```py\n{long_val}\n```')
                            await ctx.send(embed=embed)
                        embed = embed_create(ctx, title="Exec return value:", description=f'```py\n{ret}\n```')
                        return await ctx.send(embed=embed)
                    print(len(value) + len(ret))
                    embed = embed_create(ctx, title="Exec result:", description=f'```py\n{value}{ret}\n```')

        await ctx.send(embed=embed)

    @dev.command(hidden=True)
    @commands.is_owner()
    async def sudo(self, ctx, channel: Optional[discord.TextChannel], who: Union[discord.Member, discord.User], *,
                   command: str):
        msg = copy.copy(ctx.message)
        channel = channel or ctx.channel
        msg.channel = channel
        msg.author = who
        if isinstance(channel, discord.channel.DMChannel):
            prefix = self.bot.default_prefix
        else:
            prefix = self.bot.prefixes.get(channel.guild.id, self.bot.default_prefix)
        msg.content = prefix + command
        new_ctx = await self.bot.get_context(msg, cls=type(ctx))
        await self.bot.invoke(new_ctx)


def setup(bot):
    bot.add_cog(DevCog(bot))
