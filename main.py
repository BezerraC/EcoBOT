import asyncio
import datetime
import math
import os
import random

import aiohttp
import aiosqlite
import discord
import openai
import wavelink
from discord import File, Intents
from discord.ext import commands
from dotenv import load_dotenv
from easy_pil import Canvas, Editor, Font, font, load_image_async

from essentials.player import WebPlayer

load_dotenv(".env")

os.environ["JISHAKU_NO_DM_TRACEBACK"] = "true"

class MusicBot(commands.AutoShardedBot):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)

        self.can_function = False
        self.error_message = (
            "Eco BOT is not ready to listen to your commands. Please try after a few minutes."
        )

        if not hasattr(self, "wavelink"):
            self.wavelink = wavelink.Client(bot=self)

        self.loop.create_task(self.start_nodes())

    async def on_message(self, message):
        await self.process_commands(message)


    async def on_ready(self):
        print(f"{self.user} Operating at --- 100%")
        await bot.change_presence(activity=discord.Activity(type = discord.ActivityType.listening, name = "/help"))


    async def start_nodes(self):
        await self.wait_until_ready()

        await self.wavelink.initiate_node(
            host="lavalink1.albinhakanson.se",
            port=1141,
            rest_uri="http://lavalink1.albinhakanson.se:1141",
            password="albinhakanson.se",
            identifier="MAIN",
            region="brazil",
        )

        for guild in self.guilds:
            if guild.me.voice:
                player: WebPlayer = self.wavelink.get_player(guild.id, cls=WebPlayer)
                try:
                    await player.connect(guild.me.voice.channel.id)
                    print(f"Connected to voice channel -> {guild.me.voice.channel.id}")
                except Exception as e:
                    print(e)

        self.can_function = True


intents = Intents.default()
intents.members = True

PREFIX = os.getenv("PREFIX")
bot = MusicBot(command_prefix=PREFIX, intents=intents)
bot.multiplier = 1

@bot.event
async def on_member_join(ctx):
    role = discord.utils.get(ctx.guild.roles, name = 'Members')
    await ctx.add_roles(role)

@bot.event
async def on_member_join(member):
        guild = member.guild
        channel = guild.system_channel 
        if channel.permissions_for(guild.me).send_messages: 
            f1 = 'it is a pleasure to welcome you here!'
            f2 = 'grab a cup of coffee and make yourself comfortable.'
            f3 = 'we are so glad you are here'
            f4 = 'We re so happy to see you.'
            rf = format(random.choice([f1, f2, f3, f4]))
            await channel.send(f"Thanks for joining us {member.mention} {str(rf)}")

@bot.event
async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send('🤔 Invalid command. use `/help` to see the list of commands')

@bot.event
async def on_guild_join(guild):
    await guild.text_channels[0].send("Salve gente bonita é uma honra está aqui\npara começar digite /help")


async def initialize():
    await bot.wait_until_ready()
    bot.db = await aiosqlite.connect("levels.db")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS guildData (guild_id int, user_id int, exp int, PRIMARY KEY (guild_id, user_id))")
    

@bot.event
async def on_message(message):
    if not message.author.bot:
        cursor = await bot.db.execute("INSERT OR IGNORE INTO guildData (guild_id, user_id, exp) VALUES (?,?,?)", (message.guild.id, message.author.id, 1)) 

        if cursor.rowcount == 0:
            await bot.db.execute("UPDATE guildData SET exp = exp + 1 WHERE guild_id = ? AND user_id = ?", (message.guild.id, message.author.id))
            cur = await bot.db.execute("SELECT exp FROM guildData WHERE guild_id = ? AND user_id = ?", (message.guild.id, message.author.id))
            data = await cur.fetchone()
            exp = data[0]
            lvl = math.sqrt(exp) / bot.multiplier
        
            if lvl.is_integer():
                await message.channel.send(f"{message.author.mention} You are on the level: {int(lvl)} now.")

        await bot.db.commit()

    await bot.process_commands(message)




