from discord.ext import commands

from essentials.errors import (MustBeSameChannel, NotConnectedToVoice,
                               PlayerNotConnected)


class Errorhandler(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"`{error.param.name}` is required.")

        if isinstance(error, commands.CommandNotFound):
            pass

        if isinstance(error, commands.NotOwner):
            pass

        if isinstance(error, commands.MissingPermissions):
            if len(error.missing_perms) > 1:
                sorno = "permissions"
                isare = "are"
            else:
                sorno = "permission"
                isare = "is"

            perms = ", ".join(error.missing_perms)
            await ctx.send(
                f"{perms.replace('_', ' ').replace('guild', 'server').title()} {sorno} {isare} required for you."
            )

        if isinstance(error, commands.BotMissingPermissions):
            if len(error.missing_perms) > 1:
                sorno = "permissions"
                isare = "are"
            else:
                sorno = "permission"
                isare = "is"

            perms = ", ".join(error.missing_perms)
            await ctx.send(
                f"{perms.replace('_', ' ').replace('guild', 'server').title()} {sorno} {isare} required for bot."
            )

        if isinstance(error, commands.MaxConcurrencyReached):
            await ctx.send(
                "You are trying to run the same command multiple times at the same time. Please stop. If you continue to experience this problem contact Eco#0745"
            )

        if isinstance(error, PlayerNotConnected):
            await ctx.send("Eco BOT is not connected to any voice channel.")

        if isinstance(error, MustBeSameChannel):
            await ctx.send("Please join the voice channel I am connected.")

        if isinstance(error, NotConnectedToVoice):
            await ctx.send("Oops, looks like you're not logged into any voice channels.")


def setup(bot):
    bot.add_cog(Errorhandler(bot))
