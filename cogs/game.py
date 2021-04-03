from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from mojang import MojangAPI as Mojang
from pyosu import OsuApi

import discord
import pyosu
from custom_funcs import embed_create, is_uuid4


def sync_minecraft(ctx, account):
    try:
        if is_uuid4(account):
            uuid = account
        else:
            uuid = Mojang.get_uuid(account)

        profile = Mojang.get_profile(uuid)
        if not profile:
            return embed_create(ctx, title="Error!", description="Account not found!", color=0xeb4034)
        name_history = Mojang.get_name_history(uuid)
    except Exception:
        return embed_create(ctx, title="Error!", description="Can't lookup account! (API down?)", color=0xeb4034)

    past_names = [data['name'] for data in name_history if data['name'] != profile.name]

    embed = embed_create(ctx, title="Minecraft account info:")
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/632730054396215299/825080584451391529/grass.png")
    embed.add_field(name="Current Username:", value=discord.utils.escape_markdown(profile.name), inline=False)
    embed.add_field(name="Profile UUID:", value=profile.id, inline=False)
    embed.add_field(name="Past Usernames:",
                    value=(discord.utils.escape_markdown(", ".join(past_names)) if past_names else "No past usernames"),
                    inline=False)
    embed.add_field(name="Skin:",
                    value=f"[Download Skin ({'Steve Type' if not profile.skin_model == 'slim' else 'Alex Type'})]({profile.skin_url})" if profile.skin_url else "No skin",
                    inline=False)
    embed.add_field(name="Is legacy account?:", value="Yes" if profile.is_legacy_profile else "No", inline=False)

    # Dream's UUID
    if profile.id == 'ec70bcaf702f4bb8b48d276fa52a780c':
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/632730054396215299/827393984875855982/ForsenCD-emote.jpg")
    return embed


def mode_convert(mode):
    if not mode:
        return 0, ""
    mode = mode.lower()
    if mode in ["s", "standard", "osu", "osu!", "std", "0"]:
        return 0, ""
    elif mode in ["taiko", "t", "osu!taiko", "1"]:
        return 1, "taiko"
    elif mode in ["c", "catch", "ctb", "osu!catch", "2"]:
        return 2, "catch"
    elif mode in ["m", "mania", "osu!mania", "3"]:
        return 3, "mania"
    else:
        return 0, ""


class GameCog(commands.Cog, name="Game Info"):
    def __init__(self, bot):
        self.osu_api = OsuApi(bot.secrets["OSU_API_KEY"])
        self.bot = bot
        print("GameCog init")

    @commands.cooldown(1, 5, BucketType.user)
    @commands.command(aliases=["mc"])
    async def minecraft(self, ctx, account):
        """Gets info of minecraft accounts using current username or their UUID"""
        async with ctx.channel.typing():
            embed = await self.bot.loop.run_in_executor(None, sync_minecraft, ctx, account)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, BucketType.user)
    @commands.command(aliases=["osu!"])
    async def osu(self, ctx, account, gamemode=None):
        """Gets info of osu! accounts! You can also specify"""
        async with ctx.channel.typing():
            mode_int, mode_name = mode_convert(gamemode)
            osu_obj = await self.osu_api.get_user(user=account, mode=mode_int)
            if not isinstance(osu_obj, pyosu.models.User):
                embed = embed_create(ctx, title="Account not found!",
                                     description="If you are trying to get user info, use their username or user id.",
                                     color=0xeb4034)
            elif isinstance(osu_obj, pyosu.models.User):
                embed = embed_create(ctx, title=f"information for osu!{mode_name} account:")
                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/attachments/632730054396215299/825081328146841600/osu.png")
                embed.add_field(name="General Info:",
                                value=f"Username: {osu_obj.username}\nUser ID: {osu_obj.user_id}\nLevel: {int(osu_obj.level)}\nCountry: {osu_obj.country}",
                                inline=False)
                embed.add_field(name="Ranking Info:",
                                value=f"PP Score: {int(osu_obj.pp_raw)}\nRanked Score: {int(osu_obj.ranked_score)}\nTotal Score: {int(osu_obj.total_score)}\nPP Rank: {osu_obj.pp_rank}th\nCountry PP Rank: {osu_obj.pp_country_rank}th",
                                inline=False)
                embed.add_field(name="Play Info:",
                                value=f"Accuracy: {int(osu_obj.accuracy)}%\n{osu_obj.playcount} (good) beatmaps played!\nAmount of SSH ranks: {osu_obj.count_rank_ssh}\nAmount of SS ranks: {osu_obj.count_rank_ss}\nAmount of SH ranks: {osu_obj.count_rank_sh}\nAmount of S ranks: {osu_obj.count_rank_s}\nAmount of A ranks: {osu_obj.count_rank_a}")

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(GameCog(bot))