@bot.command(name="rank", aliases=["rk"])
async def rank(ctx, member: discord.Member=None):
    """Display Your Server Status"""
    if member is None: member = ctx.author

    # get user exp
    async with bot.db.execute("SELECT exp FROM guildData WHERE guild_id = ? AND user_id = ?", (ctx.guild.id, member.id)) as cursor:
        data = await cursor.fetchone()
        exp = data[0]

        # calculate rank
    async with bot.db.execute("SELECT exp FROM guildData WHERE guild_id = ?", (ctx.guild.id,)) as cursor:
        rank = 1
        async for value in cursor:
            if exp < value[0]:
                rank += 1

    lvl = int(math.sqrt(exp)//bot.multiplier)

    current_lvl_exp = (bot.multiplier*(lvl))**2
    next_lvl_exp = (bot.multiplier*((lvl+1)))**2

    lvl_percentage = ((exp-current_lvl_exp) / (next_lvl_exp-current_lvl_exp)) * 100

    # -------------------------------------- EMBED CARD ---------------------------------------------

    embed = discord.Embed(title=f"Stats for {member.name}", colour=discord.Colour.gold())
    embed.add_field(name="Level", value=str(lvl))
    embed.add_field(name="Exp", value=f"{exp}/{next_lvl_exp}")
    embed.add_field(name="Rank", value=f"{rank}/{ctx.guild.member_count}")
    embed.add_field(name="Level Progress", value=f"{round(lvl_percentage, 2)}%")
    
    # -------------------------------------- RANK CARD ---------------------------------------------

    background = Editor("cards/cardbg.png")

    profile = await load_image_async(str(ctx.author.avatar_url))
    profile = Editor(profile).resize((150, 150)).circle_image()

    poppins = Font().poppins(size=40)
    poppins_small = Font().poppins(size=30)
    poppins_rank = Font().poppins(size=60)

    square = Canvas((500, 500), "#06FFBF")
    square = Editor(canvas=square)
    square.rotate(30, expand=True)

    # background.paste(square.image, (600, -250))
    background.paste(profile.image, (30, 30))
    background.text((700, 55), f"#{rank}", font=poppins_rank, color="white") # cor do numero do rank
    background.rectangle((30, 220), width=650, height=40, fill="white", radius=20) # cor da barra inteira
    background.bar((30, 220), max_width=650, height=40, percentage=lvl_percentage ,fill="#792af4", radius=20) # cor da barra enchendo
    background.text((200, 40), f"{member.name}", font=poppins, color="white") # cor do nome
    background.rectangle((200, 100), width=350, height=2, fill="white") # cor da linha em baixo do nome
    background.text((200, 130), f"Level : {lvl}   XP: {exp}/{next_lvl_exp}", font=poppins_small, color="white") # cor das info level e xp

    # -----------------------------------------------------------------------------------

    card = File(fp=background.image_bytes, filename="rank_card.png")
    await ctx.send(file=card)

@bot.command(name="leaderboard", aliases=["lb"])
async def leaderboard(ctx): 
    """Displays the Level Table"""
    buttons = {}
    for i in range(1, 6):
        buttons[f"{i}\N{COMBINING ENCLOSING KEYCAP}"] = i # only show first 5 pages

    previous_page = 0
    current = 1
    index = 1
    entries_per_page = 10

    embed = discord.Embed(title=f"Among the best: Page {current}", description="", colour=discord.Colour.gold())
    msg = await ctx.send(embed=embed)

    for button in buttons:
        await msg.add_reaction(button)

    while True:
        if current != previous_page:
            embed.title = f"Among the best: Page  {current}"
            embed.description = ""

            async with bot.db.execute(f"SELECT user_id, exp FROM guildData WHERE guild_id = ? ORDER BY exp DESC LIMIT ? OFFSET ? ", (ctx.guild.id, entries_per_page, entries_per_page*(current-1),)) as cursor:
                index = entries_per_page*(current-1)

                async for entry in cursor:
                    index += 1
                    member_id, exp = entry
                    member = ctx.guild.get_member(member_id)
                    lvl = math.sqrt(exp) / bot.multiplier
                    lvli = int(lvl)
                    embed.description += f"{index}) {member.mention} : Lv {lvli}\n"

                await msg.edit(embed=embed)

        try:
            reaction, user = await bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.emoji in buttons, timeout=60.0)

        except asyncio.TimeoutError:
            return await msg.clear_reactions()

        else:
            previous_page = current
            await msg.remove_reaction(reaction.emoji, ctx.author)
            current = buttons[reaction.emoji]

