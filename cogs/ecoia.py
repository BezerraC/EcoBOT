import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import google.generativeai as genai

class Ecoia(commands.Cog):
    """IA Commands"""

    def __init__(self, bot):
        self.bot = bot
        self.history = {} 

    @commands.Cog.listener()
    async def on_message(self, message):
        """Start the conversation with AI"""
        if message.author.bot:
            return

        if "eco" in message.content.lower():
            GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
            genai.configure(api_key=GEMINI_API_KEY)

            model = genai.GenerativeModel("gemini-1.5-flash")
            channel_id = str(message.channel.id)
            query = message.content

            # Initializes the history for the channel if it doesn't exist
            if channel_id not in self.history:
                self.history[channel_id] = []

            # Adds the current message to the channel's history
            self.history[channel_id].append(f"<@{message.author.id}>: {query}")

            # Keeps only the last 10 messages to prevent excessive history
            self.history[channel_id] = self.history[channel_id][-10:]

            # Creates a contextualized prompt using the history
            context = "\n".join(self.history[channel_id])
            prompt = f"Your name is Eco Bot, and you are interacting inside a Discord server. Your creator's name is <@208791519136710657>. Here is the conversation history from this channel:\n{context}\n\nNow, reply to the last message with context in the User's language:"

            # Generates a response from Gemini
            response = model.generate_content(prompt)

            if response and response.text:
                # Adds the bot's response to the channel's history
                self.history[channel_id].append(f"Eco: {response.text}")

                # Sends the response to the channel
                await message.channel.send(content=response.text)

def setup(bot):
    bot.add_cog(Ecoia(bot))