import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
import time

from server_data import ServerData

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)
server_data = ServerData()

running_status_in_servers = set()


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command/s")
    except Exception as e:
        print(e)


@bot.tree.command(name="pop")
async def pop(interaction: discord.Interaction, server_number: int = 2154):
    pop_msg = server_data.pop()

    embed = discord.Embed(title="EU-PVP-TheIsland2154", color=0x00ff00)
    embed.add_field(name="Active Players", value=pop_msg, inline=True)
    await interaction.response.send_message(embed=embed)


@bot.command(name="status")
async def status(ctx):

    # Check if the bot is already running on the server, if not just run it
    server_id = ctx.guild.id
    if server_id in running_status_in_servers:
        await ctx.send("I'm already running, wait :rage: ")
        return

    running_status_in_servers.add(server_id)
    role = f"<@&492494724528340992>"

    await ctx.send(f"Cheching server status... UwU")

    counter = 1
    while True:

        # Checks for server status every 15 seconds
        if not server_data.is_server_down():
            await ctx.send(f"{role} Server is up!")
            print("Server status: Online")
            break

        print(f"Server status: Offline - {counter}")
        counter += 1
        await asyncio.sleep(15)

    running_status_in_servers.remove(server_id)


class BotState:
    def __init__(self):
        self.running = False
        self.last_message = None


bot_state = BotState()
running_autopop_in_servers = set()


@bot.command(name="on")
async def on(ctx):
    # Check if the bot is already running on the server, if not just run it
    server_id = ctx.guild.id
    if server_id in running_autopop_in_servers:
        await ctx.send("I'm already running :rage: ")
        return

    running_autopop_in_servers.add(server_id)
    bot_state.running = True
    # await ctx.send(f"Autopop on! :smiling_imp:")
    while bot_state.running:
        if not server_data.is_server_down():  # To avoid running while the server is down
            pop_msg = server_data.pop()
            time_now = f"<t:{int(time.time())}>"
            embed = discord.Embed(title="EU-PVP-TheIsland2154", color=0x00ff00)
            embed.add_field(name="Active Players", value=pop_msg, inline=True)
            embed.add_field(name="Last update", value=time_now, inline=True)

            if bot_state.last_message:
                await bot_state.last_message.edit(embed=embed)
                # print(f"Message {bot_state.last_message.id} edited!")
            else:
                bot_state.last_message = await ctx.send(embed=embed)
                # print(f"Message {bot_state.last_message.id} sent!")

            # I use this method to allow the bot to be stopped while it's running because. I have to change the way this works
            for _ in range(180):
                await asyncio.sleep(1)
                if not bot_state.running:
                    break

    running_autopop_in_servers.remove(server_id)
    await ctx.send(f"Autopop off :smiling_face_with_tear:")


@bot.command(name="off")
async def off(ctx):
    if bot_state.running:
        bot_state.running = False

bot.run(TOKEN)