# -------------------------------------- TIC TAC TOE GAME ---------------------------------------------
player1 = ""
player2 = ""
turn = ""
gameOver = True

board = []

winningConditions = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6]
]

@bot.command(name="tictactoe", aliases=["ttt"])
async def tictactoe(ctx, p1: discord.Member, p2: discord.Member):
    """Starts tic-tac-toe with a player"""
    global count
    global player1
    global player2
    global turn
    global gameOver

    if gameOver:
        global board
        board = [":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:"]
        turn = ""
        gameOver = False
        count = 0

        player1 = p1
        player2 = p2

        # print the board
        line = ""
        for x in range(len(board)):
            if x == 2 or x == 5 or x == 8:
                line += " " + board[x]
                await ctx.send(line)
                line = ""
            else:
                line += " " + board[x]

        # determine who goes first
        num = random.randint(1, 2)
        if num == 1:
            turn = player1
            await ctx.send("It's time to <@" + str(player1.id) + ">.")
        elif num == 2:
            turn = player2
            await ctx.send("It's time to <@" + str(player2.id) + ">.")
    else:
        await ctx.send("The game is in progress! Finish this one to start another one.")

@bot.command(name="place", aliases=["set", "pl"])
async def place(ctx, pos: int):
    """Informs the position of the chosen seat from 1 to 9"""
    global turn
    global player1
    global player2
    global board
    global count
    global gameOver

    if not gameOver:
        mark = ""
        if turn == ctx.author:
            if turn == player1:
                mark = ":regional_indicator_x:"
            elif turn == player2:
                mark = ":o2:"
            if 0 < pos < 10 and board[pos - 1] == ":white_large_square:" :
                board[pos - 1] = mark
                count += 1

                # print the board
                line = ""
                for x in range(len(board)):
                    if x == 2 or x == 5 or x == 8:
                        line += " " + board[x]
                        await ctx.send(line)
                        line = ""
                    else:
                        line += " " + board[x]

                checkWinner(winningConditions, mark)
                print(count)
                if gameOver == True:
                    await ctx.send(mark + " won!")
                elif count >= 9:
                    gameOver = True
                    await ctx.send("Tied!")

                # switch turns
                if turn == player1:
                    turn = player2
                elif turn == player2:
                    turn = player1
            else:
                await ctx.send("Be sure to choose a number between 1 and 9 in an unmarked block.")
        else:
            await ctx.send("It's not your turn.")
    else:
        await ctx.send("Start a new game using the !tictactoe command.")


def checkWinner(winningConditions, mark):
    global gameOver
    for condition in winningConditions:
        if board[condition[0]] == mark and board[condition[1]] == mark and board[condition[2]] == mark:
            gameOver = True

@tictactoe.error
async def tictactoe_error(ctx, error):
    print(error)
    if isinstance(error, commands.BadArgument):
        await ctx.send("Mention 2 players for this command.")
    # elif isinstance(error, commands.BadArgument):
    #     await ctx.send("Por favor, certifique-se de mencionar/pingar jogadores (Ex. <@Eco>).")

@place.error
async def place_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Enter a position you would like to tag.")
    # elif isinstance(error, commands.BadArgument):
    #     await ctx.send("Certifique-se de inserir um número inteiro.")


