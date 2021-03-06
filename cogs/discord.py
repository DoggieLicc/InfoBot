import base64
import datetime
from typing import Optional, Union

from discord.ext import commands

import discord
from custom_funcs import embed_create, get_perms, Emotes, user_friendly_dt


class DiscordInfo(commands.Cog, name="Discord Info"):
    def __init__(self, bot):
        self.bot = bot
        self.headers = {'Authorization': f'Bot {self.bot.secrets["BOT_TOKEN"]}'}
        print("DiscordCog init")

    @commands.group(invoke_without_command=True, aliases=["guild"], case_insensitive=True)
    @commands.guild_only()
    async def server(self, ctx, subcommand=None):
        """Lists info for the current guild"""

        server: discord.Guild = ctx.guild
        embed = embed_create(ctx, title=f"Info for {server.name}:")
        features = []
        if "COMMUNITY" in server.features:
            features.append("Community")
        if "VERIFIED" in server.features:
            features.append(f"{Emotes.verified} Verified")
        if "PARTNERED" in server.features:
            features.append(f"{Emotes.partnered} Partnered")
        if "DISCOVERABLE" in server.features:
            features.append(f"{Emotes.stage} Discoverable")
        if len(features) == 0:
            features.append("No special features")

        embed.set_thumbnail(url=server.icon_url)
        embed.add_field(name="General Info:",
                        value=f"Description: {server.description or 'No description'}\n"
                              f"Owner: {await self.bot.fetch_user(server.owner_id)} ({server.owner_id})\n"
                              f"Region: "
                              f"{str(server.region).replace('-', ' ').title()}\n"
                              f"ID: {server.id}\n"
                              f"Creation date: "
                              f"{user_friendly_dt(server.created_at)}",
                        inline=False)
        embed.add_field(name="Special features:", value=", ".join(features))
        embed.add_field(name=f"{Emotes.level4} Boost Info:",
                        value=f"Boost level: {server.premium_tier} \n"
                              f"Amount of boosters: "
                              f"{server.premium_subscription_count}\n"
                              f"Booster Role: "
                              f"{server.premium_subscriber_role.mention if server.premium_subscriber_role else 'None'}",
                        inline=False)
        embed.add_field(name="Counts:",
                        value=f"Members: {server.member_count} members\nRoles: {len(server.roles)} roles\n"
                              f"Text channels: {len(server.text_channels)} channels\nVoice Channels: "
                              f"{len(server.voice_channels)} channels\nEmotes: {len(ctx.guild.emojis)} emotes",
                        inline=False)
        embed.add_field(name="Security Info:",
                        value=f"2FA required?: {'Yes' if server.mfa_level else 'No'}\nVerification Level: "
                              f"{str(server.verification_level).replace('_', ' ').title()}\nNSFW Filter: "
                              f"{str(server.explicit_content_filter).replace('_', ' ').title()}")
        embed.set_image(url=server.banner_url)
        await ctx.send(embed=embed)

    @server.command()
    @commands.guild_only()
    async def list_roles(self, ctx):
        """Lists all of the roles that the server has"""
        private = embed_create(ctx, title="Listing all roles:")
        for role in ctx.guild.roles:
            perms = get_perms(role.permissions)
            if len(private) >= 5000:
                try:
                    await ctx.author.send(embed=private)
                except discord.Forbidden:
                    err = embed_create(ctx, title="Error!",
                                       description="The bot can't DM you! Check your privacy settings...")
                    return await ctx.send(embed=err)
                private = embed_create(ctx, title="Continuing...")
            private.add_field(name=f"@{role.name}",
                              value=f"Top permission: {perms[0]}\n{len(role.members)} member(s) with {role.mention}"
                                    f"\nRole ID: {role.id}\nCreated at:"
                                    f"{user_friendly_dt(role.created_at)}",
                              inline=False)
        try:
            public = embed_create(ctx, title="Success!", description="List of roles have been sent to you!")
            await ctx.author.send(embed=private)
            await ctx.send(embed=public)
        except discord.Forbidden:
            err = embed_create(ctx, title="Error!", description="The bot can't DM you! Check your privacy settings...")
            return await ctx.send(embed=err)

    @server.command()
    @commands.guild_only()
    async def list_channels(self, ctx):
        """Lists all of the channels the bot can see"""
        private = embed_create(ctx, title="Listing all channels:")
        for channel in ctx.guild.channels:
            if len(private) >= 5000:
                try:
                    await ctx.author.send(embed=private)
                except discord.Forbidden:
                    err = embed_create(ctx, title="Error!",
                                       description="The bot can't DM you! Check your privacy settings...")
                    return await ctx.send(embed=err)
                private = embed_create(ctx, title="Continuing...")
            private.add_field(name=f"Channel {channel.name}",
                              value=f"Category name: {channel.mention} in {channel.category} \nChannel type: "
                                    f"{str(channel.type).capitalize()}\nChannel ID: {channel.id}\nCreated at: "
                                    f"{user_friendly_dt(channel.created_at)}",
                              inline=False)
        try:
            public = embed_create(ctx, title="Success!", description="List of channels have been sent to you!")
            await ctx.author.send(embed=private)
            await ctx.send(embed=public)
        except discord.Forbidden:
            err = embed_create(ctx, title="Error!", description="The bot can't DM you! Check your privacy settings...")
            return await ctx.send(embed=err)

    @server.command()
    @commands.guild_only()
    async def list_emotes(self, ctx):
        """Lists all of the emotes of the current server"""
        if len(ctx.guild.emojis) == 0:
            embed = embed_create(ctx, title="Showing all emotes:", description="There are no emojis to show!")
            await ctx.send(embed=embed)
            return
        embed = embed_create(ctx, title="Showing all emotes:")
        emoji_rendered, char_count = [], 0
        for emoji in ctx.guild.emojis:
            if emoji.is_usable:
                if char_count >= 900:
                    embed.add_field(name="??????????????????", value="".join(emoji_rendered), inline=False)
                    emoji_rendered, char_count = [], 0
                    if len(embed) > 5000:
                        await ctx.send(embed=embed)
                        embed = embed_create(ctx, title="Showing all emotes:")
                emoji_rendered.append(str(emoji))
                char_count += len(str(emoji))

        embed.add_field(name="??????????????????", value="".join(emoji_rendered), inline=False)
        embed.add_field(name="Number of emotes:", value=len(ctx.guild.emojis))
        await ctx.send(embed=embed)

    @commands.command(aliases=["member"])
    async def user(self, ctx, *, user: Optional[Union[discord.Member, discord.User, str]]):
        """Shows information about the user specified, if no user specified then it returns info for invoker"""
        user: Union[discord.Member, discord.User, str] = user or ctx.author

        if isinstance(user, str):
            embed = embed_create(ctx,
                                 title='User not found!',
                                 description='No user was found with that input! (The user ID is the best way!)',
                                 color=discord.Color.red()
                                 )
            return await ctx.send(embed=embed)

        flags = [name.replace('_', ' ').title() for name, value in dict.fromkeys(iter(user.public_flags)) if value]

        embed = embed_create(ctx, title=f"Info for {user}{await Emotes.badges(user, self.bot)}:")
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name=f"Is bot? {Emotes.botTag}", value=(
            f"Yes\n[Invite This Bot](https://discord.com/oauth2/authorize?client_id={user.id}&permissions=0&scope=bot)"
            if user.bot else "No"))
        embed.add_field(name="User ID:", value=user.id)
        embed.add_field(name="Creation Date:", value=user_friendly_dt(user.created_at),
                        inline=False)
        embed.add_field(name="Badges:", value="\n".join(flags) or "None")

        if isinstance(user, discord.Member) and user.guild == ctx.guild:
            role_mentions = [role.mention for role in reversed(user.roles)]
            perms = get_perms(user.guild_permissions)
            embed.add_field(name="Server Nickname:", value=user.nick or "No nickname")
            embed.add_field(name="Joined Server At:", value=user_friendly_dt(user.joined_at),
                            inline=False)
            embed.add_field(name="Highest Role:", value=user.top_role.mention, inline=False)
            embed.add_field(name="Roles:", value="\n".join(role_mentions))
            embed.add_field(name=f"Mod permissions: {Emotes.stafftools}", value="\n".join(perms))

        await ctx.send(embed=embed)

    @commands.command(aliases=["pfp"])
    async def avatar(self, ctx, *, user: Optional[discord.User]):
        """Shows user's avatar using their ID or name"""
        user = user or ctx.author
        embed = embed_create(ctx, title=f"Avatar of {user}:")
        embed.set_image(url=user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["inv"])
    async def invite(self, ctx, invite: discord.Invite):
        """Shows info for an invite using a invite URL or its code"""
        embed = embed_create(ctx, title=f"Invite Info: {Emotes.invite}")
        embed.set_thumbnail(url=invite.guild.icon_url)
        embed.add_field(name="Invite channel:",
                        value=f"Name: #{invite.channel.name} {Emotes.channel(invite.channel)}\nID: {invite.channel.id}",
                        inline=True)
        embed.add_field(name="Active members: Total members",
                        value=f"{invite.approximate_presence_count} active member(s): {invite.approximate_member_count}"
                              f" total member(s)",
                        inline=False)
        embed.add_field(name="Invite creator:",
                        value=f"{invite.inviter}\nID: {invite.inviter.id}" if invite.inviter else "Unknown",
                        inline=False)
        embed.add_field(name="Invite ID:", value=invite.id, inline=False)
        embed.add_field(name="Server name:", value=invite.guild, inline=False)
        embed.add_field(name="Server description:", value=invite.guild.description or "No description set",
                        inline=False)
        embed.add_field(name="Server ID:", value=invite.guild.id, inline=False)
        embed.add_field(name="Server created at:", value=user_friendly_dt(invite.guild.created_at),
                        inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=["chann", "chan"])
    @commands.guild_only()
    async def channel(self, ctx, *, channel: Union[
                      discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel, discord.StoreChannel,
                      discord.StageChannel]):
        """Shows info for the channel specified using channel mention or ID"""

        embed = embed_create(ctx, title=f"Info for {channel.name}: {Emotes.channel(channel)}")
        embed.set_thumbnail(url=ctx.guild.icon_url)

        if isinstance(channel, discord.TextChannel):
            slowmode = "Disabled" if channel.slowmode_delay == 0 else f"{channel.slowmode_delay} seconds"
            embed.add_field(name=f"Slowmode: {Emotes.slowmode}", value=slowmode, inline=False)
            embed.add_field(name="NSFW?:", value=("Yes" if channel.is_nsfw() else "No"), inline=False)
            embed.add_field(name="Topic:", value=(channel.topic or "No topic set"), inline=False)

        if isinstance(channel, discord.VoiceChannel):
            embed.add_field(name="Bitrate:", value=f"{round(channel.bitrate / 1000)}kbps")
            embed.add_field(name="Region:", value=str((channel.rtc_region or "Automatic")).title())
            embed.add_field(name="Connected:", value=f"{len(channel.members)} connected\
            {f'/ {channel.user_limit} max' if channel.user_limit else ''}", inline=False)

        if isinstance(channel, discord.StageChannel):
            embed.add_field(name="Connected:", value=f"{len(channel.members)} connected")
            embed.add_field(name="Region:", value=str((channel.rtc_region or "Automatic")).title())

        embed.add_field(name="Channel type:", value=f"{str(channel.type).replace('_', ' ').title()} channel",
                        inline=False)
        embed.add_field(name="Channel category:", value=channel.category)
        embed.add_field(name="Channel ID:", value=channel.id, inline=False)
        embed.add_field(name="Creation date:", value=user_friendly_dt(channel.created_at),
                        inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def role(self, ctx, *, role: discord.Role):
        """Shows info for the role specified using role mention or ID"""
        embed = embed_create(ctx, title=f"Info for @{role.name}: {Emotes.role}")
        hex_color = "#{:02x}{:02x}{:02x}".format(role.color.r, role.color.g, role.color.b)
        perms = get_perms(role.permissions)

        if role.is_bot_managed():
            bot = await self.bot.fetch_user(role.tags.bot_id)
            embed.add_field(name="Bot manager name:", value=bot, inline=False)
            embed.add_field(name="Bot manager ID:", value=role.tags.bot_id, inline=False)
        elif role.is_integration():
            embed.add_field(name="Integration ID:", value=role.tags.integration_id, inline=False)

        embed.add_field(name="Role name:", value=role.mention)
        embed.add_field(name="Role position:", value=role.position)
        embed.add_field(name="Role ID:", value=role.id, inline=False)
        embed.add_field(name="Role color:", value=hex_color, inline=False)
        embed.add_field(name=f"{Emotes.mention} Mentionable?:", value=("Yes" if role.mentionable else "No"),
                        inline=False)
        embed.add_field(name="Appears in member list?:", value=("Yes" if role.hoist else "No"), inline=False)
        embed.add_field(name=f"{Emotes.stafftools} Mod permissions:", value="\n".join(perms), inline=False)
        embed.add_field(name="Role created at:", value=user_friendly_dt(role.created_at), inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=["emoji"])
    async def emote(self, ctx, emoji: Union[discord.Emoji, discord.PartialEmoji]):
        """Shows info of emote using the emote ID"""
        if isinstance(emoji, discord.PartialEmoji):
            if emoji.is_unicode_emoji():
                return

        embed = embed_create(ctx, title=f"Info for custom emote: {Emotes.emoji}")
        embed.set_thumbnail(url=emoji.url)
        embed.add_field(name="Emote name:", value=emoji.name, inline=False)
        embed.add_field(name="Emote ID:", value=emoji.id, inline=False)
        embed.add_field(name="Animated?:", value=("Yes" if emoji.animated else "No"))
        if isinstance(emoji, discord.PartialEmoji): return await ctx.send(embed=embed)
        embed.add_field(name="Available?:", value=("Yes" if emoji.available else "No"))
        embed.add_field(name="Created at:", value=user_friendly_dt(emoji.created_at), inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def token(self, ctx, token):
        """Shows info of an account/bot token! (Don't use valid tokens in public servers!)"""
        token = token.split(".", 2)
        if len(token) != 3:
            embed = embed_create(ctx, title="Error!", description="Invalid token!", color=0xeb4034)
            return await ctx.send(embed=embed)
        try:
            user = await self.bot.fetch_user(int(base64.b64decode(token[0])))
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
        embed.add_field(name="User:", value=f"{user}{await Emotes.badges(user, self.bot)}")
        embed.add_field(name="Is bot?", value=("Yes" if user.bot else "No"))
        embed.add_field(name="User ID:", value=user.id, inline=False)
        embed.add_field(name="User Creation Date:", value=user_friendly_dt(user.created_at),
                        inline=False)
        embed.add_field(name="Token Creation Date:", value=time, inline=False)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(DiscordInfo(bot))
