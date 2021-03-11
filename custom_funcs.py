import discord, time
from discord.ext import commands

def embed_create(ctx, title=discord.Embed.Empty, description=discord.Embed.Empty, color=0x46ff2e):
    embed = discord.Embed(description=description, title=title, color=color)
    embed.set_footer(
        text="Command sent by {}".format(ctx.author),
        icon_url=ctx.author.avatar_url,
    )
    return embed

def get_perms(permissions):
        perms = []
        if permissions.administrator:
            perms.append("Administrator")
        if permissions.manage_guild:
            perms.append("Manage guild")
        if permissions.ban_members:
            perms.append("Ban members")
        if permissions.kick_members:
            perms.append("Kick members")
        if permissions.manage_channels:
            perms.append("Manage channels")
        if permissions.manage_emojis:
            perms.append("Manage custom emotes")
        if permissions.manage_messages:
            perms.append("Manage messages")
        if permissions.manage_permissions:
            perms.append("Manage permissions")
        if permissions.manage_roles:
            perms.append("Manage roles")
        if permissions.mention_everyone:
            perms.append("Mention everyone")
        if permissions.manage_emojis:
            perms.append("Manage emojis")
        if permissions.manage_webhooks:
            perms.append("Manage webhooks")
        if permissions.move_members:
            perms.append("Move members")
        if permissions.mute_members:
            perms.append("Mute members")
        if permissions.deafen_members:
            perms.append("Deafen members")
        if permissions.priority_speaker:
            perms.append("Priority speaker")
        if permissions.view_audit_log:
            perms.append("See audit log")
        if permissions.create_instant_invite:
            perms.append("Create instant invites")
        if len(perms) == 0:
            perms.append("No moderator permissions")
        return perms
