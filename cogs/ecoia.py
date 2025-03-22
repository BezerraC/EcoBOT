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
            user_id = str(message.author.id)  
            query = message.content

            # Initializes the user's history if it doesn't already exist.
            if user_id not in self.history:
                self.history[user_id] = []

            # Adds the current message to the history.
            self.history[user_id].append(f"<@{user_id}>: {query}")

            # Keeps only the last 10 interactions to prevent the history from becoming too large.
            self.history[user_id] = self.history[user_id][-10:]

            # Creates a contextualized prompt using the history.
            context = "\n".join(self.history[user_id])
            prompt = f"Your name is Eco Bot and you are interacting with the User inside the Discord server. Your creator's name is <@208791519136710657>. Here is the conversation history:\n{context}\n\nNow, reply to the last message with context with the User language:"

            # Generates a response from Gemini.
            response = model.generate_content(prompt)

            if response and response.text:
                # Adds the response to the history.
                self.history[user_id].append(response.text)

                # Sends the response to the user.
                await message.channel.send(content=response.text)

def setup(bot):
    bot.add_cog(Ecoia(bot))