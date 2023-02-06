from discord.ext.commands.errors import CheckFailure


class NotConnectedToVoice(CheckFailure):
    """User not connected to any voice channels"""

    pass


class PlayerNotConnected(CheckFailure):
    """Eco Bot not connected"""

    pass


class MustBeSameChannel(CheckFailure):
    """I think we are not on the same voice channel"""

    pass
