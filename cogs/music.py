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
    """Comandos De Música"""

    def __init__(self, bot):
        self.bot = bot
        self.URL_REG = re.compile(r"https?://(?:www\.)?.+")

    @commands.command(name="connect", aliases=["con", "c"])
    @voice_connected()
    async def connect_(self, ctx):
        """Conecta o Eco BOT"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if player.is_connected:
            if not player.bound_channel:
                player.bound_channel = ctx.channel

            if player.channel_id == ctx.channel.id:
                return await ctx.send(
                    f"Eco BOT está conectado a um canal de voz diferente."
                )

            return await ctx.send(
                "Eco BOT já se encontra conectado ao seu canal de voz."
            )

        channel = ctx.author.voice.channel
        self.bot.voice_users[ctx.author.id] = channel.id

        msg = await ctx.send(f"Conectando em **`{channel.name}`**")
        await player.connect(channel.id)
        player.bound_channel = ctx.channel
        await msg.edit(
            content=f"Conectado em **`{channel.name}`** " #and bounded to {ctx.channel.mention}
        )

    @commands.command(name="stop", aliases=["st"])
    @voice_connected()
    @player_connected()
    @in_same_channel()
    async def disconnect_(self, ctx):
        """Para todo o player de música"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)
        await ctx.send(f"Desconectando, até breve...")
        await player.destroy()

    @commands.command(name="play", aliases=["p"])
    @voice_connected()
    async def play_(self, ctx, *, query):
        """Tocar ou adicionar música à fila"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if not player.is_connected:
            await ctx.invoke(self.connect_)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"Epa, estou sendo usado no canal {player.bound_channel.mention}", delete_after=5
            )

        msg = await ctx.send(f"Procurando por `{query}` :mag_right:")
        query = query.strip("<>")
        if not self.URL_REG.match(query):
            query = f"ytsearch:{query}"

        tracks = await self.bot.wavelink.get_tracks(query)

        if not tracks:
            return await msg.edit(content="Não consegui encontrar nenhum resultado com essa consulta.")

        if isinstance(tracks, wavelink.TrackPlaylist):
            for track in tracks.tracks:
                await player.queue.put(track)

            msg.edit(
                content=f'Adicionando a playlist **{tracks.data["playlistInfo"]["name"]}** com **{len(tracks.tracks)}** músicas à fila.'
            )
        else:
            await player.queue.put(tracks[0])

            await msg.edit(content=f"Adicionando **{str(tracks[0])}** à fila.")

        if not player.is_playing:
            await player.do_next()

    @commands.command()
    @voice_connected()
    @player_connected()
    @in_same_channel()
    async def skip(self, ctx):
        """Pula a atual música"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"Epa, estou sendo usado no canal {player.bound_channel.mention}", delete_after=5
            )

        current_loop = player.loop
        player.loop = "NENHUM"

        await player.stop()

        if current_loop != "ATUAL":
            player.loop = current_loop

    @commands.command()
    @voice_connected()
    @player_connected()
    @in_same_channel()
    async def pause(self, ctx):
        """Pausa o player de música"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"Epa, estou sendo usado no canal {player.bound_channel.mention}", delete_after=5
            )

        if player.is_playing:
            if player.is_paused:
                return await ctx.send("A música já está pausada.")

            await player.set_pause(pause=True)
            return await ctx.send("Pausando a música.")

        await ctx.send("Epa, não estou tocando nada no momento.")

    @commands.command()
    @player_connected()
    @voice_connected()
    @in_same_channel()
    async def resume(self, ctx):
        """Volta a reproduzir a música"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"Epa, estou sendo usado no canal {player.bound_channel.mention}", delete_after=5
            )

        if player.is_playing:
            if not player.is_paused:
                return await ctx.send("A música não está pausada.")

            await player.set_pause(pause=False)
            return await ctx.send("Opa rodando a música de novo.")

        await ctx.send("Ops, não estou tocando nenhuma música.")

    @commands.command()
    @voice_connected()
    @player_connected()
    @in_same_channel()
    async def seek(self, ctx, seconds: int, reverse: bool = False):
        """Avança a música para frente ou para trás"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"Epa, estou sendo usado no canal {player.bound_channel.mention}", delete_after=5
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
                return await ctx.send(f"Avançando para {seconds} segundos.")

            return await ctx.send(
                "Música pausada. Use !resume para usar esse comando."
            )

        await ctx.send("Ixi, parece que não estou tocando nada.")

    @commands.command(aliases=["vol"])
    @voice_connected()
    @player_connected()
    @in_same_channel()
    async def volume(self, ctx, vol: int, forced=False):
        """Define um volume"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"Epa, estou sendo usado no canal {player.bound_channel.mention}", delete_after=5
            )

        if vol < 0:
            return await ctx.send("O volume não pode ser menor que 0")

        if vol > 100 and not forced:
            return await ctx.send("O volume não pode ser maior que 100")

        await player.set_volume(vol)
        await ctx.send(f"Volume definido em {vol}")

    @commands.command()
    @voice_connected()
    @player_connected()
    @in_same_channel()
    async def loop(self, ctx, type: str):
        """Define o loop como `NENHUM`, `ATUAL` ou `PLAYLIST`"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"Epa, estou sendo usado no canal {player.bound_channel.mention}", delete_after=5
            )

        valid_types = ["NENHUM", "ATUAL", "PLAYLIST"]
        type = type.upper()

        if type not in valid_types:
            return await ctx.send("O tipo de loop deve ser `NENHUM`, `ATUAL` ou `PLAYLIST`.")

        if len(player.queue._queue) < 1 and type == "PLAYLIST":
            return await ctx.send(
                "Deve haver 2 músicas na fila para usar o loop PLAYLIST"
            )

        if not player.is_playing:
            return await ctx.send("Não estou tocando nenhuma faixa. Não é possível fazer um loop")

        player.loop = type

        await ctx.send(f"O player agora está em loop `{type}`")

    @commands.command(aliases=["np"])
    @voice_connected()
    @player_connected()
    @in_same_channel()
    async def nowplaying(self, ctx):
        """O que está tocando agora?"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"Epa, estou sendo usado no canal {player.bound_channel.mention}", delete_after=5
            )

        if not player.current:
            return await ctx.send("Nada está sendo reproduzido.")

        await player.invoke_player()

    @commands.command(aliases=["q"])
    @voice_connected()
    @player_connected()
    @in_same_channel()
    async def queue(self, ctx):
        """Músicas na fila de reprodução"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"Epa, estou sendo usado no canal {player.bound_channel.mention}", delete_after=5
            )

        queue = player.queue._queue
        if len(queue) < 1:
            return await ctx.send("Nenhuma música está na fila.")

        embed = discord.Embed(color=discord.Color(0x2F3136))
        embed.set_author(name="Queue", icon_url="https://cdn.shahriyar.dev/list.png")

        tracks = ""
        if player.loop == "ATUAL":
            next_song = f"Prôxima > [{player.current.title}]({player.current.uri}) \n\n"
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
        """Define um equalizador"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"Epa, estou sendo usado no canal {player.bound_channel.mention}", delete_after=5
            )

        eqs = {
            "1️⃣": ["Flat", wavelink.eqs.Equalizer.flat()],
            "2️⃣": ["Boost", wavelink.eqs.Equalizer.boost()],
            "3️⃣": ["Metal", wavelink.eqs.Equalizer.metal()],
            "4️⃣": ["Piano", wavelink.eqs.Equalizer.piano()],
        }

        embed = discord.Embed(title="Selecione um equalizador")
        embed.description = f"Equalizador atual - **{player.eq.name}**\n\n1. Flat \n2. Boost\n3. Metal\n4. Piano"
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
                f"Equalizador atual - **{eqs[reaction.emoji][0]}**\n\n"
                "1. Flat \n2. Boost\n3. Metal\n4. Piano"
            )

            await msg.edit(embed=embed)

    @commands.command(aliases=["lyric"])
    async def lyrics(self, ctx, query: str = None):
        """Procura letra de música"""
        if not query:
            player: WebPlayer = self.bot.wavelink.get_player(
                ctx.guild.id, cls=WebPlayer
            )
            if not player.is_playing:
                return await ctx.send(
                    "Nada está tocando. Toque uma música para ver suas letras ou digite o nome de uma música enquanto usa este comando"
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
