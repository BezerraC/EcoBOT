import discord
from discord.ext import commands


class Invite(commands.Cog):
    """Invite Command"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="invite", aliases=["ivt"])
    async def invite(self, ctx):
        """Display an embed with link to invite your server"""

         #Creating an invite link
        link = await ctx.channel.create_invite(xkcd=True, max_age = 0, max_uses = 0)
        #max_age = 0 The invite link will never exipre.
        #max_uses = 0 Infinite users can join throught the link.
        #-----------------------------------------------------#

        #-------Embed Time-----#
        em = discord.Embed(title=f"Join The {ctx.guild.name} Discord Server Now!", url=link, description=f"**{ctx.guild.member_count} Members**\n[**Click here to join**]({link})\n\n**Invite link for {ctx.channel.mention} is created.**\nNumber of uses: **Infinite**\nLink Expiry Time: **Never**", color=0x2F3136)
        
        #Embed Footer
        em.set_footer(text=f"Developed by Eco#0745")
        
        #Embed Thumbnail Image
        em.set_thumbnail(url=ctx.guild.icon_url)
        
        #Embed Author
        em.set_author(name="SERVER INVITE")
        #-----------------------------------------#
        await ctx.message.delete() 
        await ctx.send(f"> {link}", embed=em)
       


def setup(bot):
    bot.add_cog(Invite(bot))