# -------------------------------------- TETRIS GAME ---------------------------------------------

board = []
num_of_rows = 18
num_of_cols = 10
empty_square = ':black_large_square:'
blue_square = ':blue_square:'
brown_square = ':brown_square:'
orange_square = ':orange_square:'
yellow_square = ':yellow_square:'
green_square = ':green_square:'
purple_square = ':purple_square:'
red_square = ':red_square:'
embed_colour = 0x077ff7 #colour of line on embeds
points = 0
lines = 0 #how many lines cleared
down_pressed = False #if down button has been pressed
rotate_clockwise = False
rotation_pos = 0
h_movement = 0 #amount to move left or right
is_new_shape = False
start_higher = False #for when near top of board
game_over = False
index = 0


class Tetronimo: #Tetris pieces
    def __init__(self, starting_pos, colour, rotation_points):
        self.starting_pos = starting_pos #list
        self.colour = colour
        self.rotation_points = rotation_points #list

main_wall_kicks = [ #for J, L, T, S, Z tetronimos
                    [[0, 0], [0, -1], [-1, -1], [2, 0], [2, -1]],
                    [[0, 0], [0, 1], [1, 1], [-2, 0], [-2, 1]],
                    [[0, 0], [0, 1], [-1, 1], [2, 0], [2, 1]],
                    [[0, 0], [0, -1], [1, -1], [-2, 0], [-2, -1]]
                    ]

i_wall_kicks = [ #for I tetronimo
                [[0, 0], [0, -2], [0, 1], [1, -2], [-2, 1]],
                [[0, 0], [0, -1], [0, 2], [-2, -1], [1, 2]],
                [[0, 0], [0, 2], [0, -1], [-1, 2], [2, -1]],
                [[0, 0], [0, 1], [0, -2], [2, 1], [-1, -2]]
                ]

rot_adjustments = { #to move when rotations are slightly off
                #blue: not sure if needs any rn
                ':blue_square:': [[0, 1], [-1, -1], [0, 0], [-1, 0]], #[[0, 0], [0, 0], [0, 0], [0, 0]]
                #brown: left 1, right 1, right 1, left 1,
                ':brown_square:': [[0, 0], [0, 1], [0, 0], [0, -1]], #[[0, -1], [0, 1], [0, 1], [0, -1]]'
                #orange: left 1, nothing, right 1, nothing
                ':orange_square:': [[0, -1], [0, 0], [-1, 1], [0, 0]], #[[0, -1], [0, 0], [0, 1], [0, 0]]
                #none for yellow
                ':yellow_square:': [[0, 0], [0, 0], [0, 0], [0, 0]],
                #green: right 1, nothing, right 1, nothing
                ':green_square:': [[0, 0], [0, 0], [0, 0], [0, 0]], #[[0, 1], [0, 0], [0, 1], [0, 0]]
                #purple: nothing, right 1, left 1 (possibly up too), right 1
                ':purple_square:': [[0, 0], [1, 1], [0, -1], [0, 1]], #[[0, 0], [0, 1], [0, -1], [0, 1]]
                #red: left 1, up 1, right 1, up 1
                ':red_square:': [[1, -1], [-1, -1], [0, 2], [-1, -1]] #[[0, -1], [-1, 0], [0, 1], [-1, 0]]
                }

#starting spots, right above the board ready to be lowered. Col is 3/4 to start in middle
shape_I = Tetronimo([[0, 3], [0, 4], [0, 5], [0, 6]], blue_square, [1, 1, 1, 1])
shape_J = Tetronimo([[0, 3], [0, 4], [0, 5], [-1, 3]], brown_square, [1, 1, 2, 2])
shape_L = Tetronimo([[0, 3], [0, 4], [0, 5], [-1, 5]], orange_square, [1, 2, 2, 1])
shape_O = Tetronimo([[0, 4], [0, 5], [-1, 4], [-1, 5]], yellow_square, [1, 1, 1, 1])
shape_S = Tetronimo([[0, 3], [0, 4], [-1, 4], [-1, 5]], green_square, [2, 2, 2, 2])
shape_T = Tetronimo([[0, 3], [0, 4], [0, 5], [-1, 4]], purple_square, [1, 1, 3, 0])
shape_Z = Tetronimo([[0, 4], [0, 5], [-1, 3], [-1, 4]], red_square, [0, 1, 0, 2])


