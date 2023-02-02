from discord.ext import commands

from essentials.errors import (MustBeSameChannel, NotConnectedToVoice,
                               PlayerNotConnected)


class Errorhandler(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"`{error.param.name}` é de preenchimento obrigatório.")

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
                "Você está tentando executar o mesmo comando várias vezes ao mesmo tempo. Por favor pare. Se você continuar recebendo este problema entre em contado com o Eco#0745"
            )

        if isinstance(error, PlayerNotConnected):
            await ctx.send("Eco BOT não está conectado em nenhum canal de voz.")

        if isinstance(error, MustBeSameChannel):
            await ctx.send("Por favor entre no canal de voz em que estou conectado.")

        if isinstance(error, NotConnectedToVoice):
            await ctx.send("Ops, parece que você não está conectado em nenhum canal de voz.")


def setup(bot):
    bot.add_cog(Errorhandler(bot))
