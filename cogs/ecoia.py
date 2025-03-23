import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import google.generativeai as genai

class Ecoia(commands.Cog):
    """AI Commands"""

    def __init__(self, bot):
        self.bot = bot
        self.history = {} 

    @commands.Cog.listener()
    async def on_message(self, message):
        """Start the conversation with AI"""
        if message.author.bot:
            return

        query = message.content
        channel_id = str(message.channel.id)

        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=GEMINI_API_KEY)

        model = genai.GenerativeModel("gemini-1.5-flash")

        # Initializes the history for the channel if it doesn't exist
        if channel_id not in self.history:
            self.history[channel_id] = []

        # Adds the current message to the channel's history
        self.history[channel_id].append(f"<@{message.author.id}>: {query}")

        # Keeps only the last 10 messages to prevent excessive history
        self.history[channel_id] = self.history[channel_id][-10:]

        # Creates a contextualized prompt with instructions for voice detection
        context = "\n".join(self.history[channel_id])
        prompt = (
            "Your name is Eco Bot, and you are interacting inside a Discord server. "
            "Your creator's name is <@208791519136710657>. Here is the conversation history from this channel:\n"
            f"{context}\n\n"
            "Now, reply to the last message with context in the User's language.\n\n"
            "IMPORTANT: If the user is asking you to join a voice channel, respond with ONLY the word 'JOIN_VOICE'. "
            "Otherwise, reply normally to their message."
        )

        # Generates a response from Gemini
        response = model.generate_content(prompt)

        if response and response.text:
            response_text = response.text.strip()

            if response_text == "JOIN_VOICE":
                # User wants the bot to join voice
                if message.author.voice and message.author.voice.channel:
                    voice_channel = message.author.voice.channel
                    voice_client = discord.utils.get(self.bot.voice_clients, guild=message.guild)

                    if voice_client and voice_client.is_connected():
                        await voice_client.move_to(voice_channel)
                    else:
                        await voice_channel.connect()

                    await message.channel.send(f"✅ Connected to {voice_channel.name}!")
                else:
                    await message.channel.send("❌ You need to be in a voice channel for me to join!")
            else:
                # Normal AI response
                self.history[channel_id].append(f"Eco Bot: {response_text}")
                await message.channel.send(content=response_text)

def setup(bot):
    bot.add_cog(Ecoia(bot))