#fill board with empty squares
def make_empty_board():
    for row in range(num_of_rows):
        board.append([])
        for col in range(num_of_cols):
            board[row].append(empty_square)

def fill_board(emoji):
    for row in range(num_of_rows):
        for col in range(num_of_cols):
            if board[row][col] != emoji:
                board[row][col] = emoji


def format_board_as_str():
    board_as_str = ''
    for row in range(num_of_rows):
        for col in range(num_of_cols):
            board_as_str += (board[row][col]) # + " " possibly
            if col == num_of_cols - 1:
                board_as_str += "\n "
    return board_as_str

def get_random_shape():
    global index
    # ordered_shapes = [shape_J, shape_T, shape_L, shape_O, shape_S, shape_Z, shape_S, shape_T, shape_J, shape_Z, shape_S, shape_I, shape_Z, shape_O, shape_T, shape_J, shape_L, shape_Z, shape_I]
    # random_shape = ordered_shapes[index]
    shapes = [shape_I, shape_J, shape_L, shape_O, shape_S, shape_T, shape_Z]
    random_shape = shapes[random.randint(0, 6)] #0, 6
    index += 1
    if start_higher == True:
        for s in random_shape.starting_pos[:]: #for each square
            s[0] = s[0] - 1 #make row 1 above
    else:
        starting_pos = random_shape.starting_pos[:]
    random_shape = [random_shape.starting_pos[:], random_shape.colour, random_shape.rotation_points] #gets starting point of shapes and copies, doesn't change them
    global is_new_shape
    is_new_shape = True
    return random_shape #returns array with starting pos and colour

def do_wall_kicks(shape, old_shape_pos, shape_colour, attempt_kick_num):
    new_shape_pos = []

    if shape_colour == blue_square:
        kick_set = main_wall_kicks[rotation_pos]
    else:
        kick_set = i_wall_kicks[rotation_pos]

    # print('Kick set: ' + str(kick_set))
    for kick in kick_set:
        # print('Kick: ' + str(kick))
        for square in shape:
            square_row = square[0]
            square_col = square[1]
            new_square_row = square_row + kick[0]
            new_square_col = square_col + kick[1]
            if (0 <= new_square_col < num_of_cols) and (0 <= new_square_row < num_of_rows): #if square checking is on board
                square_checking = board[new_square_row][new_square_col] #get the square to check if empty
                if (square_checking != empty_square) and ([new_square_row, new_square_col] not in old_shape_pos): #if square is not empty / won't be when other parts of shape have moved
                    #shape doesn't fit
                    new_shape_pos = [] #reset new_shape
                    break
                else: #shape does fit
                    new_shape_pos.append([new_square_row, new_square_col]) #store pos
                    # print('New shape: ' + str(new_shape_pos))
                    if len(new_shape_pos) == 4:
                        # print('Returned new shape after doing kicks')
                        return new_shape_pos #return shape with kicks added
            else:
                #shape doesn't fit
                new_shape_pos = [] #reset new_shape
                break

    # print('Returned old, unrotated shape')
    return old_shape_pos #return shape without rotation


