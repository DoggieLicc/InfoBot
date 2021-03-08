import discord
import discord.ext.commands as err
from custom_funcs import embed_create

class ErrorCog(err.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("ErrorCog init")

    @err.Cog.listener()
    async def on_command_error(self, ctx, error):
        embed = embed_create(ctx, title="Error!", color=0xeb4034)
        print(f"Error: {error}")
        if isinstance(error, err.errors.CommandNotFound):
            return
        if isinstance(error, err.MissingRequiredArgument):
            embed.add_field(name="Missing Arguments:", value=error)
        if isinstance(error, err.NoPrivateMessage):
            embed.add_field(name="No DMs!:", value=error)
        if isinstance(error, err.errors.EmojiNotFound):
            embed.add_field(name="Emote not found!", value=error)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ErrorCog(bot))
