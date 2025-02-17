import os
import aiosqlite
import discord
from discord.commands import Option
from discord.ext import commands
from utils import logger, time, duration, bot

log = logger.Logger.afkbot_logger


class DeAfk(commands.Cog):
    """Cog for removing AFK status."""

    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="de-afk", description="Remove your AFK status.")
    async def deafk(
        self,
        ctx: discord.ApplicationContext,
        quiet: Option(
            str,
            description="Do you want the bot to not announce your return?",
            required=True,
            choices=["Off", "On"],
        ),
    ):
        """Removes AFK status from a user."""
        log.debug(f"Received de-afk command from {ctx.user.id}, quiet mode: {quiet}")

        db_path = os.path.join(os.path.dirname(__file__), "..", "users.sqlite")

        try:
            async with aiosqlite.connect(db_path) as db:
                query = "SELECT * FROM Afk WHERE usr = ?"
                result = await db.execute_fetchall(query, (ctx.user.id,))

                if not result:
                    log.debug(f"User {ctx.user.id} is not in the AFK database.")
                    embed = discord.Embed(
                        title="Error: You are not AFK.",
                        color=discord.Color.red(),
                    )
                    await ctx.respond(embed=embed, ephemeral=True)
                    return

                log.debug(f"User {ctx.user.id} found in AFK database, proceeding with removal.")

                await db.execute("DELETE FROM Afk WHERE usr = ?", (ctx.user.id,))
                await db.commit()

        except Exception as e:
            log.error(f"Error removing AFK status for {ctx.user.id}: {e}")
            embed = discord.Embed(
                title="Error",
                description="An unexpected error occurred while removing your AFK status.",
                color=discord.Color.red(),
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        # Determine ephemeral response setting
        is_ephemeral = True if quiet == "On" else False
        log.debug(f"User {ctx.user.id} de-AFK successful, ephemeral={is_ephemeral}")

        # Constructing success embed
        afk_duration = await duration.time_duration(
            start_str=result[0][4], end_str=time.now()
        )

        embed = discord.Embed(
            title=f"Welcome back, {ctx.user.display_name}!",
            color=discord.Color.green(),
        )
        embed.add_field(name="You have been away for", value=afk_duration, inline=False)
        embed.set_thumbnail(url=ctx.user.display_avatar.url)
        embed.set_footer(text=f"Current UTC time: {time.now()}")

        await ctx.respond(embed=embed, ephemeral=is_ephemeral)
        log.info(f"User {ctx.user.id} is now marked as not AFK.")


def setup(bot: commands.Bot):
    """Setup function for the DeAfk cog."""
    log.debug("Loading DeAfk cog.")
    bot.add_cog(DeAfk(bot))
