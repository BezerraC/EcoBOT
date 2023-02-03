
import datetime
import json
import random
import re

import aiohttp
import discord
import urllib3
from aiohttp.helpers import current_task
from discord.ext import commands


class Meme(commands.Cog):
    """Comandos De Meme"""

    def __init__(self, bot):
        self.bot = bot
        self.URL_REG = re.compile(r"https?://(?:www\.)?.+")

    @commands.command(name="meme", aliases=["m"])
    async def meme(self, ctx):
        """Exibe um meme aleatório"""
        async with aiohttp.ClientSession() as cs:
            a = 'DiretoDoZapZap'
            b = 'HUEStation'
            c = 'BrazilMemes'
            d = 'MemesBR'
            y = format(random.choice([a, b, c, d]))
            x =  f'https://meme-api.com/gimme/{str(y)}'
            print(x)
            async with cs.get(x) as r:
                res = await r.json()
                embed = discord.Embed(title=res['title'], color=0xD77AFE)
                embed.set_image(url=res['url'])
                await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Meme(bot))
