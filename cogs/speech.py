import os

import openai
import speech_recognition as sr
from discord import *
from discord.ext import commands


def listen_microphone():
    microfone = sr.Recognizer()
    with sr.Microphone() as source:
            microfone.adjust_for_ambient_noise(source, duration=0.8)
            print("Listening...")
            audio = microfone.listen(source)
            with open('recordings/speech.wav', 'wb') as f:
                    f.write(audio.get_wav_data())
    try:
            frase = microfone.recognize_google(audio, language='pt-BR')
            print("Voce disse: " + frase)
    except sr.UnknownValueError:
            frase = ''
            print("Nao entendi")
    return frase

class Speech(commands.Cog):
    """Speech Recognition"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """Speech Recognition Commands"""
        msg = message.content.lower()
        eco = "eco"

        if message.author != self.bot.user: # make sure the message isn't from the bot itself
            if message.mentions: # check if the message contains any mentions 
                for mention in message.mentions: # loop through all mentions 
                    if mention == self.bot.user: # check if one of the mentions is the bot itself 

                        await message.delete()

                        msg = await message.channel.send("Alright let`s do it", delete_after=3) # send a response to the user's channel 
                                        
                        microfone = sr.Recognizer()
                        with sr.Microphone() as source:
                                microfone.adjust_for_ambient_noise(source, duration=0.8)
                                print("Listening")
                                ltg = await message.channel.send("Listening...")
                                audio = microfone.listen(source)
                        with open('recordings/speech.wav', 'wb') as f:
                                f.write(audio.get_wav_data())
                        try:
                                frase = microfone.recognize_google(audio, language='pt-BR')
                                print("Voce disse: " + frase)
                                await ltg.edit(content=message.author.mention + ": " + frase)
                                GPT_TOKEN = os.getenv("GPT_TOKEN")
                                query = message.content #.replace("eco","")
                                response = openai.Completion.create(
                                api_key = GPT_TOKEN,
                                model="text-davinci-003",
                                prompt=frase, #switch to query for text message
                                temperature=0.5,
                                max_tokens=2000,
                                top_p=0.3,
                                frequency_penalty=0.5,
                                presence_penalty=0.0
                                )
                                                
                                await message.channel.send(content=response['choices'][0]['text'].replace(str(query), ""))


                                # await msg.edit(content=f"Voce disse: " + frase)
                        except sr.UnknownValueError:
                                frase = ''
                                print("Nao entendi")
                                await ltg.edit(content=f"Sorry, I didn't understand what you say...")
                        return frase


        if not message.author.bot:
            if eco in msg:
                GPT_TOKEN = os.getenv("GPT_TOKEN")
                query = message.content #.replace("eco","")
                response = openai.Completion.create(
                    api_key = GPT_TOKEN,
                    model="text-davinci-003",
                    prompt=query,
                    temperature=0.5,
                    max_tokens=2000,
                    top_p=0.3,
                    frequency_penalty=0.5,
                    presence_penalty=0.0
                )
                await message.channel.send(content=response['choices'][0]['text'].replace(str(query), ""))
                # print (query)

def setup(bot):
    bot.add_cog(Speech(bot))