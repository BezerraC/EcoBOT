import unittest
from unittest.mock import AsyncMock, MagicMock, Mock

from discord import Member, Message, VoiceState

from cogs.ecoia import Ecoia
from cogs.events import MusicEvents
from cogs.invite import Invite
from cogs.meme import Meme
from cogs.music import Music
from cogs.speech import Speech
from essentials.player import WebPlayer
from main import MusicBot, initialize


class TestMusicBot(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Set up the bot for testing
        self.bot = MusicBot(command_prefix="/", intents=None)
        await initialize()
        self.music_cog = Music(self.bot)
        self.web_player = WebPlayer(self.bot)
        self.ecoia_cog = Ecoia(self.bot)
        self.invite_cog = Invite(self.bot)
        self.events_cog = MusicEvents(self.bot)
        self.speech_cog = Speech(self.bot)
        self.meme_cog = Meme(self.bot)

    async def test_on_message(self):
        # Create a mock Message object
        message = AsyncMock(spec=Message)
        message.author.bot = False  # Simulate a non-bot message

        # Call the on_message event
        await self.bot.on_message(message)

        # Assert the expected behavior based on your on_message implementation
        self.bot.db.execute.assert_called_once_with("INSERT OR IGNORE INTO guildData (guild_id, user_id, exp) VALUES (?,?,?)", (message.guild.id, message.author.id, 1))
        self.bot.db.commit.assert_called_once()
        self.bot.db.execute.reset_mock()

        self.bot.multiplier = 2.0

        await self.bot.on_message(message)

        self.bot.db.execute.assert_called_once_with("UPDATE guildData SET exp = exp + 1 WHERE guild_id = ? AND user_id = ?", (message.guild.id, message.author.id))
        self.bot.db.commit.assert_called_once()
        self.bot.db.execute.reset_mock()

        self.bot.multiplier = 1.5

        await self.bot.on_message(message)

        self.bot.db.execute.assert_not_called()
        self.bot.db.commit.assert_not_called()

    async def test_on_message_event(self):
        # Create a mock Message object for testing the on_message event
        message = AsyncMock(spec=Message)
        message.author.bot = False
        message.guild.id = 941388532734361640 
        message.author.id = 208791519136710657  
        message.content = "Test message"

        # Create a mock cursor
        mock_cursor = AsyncMock()
        mock_cursor.rowcount = 0
        self.bot.db.execute = AsyncMock(return_value=mock_cursor)
        self.bot.db.commit = AsyncMock()

        # Set multiplier and invoke on_message event
        self.bot.multiplier = 1.5
        await self.bot.on_message(message)

        # Assert the expected behavior based on your on_message implementation
        self.bot.db.execute.assert_called_once_with("INSERT OR IGNORE INTO guildData (guild_id, user_id, exp) VALUES (?,?,?)", (message.guild.id, message.author.id, 1))
        self.bot.db.commit.assert_called_once()
        self.bot.db.execute.reset_mock()

        self.bot.multiplier = 2.0
        await self.bot.on_message(message)

        self.bot.db.execute.assert_called_once_with("UPDATE guildData SET exp = exp + 1 WHERE guild_id = ? AND user_id = ?", (message.guild.id, message.author.id))
        self.bot.db.commit.assert_called_once()
        self.bot.db.execute.reset_mock()

        self.bot.multiplier = 1.5
        mock_cursor.rowcount = 1  # Simulate a user already existing in the database
        await self.bot.on_message(message)

        self.bot.db.execute.assert_not_called()
        self.bot.db.commit.assert_not_called()
       
    async def test_rank_command(self):
        # Create a mock Message object for the command
        message = AsyncMock(spec=Message)
        message.author.bot = False  # Simulate a non-bot message
        message.content = "/rank"

        # Call the command handler
        await self.bot.process_commands(message)

        message.channel.send.assert_called_once()

    async def test_leaderboard_command(self):
        # Create a mock Message object for the command
        message = AsyncMock(spec=Message)
        message.author.bot = False  # Simulate a non-bot message
        message.content = "/leaderboard"

        # Call the command handler
        await self.bot.process_commands(message)

        message.channel.send.assert_called_once()

    async def test_connect_command(self):
        # Create a mock Message object for the command
        message = AsyncMock(spec=Message)
        message.author.bot = False  # Simulate a non-bot message
        message.content = "/connect"

        # Call the connect command handler
        await self.music_cog.connect_(message)

    async def test_disconnect_command(self):
        # Create a mock Message object for the command
        message = AsyncMock(spec=Message)
        message.author.bot = False  # Simulate a non-bot message
        message.content = "/disconnect"

        # Call the disconnect command handler
        await self.music_cog.disconnect_(message)

    async def test_play_command(self):
        # Create a mock Message object for the command
        message = AsyncMock(spec=Message)
        message.author.bot = False  # Simulate a non-bot message
        message.content = "/play TestSong"

        # Call the play command handler
        await self.music_cog.play_(message, query="TestSong")

    async def test_destroy_method(self):
        # Create a mock Message object for the player's controller message
        controller_message = AsyncMock(spec=Message)
        self.web_player.controller_message = controller_message

        # Call the destroy method
        await self.web_player.destroy(force=True)

    async def test_do_next_method(self):
        # Create a mock Track object for the queue
        track = MagicMock()
        self.web_player.queue.put_nowait(track)

        # Call the do_next method
        await self.web_player.do_next()

    async def test_invoke_player_method(self):
        # Create a mock Track object for the current track
        track = MagicMock()
        self.web_player.current = track

        # Create a mock Message object for the player's controller message
        controller_message = AsyncMock(spec=Message)
        self.web_player.controller_message = controller_message

        # Call the invoke_player method
        await self.web_player.invoke_player()

    async def test_on_message_listener(self):
        # Create a mock Message object for testing the on_message listener
        message = AsyncMock(spec=Message)
        message.content = "Hello eco"
        message.author.bot = False

        # Call the on_message listener
        await self.ecoia_cog.on_message(message)
        
    async def test_invite_command(self):
        # Create a mock Message object for the invite command
        message = AsyncMock(spec=Message)

        # Call the invite command
        await self.invite_cog.invite(message)
    
    async def test_on_message_listener(self):
        # Create a mock Message object for testing the on_message listener
        message = AsyncMock(spec=Message)
        message.author.bot = False
        self.bot.wavelink.get_player.return_value = AsyncMock(spec=self.bot.wavelink.Player)

        # Call the on_message listener
        await self.events_cog.on_message(message)

    async def test_on_voice_state_update_listener(self):
        # Create mock objects for testing the on_voice_state_update listener
        member = AsyncMock(spec=Member)
        before = AsyncMock(spec=VoiceState)
        after = AsyncMock(spec=VoiceState)

        # Call the on_voice_state_update listener
        await self.events_cog.on_voice_state_update(member, before, after)

    async def test_on_player_stop_listener(self):
        # Create mock objects for testing the on_player_stop listener
        node = AsyncMock(spec=self.bot.wavelink.Node)
        payload = MagicMock()

        # Call the on_player_stop listener
        await self.events_cog.on_player_stop(node, payload)

    async def test_on_message_listener(self):
        # Create a mock Message object for testing the on_message listener
        message = AsyncMock(spec=Message)
        message.content = "Hello eco"
        message.author.bot = False
        self.bot.user = AsyncMock()

        # Call the on_message listener
        await self.speech_cog.on_message(message)

    async def test_memebr_command(self):
        # Create a mock Context object for testing the memebr command
        ctx = AsyncMock()

        # Call the memebr command
        await self.meme_cog.memebr(ctx)


    async def test_memeus_command(self):
        # Create a mock Context object for testing the memeus command
        ctx = AsyncMock()

        # Call the memeus command
        await self.meme_cog.memeus(ctx)

if __name__ == '__main__':
    unittest.main()
