import discord, time, base64, datetime
from discord.ext import commands
from custom_funcs import embed_create, get_perms
from datetime import timedelta
from typing import Optional, Union
from baseconv import base64 as num64

class DiscordInfo(commands.Cog, name="Discord Info"):
    def __init__(self, bot):
        self.bot = bot
        print("DiscordCog init")

    @commands.group(invoke_without_command=True, aliases=["guild"], case_insensitive=True)
    @commands.guild_only()
    async def server(self, ctx, subcommand=None):
        '''Lists info for the current guild'''

        server = ctx.guild
        embed = embed_create(ctx, title=f"Info for {server.name}:")
        features = []
        if "COMMUNITY" in server.features:
            features.append("Community")
        if "VERIFIED" in server.features:
            features.append("Verified")
        if "PARTNERED" in server.features:
            features.append("Partnered")
        if len(features) == 0:
            features.append("None")

        embed.set_thumbnail(url=server.icon_url)
        embed.add_field(name="Special features:", value=", ".join(features))
        embed.add_field(name="Boost Level:", value=server.premium_tier)
        embed.add_field(name="Owner:", value=server.owner)
        embed.add_field(name="Region:", value=server.region)
        embed.add_field(name="Amount of members:", value=server.member_count)
        embed.add_field(name="Amount of roles:", value=len(server.roles))
        embed.add_field(name="Amount of boosters:", value=server.premium_subscription_count)
        embed.add_field(name="Amount of text channels:", value=len(server.text_channels))
        embed.add_field(name="Amount of voice channels:", value=len(server.voice_channels))
        embed.add_field(name="Amount of emotes:", value=len(ctx.guild.emojis))
        embed.add_field(name="Server ID:", value=server.id)
        embed.add_field(name="Creation date:", value=server.created_at.strftime("%A, %d %b %Y, %I:%M:%S %p"), inline=False)
        await ctx.send(embed=embed)

    @server.command(help="Lists all of the roles that the server has")
    @commands.guild_only()
    async def list_roles(self, ctx):
        private = embed_create(ctx, title="Listing all roles:")
        for role in ctx.guild.roles:
            perms = get_perms(role.permissions)
            if len(private) >= 5000:
                try:
                    await ctx.author.send(embed=private)
                except:
                    err = embed_create(ctx, title="Error!", description="The bot can't DM you! Check your privacy settings...")
                    await ctx.send(embed=err)
                private = embed_create(ctx, title="Continuing...")
            private.add_field(name=f"@{role.name}", value=f"Top permission: {perms[0]}\n{len(role.members)} member(s) with {role.mention}\nRole ID: {role.id}\nCreated at: {role.created_at.strftime('%A, %d %b %Y, %I:%M:%S %p')}", inline=False)
        try:
            public = embed_create(ctx, title="Success!", description="List of roles have been sent to you!")
            await ctx.author.send(embed=private)
            await ctx.send(embed=public)
        except:
            err = embed_create(ctx, title="Error!", description="The bot can't DM you! Check your privacy settings...")
            await ctx.send(embed=err)

    @server.command(help="Lists all of the channels the bot can see")
    @commands.guild_only()
    async def list_channels(self, ctx):
        private = embed_create(ctx, title="Listing all channels:")
        for channel in ctx.guild.channels:
            if len(private) >= 5000:
                try:
                    await ctx.author.send(embed=private)
                except:
                    err = embed_create(ctx, title="Error!", description="The bot can't DM you! Check your privacy settings...")
                    await ctx.send(embed=err)
                private = embed_create(ctx, title="Continuing...")
            private.add_field(name=f"Channel {channel.name}", value=f"Category name: {channel.mention} in {channel.category} \nChannel type: {str(channel.type).capitalize()}\nChannel ID: {channel.id}\nCreated at: {channel.created_at.strftime('%A, %d %b %Y, %I:%M:%S %p')}", inline=False)
        try:
            public = embed_create(ctx, title="Success!", description="List of channels have been sent to you!")
            await ctx.author.send(embed=private)
            await ctx.send(embed=public)
        except:
            err = embed_create(ctx, title="Error!", description="The bot can't DM you! Check your privacy settings...")
            await ctx.send(embed=err)

    @server.command(help="Lists all of the emotes of the current server")
    @commands.guild_only()
    async def list_emotes(self, ctx):
        if len(ctx.guild.emojis) == 0:
            embed = embed_create(ctx, title="Showing all emotes:", description="There are no emojis to show!")
            await ctx.send(embed=embed)
            return
        embed = embed_create(ctx, title="Showing all emotes:")
        emoji_rendered, char_count = [], 0
        for emoji in ctx.guild.emojis:
            if emoji.is_usable:
                if char_count >= 900:
                    embed.add_field(name="᲼᲼᲼᲼᲼᲼", value="".join(emoji_rendered), inline=False)
                    emoji_rendered, char_count = [], 0
                emoji_rendered.append(str(emoji))
                char_count += len(str(emoji))

        embed.add_field(name="᲼᲼᲼᲼᲼᲼", value="".join(emoji_rendered), inline=False)
        embed.add_field(name="Number of emotes:", value=len(ctx.guild.emojis))
        await ctx.send(embed=embed)

    @commands.command(help="Shows information about the user specified, if no user specified then it returns info for invoker", aliases=["member"])
    async def user(self, ctx, *, user: Optional[discord.User]):
        user = user or ctx.author
        member_obj = None
        try:
            member_obj = ctx.guild.get_member(user.id)
        except Exception:
            pass

        embed = embed_create(ctx, title=f"Info for {user}:")
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name="Is bot?", value=user.bot)
        embed.add_field(name="User ID:", value=user.id)
        embed.add_field(name="Creation date:", value=user.created_at.strftime("%A, %d %b %Y, %I:%M:%S %p"), inline=False)

        if member_obj:
            role_mentions = []
            for role in member_obj.roles:
                role_mentions.append(role.mention)
            perms = get_perms(member_obj.guild_permissions)
            embed.add_field(name="Joined at:", value=member_obj.joined_at.strftime("%A, %d %b %Y, %I:%M:%S %p"), inline=False)
            embed.add_field(name="Highest role:", value=member_obj.top_role.mention, inline=False)
            embed.add_field(name="Roles:", value="\n".join(role_mentions))
            embed.add_field(name="Mod permissions:", value=",\n".join(perms))

        await ctx.send(embed=embed)

    @commands.command(help="Shows user's avatar", aliases=["pfp"])
    async def avatar(self, ctx, *, user: Optional[discord.User]):
        user = user or ctx.author
        embed = embed_create(ctx, title=f"Avatar of {user}:")
        embed.set_image(url=user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(help="Shows info for an invite using a invite URL", aliases=["inv"])
    async def invite(self, ctx, invite: discord.Invite):
        embed = embed_create(ctx, title="Invite Info:")
        embed.set_thumbnail(url=invite.guild.icon_url)
        embed.add_field(name="Invite channel:", value=f"Name: #{invite.channel.name}\nID: {invite.channel.id}", inline=True)
        embed.add_field(name="Active members: Total members", value=f"{invite.approximate_presence_count} active member(s): {invite.approximate_member_count} total member(s)", inline=False)
        embed.add_field(name="Invite creator:", value=invite.inviter, inline=False)
        embed.add_field(name="Invite ID:", value=invite.id, inline=False)
        embed.add_field(name="Server name:", value=invite.guild, inline=False)
        embed.add_field(name="Server ID:", value=invite.guild.id, inline=False)
        embed.add_field(name="Server created at:", value=invite.guild.created_at.strftime("%A, %d %b %Y, %I:%M:%S %p"), inline=False)
        await ctx.send(embed=embed)

    @commands.command(help="Shows info for the channel specified using channel mention or ID", aliases=["chann"])
    @commands.guild_only()
    async def channel(self, ctx, channel: Union[discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel]):

        embed = embed_create(ctx, title=f"Info of ``{channel.name}``")
        embed.set_thumbnail(url=ctx.guild.icon_url)

        if isinstance(channel, discord.TextChannel):
            slowmode = "Disabled" if channel.slowmode_delay == 0 else f"{channel.slowmode_delay} seconds"
            embed.add_field(name="Slowmode:", value=slowmode, inline=False)
            embed.add_field(name="NSFW?:", value=channel.is_nsfw(), inline=False)

        if isinstance(channel, discord.VoiceChannel):
            user_limit = "Disabled" if channel.user_limit == 0 else f"{channel.user_limit} max"
            embed.add_field(name="Bitrate:", value=f"{round(channel.bitrate/1000)}kbps")
            embed.add_field(name="User limit", value=user_limit)

        embed.add_field(name="Channel type:", value=f"{str(channel.type).capitalize()} channel", inline=False)
        embed.add_field(name="Channel category", value=channel.category)
        embed.add_field(name="Channel ID", value=channel.id, inline=False)
        embed.add_field(name="Creation date:", value=channel.created_at.strftime("%A, %d %b %Y, %I:%M:%S %p"), inline=False)
        await ctx.send(embed=embed)

    @commands.command(help="Shows info for the role specified using role mention or ID")
    @commands.guild_only()
    async def role(self, ctx, *, role: discord.Role):
        embed = embed_create(ctx, title=f"Info for @{role.name}:")

        hex_color = "#{:02x}{:02x}{:02x}".format(role.color.r, role.color.g, role.color.b)
        perms = get_perms(role.permissions)

        if role.is_bot_managed():
            bot = await self.bot.fetch_user(role.tags.bot_id)
            embed.add_field(name="Bot manager name:", value=bot, inline=False)
            embed.add_field(name="Bot manager ID:", value=role.tags.bot_id, inline=False)
        elif role.is_premium_subscriber():
            embed.add_field(name="Amount of boosters with role:", value=f"{len(role.members)} member(s)", inline=False)
        elif role.is_integration():
            embed.add_field(name="Integration ID:", value=role.tags.integration_id, inline=False)
        else:
            embed.add_field(name="Amount of members with role:", value=f"{len(role.members)} member(s)", inline=False)

        embed.add_field(name="Role name:", value=role.mention)
        embed.add_field(name="Role position:", value=role.position)
        embed.add_field(name="Role ID:", value=role.id, inline=False)
        embed.add_field(name="Role color:", value=hex_color, inline=False)
        embed.add_field(name="Mentionable?:", value=role.mentionable, inline=False)
        embed.add_field(name="Appears in member list?:", value=role.hoist, inline=False)
        embed.add_field(name="Mod permissions:", value="\n".join(perms), inline=False)
        embed.add_field(name="Created at:", value=role.created_at.strftime("%A, %d %b %Y, %I:%M:%S %p"), inline=False)
        await ctx.send(embed=embed)

    @commands.command(help="Shows info of emote using the emote ID", aliases=["emoji"])
    @commands.guild_only()
    async def emote(self, ctx, emoji: discord.Emoji):
        embed = embed_create(ctx, title="Info for custom emote:")
        embed.set_thumbnail(url=emoji.url)
        embed.add_field(name="Emote name:", value=emoji.name, inline=False)
        embed.add_field(name="Emote ID:", value=emoji.id, inline=False)
        embed.add_field(name="Animated?:", value=emoji.animated)
        embed.add_field(name="Available?:", value=emoji.available)
        embed.add_field(name="Created at:", value=emoji.created_at.strftime("%A, %d %b %Y, %I:%M:%S %p"), inline=False)
        await ctx.send(embed=embed)

    @commands.command(help="Shows info of an account/bot token! (Don't use valid tokens in public servers!)")
    async def token(self, ctx, token):
        token = token.split(".", 2)
        if len(token) != 3:
            embed = embed_create(ctx, title="Error!", description="Invalid token!", color=0xeb4034)
            return await ctx.send(embed=embed)
        try:
            user = await self.bot.fetch_user(int(base64.b64decode(token[0])))
        except discord.NotFound:
            embed = embed_create(ctx, title="Error!", description="Invalid token!", color=0xeb4034)
            return await ctx.send(embed=embed)
        try:
            bytes_int = base64.urlsafe_b64decode(token[1] + "==")
            bytes_decoded = int.from_bytes(bytes_int, "big")
        except Exception:
            embed = embed_create(ctx, title="Error!", description="Invalid token!", color=0xeb4034)
            return await ctx.send(embed=embed)
        time = datetime.datetime.utcfromtimestamp(bytes_decoded)
        if time.year < 2015:
            time = datetime.datetime.utcfromtimestamp(bytes_decoded + 1293840000)

        embed = embed_create(ctx, title=f"Info for {user.name}'s token!")
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name="Token:", value=f"{token[0]}.{token[1]}.XXXXXXX", inline=False)
        embed.add_field(name="User:", value=str(user))
        embed.add_field(name="Is bot?", value=user.bot)
        embed.add_field(name="User ID:", value=user.id, inline=False)
        embed.add_field(name="User Creation Date:", value=user.created_at.strftime("%A, %d %b %Y, %I:%M:%S %p"), inline=False)
        embed.add_field(name="Token Creation Date:", value=time, inline=False)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(DiscordInfo(bot))
