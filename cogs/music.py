import asyncio
import re
from os import replace

import aiohttp
import discord
import wavelink
from aiohttp.helpers import current_task
from discord.ext import commands

from essentials.checks import (in_same_channel, player_connected,
                               voice_connected)
from essentials.player import WebPlayer


class Music(commands.Cog):
    """Music Commands"""

    def __init__(self, bot):
        self.bot = bot
        self.URL_REG = re.compile(r"https?://(?:www\.)?.+")

    @commands.command(name="connect", aliases=["con", "c"])
    @voice_connected()
    async def connect_(self, ctx):
        """Connect the Eco BOT"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if player.is_connected:
            if not player.bound_channel:
                player.bound_channel = ctx.channel

            if player.channel_id == ctx.channel.id:
                return await ctx.send(
                    f"Echo BOT is connected to a different voice channel."
                )

            return await ctx.send(
                "Eco BOT is already connected to your voice channel."
            )

        channel = ctx.author.voice.channel
        self.bot.voice_users[ctx.author.id] = channel.id

        msg = await ctx.send(f"Connecting in **`{channel.name}`**")
        await player.connect(channel.id)
        player.bound_channel = ctx.channel
        await msg.edit(
            content=f"Logged in **`{channel.name}`** " #and bounded to {ctx.channel.mention}
        )

    @commands.command(name="stop", aliases=["st"])
    @voice_connected()
    @player_connected()
    @in_same_channel()
    async def disconnect_(self, ctx):
        """Stop all music player"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)
        await ctx.send(f"Disconnecting, see you soon...")
        await player.destroy()

    @commands.command(name="play", aliases=["p"])
    @voice_connected()
    async def play_(self, ctx, *, query):
        """Play or add music to queue"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if not player.is_connected:
            await ctx.invoke(self.connect_)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"Whoops, I'm being used on the channel {player.bound_channel.mention}", delete_after=5
            )

        msg = await ctx.send(f"Looking for `{query}` :mag_right:")
        query = query.strip("<>")
        if not self.URL_REG.match(query):
            query = f"ytsearch:{query}"

        tracks = await self.bot.wavelink.get_tracks(query)

        if not tracks:
            return await msg.edit(content="I couldn't find any results with this query.")

        if isinstance(tracks, wavelink.TrackPlaylist):
            for track in tracks.tracks:
                await player.queue.put(track)

            msg.edit(
                content=f'Adding to playlist **{tracks.data["playlistInfo"]["name"]}** with **{len(tracks.tracks)}** songs in the queue.'
            )
        else:
            await player.queue.put(tracks[0])

            await msg.edit(content=f"Adding **{str(tracks[0])}** in the queue.")

        if not player.is_playing:
            await player.do_next()

    @commands.command()
    @voice_connected()
    @player_connected()
    @in_same_channel()
    async def skip(self, ctx):
        """Skip the current song"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"Whoops, I'm being used on the channel {player.bound_channel.mention}", delete_after=5
            )

        current_loop = player.loop
        player.loop = "NONE"

        await player.stop()

        if current_loop != "CURRENT":
            player.loop = current_loop

    @commands.command()
    @voice_connected()
    @player_connected()
    @in_same_channel()
    async def pause(self, ctx):
        """Pause the music player"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"Whoops, I'm being used on the channel {player.bound_channel.mention}", delete_after=5
            )

        if player.is_playing:
            if player.is_paused:
                return await ctx.send("The music is already paused.")

            await player.set_pause(pause=True)
            return await ctx.send("Pausing the music.")

        await ctx.send("Whoops, I'm not playing anything at the moment.")

    @commands.command()
    @player_connected()
    @voice_connected()
    @in_same_channel()
    async def resume(self, ctx):
        """Play music again"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"Whoops, I'm being used on the channel {player.bound_channel.mention}", delete_after=5
            )

        if player.is_playing:
            if not player.is_paused:
                return await ctx.send("Music is not paused.")

            await player.set_pause(pause=False)
            return await ctx.send("Running music again.")

        await ctx.send("Oops, I'm not playing any music.")

    @commands.command()
    @voice_connected()
    @player_connected()
    @in_same_channel()
    async def seek(self, ctx, seconds: int, reverse: bool = False):
        """Skip the song forward or backward"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"Whoops, I'm being used on the channel {player.bound_channel.mention}", delete_after=5
            )

        if player.is_playing:
            if not player.is_paused:
                if not reverse:
                    new_position = player.position + (seconds * 1000)
                    if new_position > player.current.length:
                        new_position = player.current.length
                else:
                    new_position = player.position - (seconds * 1000)
                    if new_position < 0:
                        new_position = 0

                await player.seek(new_position)
                return await ctx.send(f"Moving forward to {seconds} seconds.")

            return await ctx.send(
                "Music paused. Use !resume to use this command."
            )

        await ctx.send("Bruh, it feels like I'm not playing anything.")

    @commands.command(aliases=["vol"])
    @voice_connected()
    @player_connected()
    @in_same_channel()
    async def volume(self, ctx, vol: int, forced=False):
        """Defines a volume"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"Whoops, I'm being used on the channel {player.bound_channel.mention}", delete_after=5
            )

        if vol < 0:
            return await ctx.send("Volume cannot be less than 0")

        if vol > 100 and not forced:
            return await ctx.send("Volume cannot be greater than 100")

        await player.set_volume(vol)
        await ctx.send(f"Volume set to {vol}")

    @commands.command()
    @voice_connected()
    @player_connected()
    @in_same_channel()
    async def loop(self, ctx, type: str):
        """Set the loop to `NONE`, `CURRENT` or `PLAYLIST`"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"Whoops, I'm being used on the channel {player.bound_channel.mention}", delete_after=5
            )

        valid_types = ["NONE", "CURRENT", "PLAYLIST"]
        type = type.upper()

        if type not in valid_types:
            return await ctx.send("The loop type must be `NONE`, `CURRENT` or `PLAYLIST`.")

        if len(player.queue._queue) < 1 and type == "PLAYLIST":
            return await ctx.send(
                "There must be 2 songs in the queue to use the PLAYLIST loop"
            )

        if not player.is_playing:
            return await ctx.send("I'm not playing any tracks. Unable to loop")

        player.loop = type

        await ctx.send(f"The player is now looping `{type}`")

    @commands.command(aliases=["np"])
    @voice_connected()
    @player_connected()
    @in_same_channel()
    async def nowplaying(self, ctx):
        """What's playing now?"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"Whoops, I'm being used on the channel {player.bound_channel.mention}", delete_after=5
            )

        if not player.current:
            return await ctx.send("Nothing is playing.")

        await player.invoke_player()

    @commands.command(aliases=["q"])
    @voice_connected()
    @player_connected()
    @in_same_channel()
    async def queue(self, ctx):
        """Songs in the Play Queue"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"Whoops, I'm being used on the channel {player.bound_channel.mention}", delete_after=5
            )

        queue = player.queue._queue
        if len(queue) < 1:
            return await ctx.send("Nenhuma música está na fila.")

        embed = discord.Embed(color=discord.Color(0x2F3136))
        embed.set_author(name="Queue", icon_url="https://cdn.shahriyar.dev/list.png")

        tracks = ""
        if player.loop == "CURRENT":
            next_song = f"Next > [{player.current.title}]({player.current.uri}) \n\n"
        else:
            next_song = ""

        if next_song:
            tracks += next_song

        for index, track in enumerate(queue):
            tracks += f"{index + 1}. [{track.title}]({track.uri}) \n"

        embed.description = tracks

        await ctx.send(embed=embed)

    @commands.command(aliases=["eq"])
    @voice_connected()
    @player_connected()
    @in_same_channel()
    async def equalizer(self, ctx):
        """Defines an equalizer"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"Whoops, I'm being used on the channel {player.bound_channel.mention}", delete_after=5
            )

        eqs = {
            "1️⃣": ["Flat", wavelink.eqs.Equalizer.flat()],
            "2️⃣": ["Boost", wavelink.eqs.Equalizer.boost()],
            "3️⃣": ["Metal", wavelink.eqs.Equalizer.metal()],
            "4️⃣": ["Piano", wavelink.eqs.Equalizer.piano()],
        }

        embed = discord.Embed(title="Select an equalizer")
        embed.description = f"Current equalizer - **{player.eq.name}**\n\n1. Flat \n2. Boost\n3. Metal\n4. Piano"
        embed.set_thumbnail(url="https://cdn.shahriyar.dev/equalizer.png")

        msg = await ctx.send(embed=embed)

        await msg.add_reaction("1️⃣")
        await msg.add_reaction("2️⃣")
        await msg.add_reaction("3️⃣")
        await msg.add_reaction("4️⃣")

        def check(reaction, user):
            return (
                reaction.message.id == msg.id
                and user.id == ctx.author.id
                and reaction.emoji in ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
            )

        while True:
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", timeout=60.0, check=check
                )
            except:
                await msg.delete()
                break

            selected_eq = eqs[reaction.emoji][1]
            await player.set_equalizer(selected_eq)

            embed.description = (
                f"Current equalizer - **{eqs[reaction.emoji][0]}**\n\n"
                "1. Flat \n2. Boost\n3. Metal\n4. Piano"
            )

            await msg.edit(embed=embed)

    @commands.command(aliases=["lyric"])
    async def lyrics(self, ctx, query: str = None):
        """Search song lyrics"""
        if not query:
            player: WebPlayer = self.bot.wavelink.get_player(
                ctx.guild.id, cls=WebPlayer
            )
            if not player.is_playing:
                return await ctx.send(
                    "Nothing is playing. Play a song to see its lyrics or type a song name while using this command"
                )

            title = player.current.title

        else:
            title = query

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://some-random-api.ml/lyrics?title={title}"
            ) as response:
                song_data = await response.json()
                if song_data:
                    lyrics = song_data["lyrics"]

        lines = [line.replace("\n", "") for line in lyrics.split("\n")]
        pages = []

        stack = ""
        for line in lines:
            new_stack = stack + line + "\n"
            if len(new_stack) > 300:
                pages.append(stack)
                stack = ""
            stack += line + "\n"

        if not pages:
            pages.append(stack)

        embed = discord.Embed(title=f"{song_data['author']}/{song_data['title']}")
        embed.description = pages[0]
        try:
            embed.set_thumbnail(url=song_data["thumbnail"]["genius"])
        except:
            pass

        if len(pages) == 1:
            return await ctx.send(embed=embed)

        else:
            current_page = 0
            embed.set_footer(text=f"{current_page + 1}/{len(pages)}")

            book: discord.Message = await ctx.send(embed=embed)
            buttons = ["◀️", "▶️"]

            for emoji in buttons:
                await book.add_reaction(emoji)

            await asyncio.sleep(1)
            while True:
                reaction, reaction_user = await self.bot.wait_for(
                    "reaction_add", timeout=180
                )

                if reaction.emoji == "◀️":
                    current_page -= 1
                    if current_page < 0:
                        current_page = 0
                        continue

                elif reaction.emoji == "▶️":
                    current_page += 1

                try:
                    await book.remove_reaction(reaction.emoji, reaction_user)
                except:
                    pass

                try:
                    content = pages[current_page]
                except:
                    current_page -= 1
                    continue

                embed.description = content
                embed.set_footer(text=f"{current_page + 1}/{len(pages)}")
                await book.edit(embed=embed)


def setup(bot):
    bot.add_cog(Music(bot))