def rotate_shape(shape, direction, rotation_point_index, shape_colour):
    rotation_point = shape[rotation_point_index] #coords of rotation point
    new_shape = [] #to store coords of rotated shape

    #Rotate shape
    for square in shape:
        square_row = square[0]
        square_col = square[1]
        if direction == 'clockwise':
            new_square_row = (square_col - rotation_point[1]) + rotation_point[0] + rot_adjustments.get(shape_colour)[rotation_pos-1][0]
            # print('Adjustment made: ' + str(rot_adjustments.get(shape_colour)[rotation_pos-1][0]))
            new_square_col = -(square_row - rotation_point[0]) + rotation_point[1] + rot_adjustments.get(shape_colour)[rotation_pos-1][1]
            # print('Adjustment made: ' + str(rot_adjustments.get(shape_colour)[rotation_pos-1][1]))
        elif direction == 'anticlockwise': #currently not a thing
            new_square_row = -(square_col - rotation_point[1]) + rotation_point[0]
            new_square_col = (square_row - rotation_point[0]) + rotation_point[1]
        new_shape.append([new_square_row, new_square_col]) #store pos of rotated square
        if (0 <= square_col < num_of_cols) and (0 <= square_row < num_of_rows): #if on board
            board[square_row][square_col] = empty_square #make empty old square pos

    new_shape = do_wall_kicks(new_shape, shape, shape_colour, 0) #offset shape

    new_shape = sorted(new_shape, key=lambda l:l[0], reverse=True) #sort so that bottom squares are first in list
    # print('Rotated shape: ' + str(new_shape))

    #Place rotated shape (in case can't move down)
    if new_shape != shape: #if not same as old unrotated shape (in case places at start pos)
        for square in new_shape:
            square_row = square[0]
            square_col = square[1]
            board[square_row][square_col] = shape_colour

    return new_shape

def clear_lines():
    global board
    global points
    global lines
    lines_to_clear = 0
    for row in range(num_of_rows):
        row_full = True #assume line is full
        for col in range(num_of_cols):
            if board[row][col] == empty_square:
                row_full = False
                break #don't clear this row
        if row_full: #if line to clear
            lines_to_clear += 1
            #bring all lines above down
            board2 = board[:] #clone board
            for r in range(row, 0, -1): #for every row above row
                if r == 0: #if top row
                    for c in range(num_of_cols):
                        board2[r][c] = empty_square #make each spot empty
                else:
                    for c in range(num_of_cols):
                        board2[r][c] = board[r - 1][c] #make each spot the one above
            board = board2[:]
    if lines_to_clear == 1:
        points += 100
        lines += 1
    elif lines_to_clear == 2:
        points += 300
        lines += 2
    elif lines_to_clear == 3:
        points += 500
        lines += 3
    elif lines_to_clear == 4:
        points += 800
        lines += 4


def get_next_pos(cur_shape_pos):
    global h_movement
    global start_higher
    global game_over

    #Check if new pos for whole shape is available
    movement_amnt = 1

    if down_pressed == False:
        amnt_to_check = 1 #check space one below
    else:
        amnt_to_check = num_of_rows #check all rows until furthest available space

    for i in range(amnt_to_check):
        square_num_in_shape = -1
        for square in cur_shape_pos:
            next_space_free = True
            square_num_in_shape += 1
            square_row = square[0]
            square_col = square[1]
            if (0 <= square_col < num_of_cols): #if current column spot will fit
                if not (0 <= square_col + h_movement < num_of_cols): #if spot with column position changed won't fit
                    h_movement = 0 #just change row position
                if (0 <= square_row + movement_amnt < num_of_rows): #if new square row pos is on board
                    square_checking = board[square_row + movement_amnt][square_col + h_movement] #get the square to check if empty
                    if (square_checking != empty_square) and ([square_row + movement_amnt, square_col + h_movement] not in cur_shape_pos): #if square is not empty / won't be when other parts of shape have moved
                        #check if space free if not moving horizontally (in case going into wall) but still going down
                        h_movement = 0
                        square_checking = board[square_row + movement_amnt][square_col + h_movement]
                        if (square_checking != empty_square) and ([square_row + movement_amnt, square_col + h_movement] not in cur_shape_pos):
                            if movement_amnt == 1:
                                next_space_free = False #can't put shape there
                                # print('Detected a space that isnt free')
                                # print('Square checking: ' + str(square_row + movement_amnt) + ', ' + str(square_col + h_movement))
                                if is_new_shape: #if can't place new shape
                                    if start_higher == True:
                                        game_over = True
                                    else:
                                        start_higher = True
                            elif movement_amnt > 1: #if sending down
                                movement_amnt -= 1 #accomodate for extra 1 added to check if its free
                            return [movement_amnt, next_space_free] #stop checking
                    elif down_pressed == True:
                        if square_num_in_shape == 3: #only on last square in shape
                            movement_amnt += 1 #increase amount to move shape by
                elif square_row + movement_amnt >= num_of_rows: #new square row isn't on board
                    if movement_amnt == 1:
                        next_space_free = False #can't put shape there
                        # print('Detected a space that isnt free')
                    elif movement_amnt > 1: #if sending down
                        movement_amnt -= 1 #accomodate for extra 1 added to check if its free
                    return [movement_amnt, next_space_free] #stop checking
                elif down_pressed == True:
                    if square_num_in_shape == 3: #only on last square in shape
                        movement_amnt += 1 #increase amount to move shape by

    return [movement_amnt, next_space_free]


