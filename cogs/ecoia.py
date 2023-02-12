
import asyncio
import os
import re

import aiohttp
import aiosqlite
import discord
import openai
from discord import File, Intents
from discord.ext import commands
from dotenv import load_dotenv
from easy_pil import Canvas, Editor, Font, font, load_image_async

from essentials.player import WebPlayer


class Ecoia(commands.Cog):
    """IA Commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, ctx):
        """Start the conversation with AI"""
        if 'eco' in ctx.content:
            async with ctx.channel.typing():
                GPT_TOKEN = os.getenv("GPT_TOKEN")
                query = ctx.content.replace("eco","")
                response = openai.Completion.create(
                    api_key = GPT_TOKEN,
                    model="text-davinci-003",
                    prompt=query,
                    temperature=0.5,
                    max_tokens=3000,
                    top_p=0.3,
                    frequency_penalty=0.5,
                    presence_penalty=0.0
                )
                
            await ctx.channel.send(content=response['choices'][0]['text'].replace(str(query), ""))
            print (query)

def setup(bot):
    bot.add_cog(Ecoia(bot))