import discord
from discord.ext import commands

from custom_funcs import embed_create


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        help_attributes = {
            'help': "Displays help for the bot's commands... duh",
            'hidden': True,
            'aliases': ["h"]
        }
        help_obj = MyHelp(command_attrs=help_attributes, verify_checks=False)
        bot.help_command = help_obj
        print("HelpCog init")


class MyHelp(commands.HelpCommand):
    def get_command_signature(self, command):
        return '%s%s %s' % (self.clean_prefix, command.qualified_name, command.signature)

    async def send_bot_help(self, mapping):
        embed = embed_create(self.context, title="Help:",
                             description=f"``{self.clean_prefix}help [command]`` for command info")
        for cog, command in mapping.items():
            filtered = await self.filter_commands(command, sort=True)
            command_signatures = [self.get_command_signature(c) for c in filtered]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "Other")
                embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_command_help(self, command):
        embed = embed_create(self.context, title=self.get_command_signature(command))
        embed.add_field(name="Command Help:", value=command.help)
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_group_help(self, group):
        embed = embed_create(self.context, title=self.get_command_signature(group))
        embed.add_field(name="Help:", value=f"{group.short_doc}\n", inline=False)
        embed.add_field(name="Subcommand Help:", value="???", inline=False)
        for command in group.commands:
            embed.add_field(name=self.get_command_signature(command), value=command.help, inline=False)
        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_error_message(self, error):
        embed = embed_create(self.context, title="Help command error!", description=error, color=0xeb4034)
        channel = self.get_destination()
        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(HelpCog(bot))
