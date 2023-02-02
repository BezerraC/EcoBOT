from discord.ext import commands

from .errors import MustBeSameChannel, NotConnectedToVoice, PlayerNotConnected
from .player import WebPlayer


def voice_connected():
    def predicate(ctx):
        try:
            ctx.author.voice.channel
            return True
        except AttributeError:
            raise NotConnectedToVoice("Ops, parece que você não está conectado em nenhum canal de voz.")

    return commands.check(predicate)


def player_connected():
    def predicate(ctx):
        player: WebPlayer = ctx.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if not player.is_connected:
            raise PlayerNotConnected("Eco BOT não está conectado em nenhum canal de voz.")
        return True

    return commands.check(predicate)


def in_same_channel():
    def predicate(ctx):
        player: WebPlayer = ctx.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if not player.is_connected:
            raise PlayerNotConnected("Eco BOT não está conectado em nenhum canal de voz.")

        try:
            return player.channel_id == ctx.author.voice.channel.id
        except:
            raise MustBeSameChannel(
                "Por favor entre no canal de voz em que estou conectado."
            )

    return commands.check(predicate)
