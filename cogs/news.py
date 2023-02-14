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
       
        description += "**Invite Command** \nNow you can generate an instant server invite.\n\n"

        description += "**Eco I.A** \nChange the max_token to `3000`, now he can process more lines in your answer\nAdd type effect, wen he staying processing a answer you can view the time in `typing`\n\n"
        
        description += "Developed by Eco#0745 \n\n"
        description += "*For more information call [developer](https://discord.gg/HahR7qjQ7s)*"

        embed.description = description
        await ctx.message.delete() 
        await ctx.send(embed=embed)
       


def setup(bot):
    bot.add_cog(News(bot))
