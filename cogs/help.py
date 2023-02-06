import discord
from discord.ext import commands


class HelpCog(commands.HelpCommand):
    def __init__(self, **options):
        super().__init__(**options)
        self.color = discord.Color(0x2F3136)

    async def send_bot_help(self, mapping):
        ctx = self.context
        prefix = ctx.prefix
        pre = self.clean_prefix

        embed = discord.Embed(title="Eco BOT help", color=self.color)
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)

        description = f"For more detailed help write: `{prefix}help <command>` \n\n"
        description += "For the latest updates write: `/news` \n\n"
        description += "**I.A Commands** \n`eco` Start a conversation with the Integrated AI, e.g. talk to me eco..\n\n"
        description += "**Invite Commands** \n`/invite` Generate an instant server invite\n\n"
        description += "**Music Commands** \n`/play` Search and play any song\n\n`/stop` Stop the music player\n\n`/skip` Skip to next song\n\n`/pause` Pause the music\n\n`/resume` Go back where the music left off\n\n`/seek` Fast-forward or rewind as many seconds of the song\n\n`/volume` Change bot volume\n\n`/loop` Loop the music with 3 possible options\n\n`/nowplaying` See the song that is currently playing\n\n`/queue` Show the song list\n\n`/equalizer` Change music equalization with 3 different options\n\n`/lyrics` See the lyrics of the song\n\n"
        description += "**Level Commands** \n`/rank` Show your level on the server\n\n`/leaderboard` Show server leaderboard\n\n "
        description += "**Games Commands** \n Tic Tac Toe:\n `/tictactoe` Start tic-tac-toe with one player\n\n `/place` Informs the position of the chosen location from 1 to 9\n\n Tetris:\n `/tetris` Start the tetris game\n\n"
        description += "**Meme Commands** \n `/memebr` Get a meme from some brazilian meme subreddit\n\n `/memeus` Get a meme from some american meme subreddit\n\n"
        # description += "**Comandos de Meme** \n`!meme` Receba um meme 🙂\n\n"
        description += "Developed by Eco#0745 \n\n"
        description += "*For more information call [developer](https://discord.gg/HahR7qjQ7s)*"

        embed.description = description

        await ctx.send(embed=embed)

        # await ctx.send(embed=embed, components=[
        #     [Button(label="Convide-me", style=5,url="https://discord.com/api/oauth2/authorize?client_id=941379078475362344&permissions=8&scope=bot", custom_id="button1"), 
        #      Button(label="Donate",style=5,url="https://www.buymeacoffee.com/ecodj", custom_id="button2"),
        #      Button(label="Reportar Bug",style=5,url="https://www.devcbezerra.com/#contact", custom_id="button3")]
        # ])

    async def send_cog_help(self, cog):
        ctx = self.context
        pre = self.clean_prefix

        embed = discord.Embed(
            color=self.color, timestamp=ctx.message.created_at, description=""
        )

        if await ctx.bot.is_owner(ctx.author):
            shown_commands = [command for command in cog.get_commands()]
        else:
            shown_commands = [
                command
                for command in cog.get_commands()
                if command.hidden == False and command.enabled == True
            ]

        if len(shown_commands) == 0:
            return await ctx.send("No commands.")

        if cog.description:
            cog_help = cog.description
        else:
            cog_help = "No commands provided"

        embed.title = f"{cog.qualified_name}"
        embed.description += f"{cog_help}\nUse `{pre}help <command>` for more details.\n\n**Commands :** \n"

        for command in shown_commands:
            embed.description += f"▪︎ {pre}{command.qualified_name} "
            if command.signature:
                embed.description += f"{command.signature} \n"
            else:
                embed.description += "\n"

        embed.set_thumbnail(url=ctx.bot.user.avatar_url)
        await ctx.send(embed=embed)

    # Command Help
    async def send_command_help(self, command):
        ctx = self.context

        embed = discord.Embed(
            color=self.color,
            timestamp=ctx.message.created_at,
            description="",
        )

        if (
            command.hidden == True or command.enabled == False
        ) and await ctx.bot.is_owner(ctx.author) == False:
            return await ctx.send(
                f'No command called "{command.qualified_name}" founded.'
            )

        if command.signature:
            embed.title = f"{command.qualified_name} {command.signature} \n"
        else:
            embed.title = f"{command.qualified_name}\n"

        embed.description = command.help or "No description provided."

        if len(command.aliases) > 0:
            embed.description += "\aAbbreviation : " + ", ".join(command.aliases)

        embed.set_thumbnail(url=ctx.bot.user.avatar_url)
        await ctx.send(embed=embed)

    # Group Help
    async def send_group_help(self, group):
        ctx = self.context
        pre = ctx.clean_prefix

        embed = discord.Embed(color=self.color, timestamp=ctx.message.created_at)

        if group.signature:
            embed.title = f"{group.qualified_name} {group.signature}"
        else:
            embed.title = group.qualified_name + " - group"

        embed.description = group.help or "No description provided."
        embed.description += f"\nUse `{pre}help {group.qualified_name} <sub_command>` for more details of the command group. \n\n**Subcommands : **\n"

        if await ctx.bot.is_owner(ctx.author):
            group_commands = [command for command in group.commands]
            if len(group_commands) == 0:
                return await ctx.send("This group has no subcommands")
        else:
            group_commands = [
                command
                for command in group.commands
                if command.hidden == False and command.enabled == True
            ]

        if len(group_commands) == 0:
            return await ctx.send(f'No command called "{group.qualified_name}" founded.')

        for command in group_commands:
            if command.signature:
                command_help = (
                    f"▪︎ {pre}{command.qualified_name} {command.signature} \n"
                )
            else:
                command_help = f"▪︎ {pre}{command.qualified_name} \n"

            embed.description += command_help

        embed.set_thumbnail(url=ctx.bot.user.avatar_url)
        await ctx.send(embed=embed)


class Help(commands.Cog):
    """Help Commands"""

    def __init__(self, client):
        self.client = client
        self.client._original_help_command = client.help_command
        client.help_command = HelpCog()
        client.help_command.cog = self

    def cog_unload(self):
        self.client.help_command = self.client._original_help_command


def setup(client):
    client.add_cog(Help(client))