async def run_game(msg, cur_shape):
    global is_new_shape
    global h_movement
    global rotate_clockwise
    global rotation_pos

    cur_shape_pos = cur_shape[0]
    cur_shape_colour = cur_shape[1]

    if rotate_clockwise == True and cur_shape_colour != yellow_square:
        cur_shape_pos = rotate_shape(cur_shape_pos, 'clockwise', cur_shape[2][rotation_pos], cur_shape_colour) #rotate shape
        cur_shape = [cur_shape_pos, cur_shape_colour, cur_shape[2]] #update shape

    next_pos = get_next_pos(cur_shape_pos)[:]
    movement_amnt = next_pos[0]
    next_space_free = next_pos[1]

    #move/place shape if pos is available
    square_num_in_shape = -1
    if next_space_free:
        for square in cur_shape_pos:
            square_num_in_shape += 1
            square_row = square[0]
            square_col = square[1]
            if (0 <= square_row + movement_amnt < num_of_rows): #if new square row pos is on board
                square_changing = board[square_row + movement_amnt][square_col + h_movement] #get square to change
                board[square_row + movement_amnt][square_col + h_movement] = cur_shape_colour #changes square colour to colour of shape
                if is_new_shape == True:
                    is_new_shape = False #has been placed, so not new anymore
                if square_row > -1: #stops from wrapping around list and changing colour of bottom rows.
                    board[square_row][square_col] = empty_square #make old square empty again
                cur_shape_pos[square_num_in_shape] = [square_row + movement_amnt, square_col + h_movement] #store new pos of shape square
            else: #if new square row pos is not on board
                cur_shape_pos[square_num_in_shape] = [square_row + movement_amnt, square_col + h_movement] #store new pos of shape square
    else:
        global down_pressed
        down_pressed = False #reset it
        clear_lines() #check for full lines and clear them
        cur_shape = get_random_shape() #change shape
        rotation_pos = 0 #reset rotation
        # print('Changed shape.')

    if not game_over:
        #Update board
        embed = discord.Embed(description=format_board_as_str(), color=embed_colour)
        h_movement = 0 #reset horizontal movement
        rotate_clockwise = False #reset clockwise rotation
        await msg.edit(embed=embed)
        if not is_new_shape:
            await asyncio.sleep(1) #to keep under api rate limit
        await run_game(msg, cur_shape)
    else:
        # print('GAME OVER')
        desc = 'Points: {} \n Lines: {} \n \n Press ▶ to play again.'.format(points, lines)
        embed = discord.Embed(title='GAME OVER', description=desc, color=embed_colour)
        await msg.edit(embed=embed)
        await msg.remove_reaction("⬅", bot.user) #Left
        await msg.remove_reaction("⬇", bot.user) #Down
        await msg.remove_reaction("➡", bot.user) #Right
        await msg.remove_reaction("🔃", bot.user) #Rotate
        await msg.add_reaction("▶") #Play


