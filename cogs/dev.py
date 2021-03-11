import discord, time, io, textwrap, traceback
from contextlib import redirect_stdout
from discord.ext import commands
from custom_funcs import embed_create

def cleanup_code(content):
    if content.startswith('```') and content.endswith('```'):
        return '\n'.join(content.split('\n')[1:-1])
    return content.strip('` \n')

class DevCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        print("DevCog init")

    @commands.group(invoke_without_command=False, hidden=True)
    @commands.is_owner()
    async def dev(self, ctx):
        pass

    @dev.command(name='load', hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
        try:
            self.bot.load_extension(cog)
        except Exception as e:
            embed = embed_create(ctx, title="Error!", description=f"{type(e).__name__} - {e}", color=0xeb4034)
            await ctx.send(embed=embed)
        else:
            embed = embed_create(ctx, title="Success!", description=f"Cog ``{cog}`` has been loaded!")
            await ctx.send(embed=embed)

    @dev.command(name='unload', hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            embed = embed_create(ctx, title="Error!", description=f"{type(e).__name__} - {e}", color=0xeb4034)
            await ctx.send(embed=embed)
        else:
            embed = embed_create(ctx, title="Success!", description=f"Cog ``{cog}`` has been unloaded!")
            await ctx.send(embed=embed)

    @dev.command(name='reload', hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, *, cog: str):
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            embed = embed_create(ctx, title="Error!", description=f"{type(e).__name__} - {e}", color=0xeb4034)
            await ctx.send(embed=embed)
        else:
            embed = embed_create(ctx, title="Success!", description=f"Cog ``{cog}`` has been reloaded!")
            await ctx.send(embed=embed)

    @dev.command(name='list', hidden=True)
    @commands.is_owner()
    async def list(self, ctx):
        embed = embed_create(ctx, title="Showing all loaded cogs...", description="\n".join(self.bot.cogs))
        embed.add_field(name="Number of cogs loaded:", value=len(self.bot.cogs), inline=False)
        await ctx.send(embed=embed)

    @dev.command(name='eval', hidden=True)
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
            print(code)
            code = cleanup_code(code)
            print(code)
            to_compile = f'async def func():\n{textwrap.indent(code, "  ")}'
            stdout = io.StringIO()
            try:
                exec(to_compile, env)
            except Exception as e:
                return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')
            func = env['func']
            try:
                with redirect_stdout(stdout):
                    ret = await func()
            except Exception as e:
                value = stdout.getvalue()
                await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
            else:
                value = stdout.getvalue()
                if ret is None:
                    if value:
                        embed = embed_create(ctx, title="Exec result:", description=f'```py\n{value}\n```')
                    else:
                        embed = embed_create(ctx, title="Eval code executed!")

                else:
                    self._last_result = ret
                    embed = embed_create(ctx, title="Exec result:", description=f'```py\n{value}{ret}\n```')
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(DevCog(bot))
