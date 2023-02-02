from discord.ext.commands.errors import CheckFailure


class NotConnectedToVoice(CheckFailure):
    """Usuário não conectado a nenhum canal de voz"""

    pass


class PlayerNotConnected(CheckFailure):
    """EcoDj não conectou"""

    pass


class MustBeSameChannel(CheckFailure):
    """Creio que não estamos no mesmo canal de voz"""

    pass
