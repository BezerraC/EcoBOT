import discord
from discord.ext import commands


class News(commands.Cog):
    """Inform the latest updates"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="news", aliases=["nw"])
    async def news(self, ctx):
        """Inform the latest updates"""
        embed = discord.Embed(title="NEWS 🎉🎉", color=discord.Color(0x2F3136))
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)

        description = f"Check the latest updates\n\n"
       
        description += "**Language** \nEcobot's content is now all in English to reach an international audience\n\n"
        description += "**Invite Command** \nNow you can generate an instant server invite.\n\n"
        
        description += "Developed by Eco#0745 \n\n"
        description += "*For more information call [developer](https://discord.gg/HahR7qjQ7s)*"

        embed.description = description
        await ctx.message.delete() 
        await ctx.send(embed=embed)
       


def setup(bot):
    bot.add_cog(News(bot))
