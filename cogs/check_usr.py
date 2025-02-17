import os
import aiosqlite
import discord
from discord.ext import commands
from utils import bot, duration, logger, time

log = logger.Logger.afkbot_logger


class CheckUSR(commands.Cog):
    """Cog for checking if a user is AFK."""

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="checkusr", description="Check if a user is AFK.")
    async def checkusr(
        self,
        ctx: discord.ApplicationContext,
        member: discord.Option(
            discord.Member,
            description="Check if a member is AFK (leave blank to check yourself).",
            required=False,
        ),
    ):
        """Check if a user is AFK and return their status."""
        member = member or ctx.user
        log.debug(f"User {ctx.user.id} requested AFK status for {member.id}.")

        db_path = os.path.join(os.path.dirname(__file__), "..", "users.sqlite")

        try:
            async with aiosqlite.connect(db_path) as db:
                query = "SELECT * FROM Afk WHERE usr = ?"
                result = await db.execute_fetchall(query, (member.id,))

            if not result:
                log.debug(f"User {member.id} is not in the AFK database.")
                embed = discord.Embed(
                    title=f"{member.name} is not AFK",
                    color=discord.Color.green(),
                )
                await ctx.respond(embed=embed, ephemeral=True)
                return

            afk_data = result[0]
            log.debug(f"User {member.id} found in the AFK database.")

            embed = discord.Embed(
                title=f"💤 {member.display_name} is AFK",
                color=discord.Color.orange(),
            )

            if afk_data[1]:
                embed.add_field(name="Status", value=afk_data[1], inline=False)
            if afk_data[2]:
                embed.add_field(name="ETA until back", value=afk_data[2], inline=False)

            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(
                text=f"Away for {await duration.time_duration(start_str=afk_data[4], end_str=time.now())}"
            )

            await ctx.respond(embed=embed, ephemeral=True)
            log.info(f"Sent AFK status of {member.id} to {ctx.user.id}.")

        except Exception as e:
            log.error(f"Error checking AFK status for {member.id}: {e}")
            embed = discord.Embed(
                title="Error",
                description="An unexpected error occurred while checking AFK status.",
                color=discord.Color.red(),
            )
            await ctx.respond(embed=embed, ephemeral=True)

    @commands.user_command(name="Check AFK Status", description="Check if a user is AFK.")
    async def checkusr_user_command(self, ctx: discord.ApplicationContext, member: discord.User):
        """User context menu command to check if someone is AFK."""
        await ctx.defer(ephemeral=True)
        await self.checkusr(ctx, member=member)


def setup(bot: commands.Bot):
    """Setup function for the CheckUSR cog."""
    log.debug("Loading CheckUSR cog.")
    bot.add_cog(CheckUSR(bot))

