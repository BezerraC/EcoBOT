import discord
from discord.ext import commands


class News(commands.Cog):
    """Informa as últimas atualizações"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="news", aliases=["nw"])
    async def news(self, ctx):
        """Informa as últimas atualizações"""
        embed = discord.Embed(title="NOVIDADES 🎉🎉", color=discord.Color(0x2F3136))
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)

        description = f"Confira as últimas atualizações\n\n"
        description += "**(Return) Meme** \nVoltamos com o comando `/meme` contando com mais variedade de memes de qualidade\n\n"
        description += "**Música** \nAdicionado o comando `/stop`.\n\n"
        
        description += "Desenvolvido por: Eco#0745 \n\n"
        description += "*para mais informações acione o [desenvolvedor](https://discord.gg/HahR7qjQ7s)*"

        embed.description = description
        await ctx.message.delete() 
        await ctx.send(embed=embed)
       


def setup(bot):
    bot.add_cog(News(bot))
