import discord, traceback
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
            embed.add_field(name="Command not found!:", value=error)
        elif isinstance(error, err.MissingRequiredArgument):
            embed.add_field(name="Missing Arguments:", value=error)
        elif isinstance(error, err.NoPrivateMessage):
            embed.add_field(name="No DMs!:", value=error)
        elif isinstance(error, err.errors.EmojiNotFound):
            embed.add_field(name="Emote not found!:", value=error)
        elif isinstance(error, err.errors.RoleNotFound):
            embed.add_field(name="Role not found!:", value=error)
        elif isinstance(error, err.errors.BadInviteArgument):
            embed.add_field(name="Invite not found!:", value=error)
        elif isinstance(error, err.CheckAnyFailure):
            embed.add_field(name="You don't have permissions for this command!:", value="You need the `Manage Server` permission!")
        elif isinstance(error, err.errors.NotOwner):
            embed.add_field(name="You aren't the owner of this bot!:", value=error)
        else:
            owner = self.bot.get_user(203161760297910273)
            embed.add_field(name="Unhandled Error!:", value=f"{error.__class__.__name__}: {error}")
            await owner.send(embed=embed)
            return

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ErrorCog(bot))
