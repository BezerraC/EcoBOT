from discord.ext import commands

from .errors import MustBeSameChannel, NotConnectedToVoice, PlayerNotConnected
from .player import WebPlayer


def voice_connected():
    def predicate(ctx):
        try:
            ctx.author.voice.channel
            return True
        except AttributeError:
            raise NotConnectedToVoice("Oops, looks like you're not logged into any voice channels.")

    return commands.check(predicate)


def player_connected():
    def predicate(ctx):
        player: WebPlayer = ctx.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if not player.is_connected:
            raise PlayerNotConnected("Eco BOT is not connected to any voice channel.")
        return True

    return commands.check(predicate)


def in_same_channel():
    def predicate(ctx):
        player: WebPlayer = ctx.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if not player.is_connected:
            raise PlayerNotConnected("Eco BOT is not connected to any voice channel.")

        try:
            return player.channel_id == ctx.author.voice.channel.id
        except:
            raise MustBeSameChannel(
                "Please join the voice channel I am connected to."
            )

    return commands.check(predicate)