async def reset_game():
    global down_pressed
    global rotate_clockwise
    global rotation_pos
    global h_movement
    global is_new_shape
    global start_higher
    global game_over
    global points
    global lines
    fill_board(empty_square)
    down_pressed = False
    rotate_clockwise = False
    rotation_pos = 0
    h_movement = 0 #amount to move left or right
    is_new_shape = False
    start_higher = False
    game_over = False
    next_space_free = True
    points = 0
    lines = 0

make_empty_board()


@bot.command(name="tetris", aliases=["trs"])
async def tetris(ctx): #Starts embed
    """Start the Tetris game"""
    await reset_game()
    embed = discord.Embed(title='Tetris - Eco Bot', description=format_board_as_str(), color=embed_colour)
    embed.add_field(name='How to play:', value='Use ⬅ ⬇ ➡ to move left, down, and right respectively. \n  \n Use 🔃 to rotate the piece. \n \n Press ▶ to play.', inline=False)

    msg = await ctx.send(embed=embed)

    #Add button choices / reactions
    await msg.add_reaction("▶") #Play

    #On new reaction:
    #Update board and board_as_str
    #await msg.edit(embed=embed)

@bot.event
async def on_reaction_add(reaction, user):
    global h_movement
    global rotation_pos
    if user != bot.user:
        msg = reaction.message
        if str(reaction.emoji) == "▶": #Play button pressed
            # print('O usuário pressionou o play')  
            await reset_game()
            await msg.remove_reaction("❌", bot.user) #Remove delete
            embed = discord.Embed(description=format_board_as_str(), color=embed_colour)
            await msg.remove_reaction("▶", user)
            await msg.remove_reaction("▶", bot.user)
            await msg.edit(embed=embed)
            await msg.add_reaction("⬅") #Left
            await msg.add_reaction("⬇") #Down
            await msg.add_reaction("➡") #Right
            await msg.add_reaction("🔃") #Rotate
            await msg.add_reaction("❌") #Stop game
            starting_shape = get_random_shape()
            await run_game(msg, starting_shape)

        if str(reaction.emoji) == "⬅": #Left button pressed
            # print('Left button pressed')
            h_movement = -1 #move 1 left
            await msg.remove_reaction("⬅", user)
        if str(reaction.emoji) == "➡": #Right button pressed
            # print('Right button pressed')
            h_movement = 1 #move +1 right
            await msg.remove_reaction("➡", user)
        if str(reaction.emoji) == "⬇": #Down button pressed
            # print('Down button pressed')
            global down_pressed
            down_pressed = True
            await msg.remove_reaction("⬇", user)
        if str(reaction.emoji) == "🔃": #Rotate clockwise button pressed
            # print('Rotate clockwise button pressed')
            global rotate_clockwise
            rotate_clockwise = True
            if rotation_pos < 3:
                rotation_pos += 1
            else:
                rotation_pos = 0 #go back to original pos
            await msg.remove_reaction("🔃", user)
        if str(reaction.emoji) == "❌": #Stop game button pressed
            #In future maybe put score screen here or a message saying stopping.
            await reset_game()
            await msg.delete()
        if str(reaction.emoji) == "🔴":
            await msg.edit(content="")



bot.load_extension("cogs.music")
bot.load_extension("cogs.meme")
bot.load_extension("cogs.events")
bot.load_extension("cogs.invite")
bot.load_extension("cogs.ecoia")
bot.load_extension("cogs.help")
bot.load_extension("cogs.news")
bot.load_extension("cogs.error_handler")

bot.load_extension("jishaku") # uncomment this if you want to debug for testing
bot.load_extension("cog_reloader") # Uncomment this if you want to hot reload extensions whenever they get editted
bot.loop.create_task(initialize())
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
asyncio.run(bot.db.close())