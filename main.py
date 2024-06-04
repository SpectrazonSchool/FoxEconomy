import discord
from discord.ext import commands
import random
import json
from discord import app_commands
import os

intents = discord.Intents.default()
intents.members = True  # Enable the members intent
intents.message_content = True  # Enable the message content intent

bot = commands.Bot(command_prefix="!", intents=intents)

# Load or initialize data
try:
    with open("data.json", "r") as f:
        data = json.load(f)
except FileNotFoundError:
    data = {"users": {}, "shop": {"item1": 100, "item2": 200}}

def save_data():
    with open("data.json", "w") as f:
        json.dump(data, f)

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    guild = discord.utils.get(bot.guilds)
    if guild:
        for member in guild.members:
            if str(member.id) not in data["users"]:
                data["users"][str(member.id)] = {"xp": 0, "level": 1, "balance": 0, "inventory": []}
        save_data()

@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name="Member")
    if role:
        await member.add_roles(role)
    if str(member.id) not in data["users"]:
        data["users"][str(member.id)] = {"xp": 0, "level": 1, "balance": 0, "inventory": []}
        save_data()

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    user_data = data["users"].get(str(message.author.id), None)
    if user_data:
        xp = random.randint(1, 10)
        user_data["xp"] += xp
        if user_data["xp"] >= user_data["level"] * 100:
            user_data["level"] += 1
            await message.channel.send(f'{message.author.mention} has leveled up to level {user_data["level"]}!')
        save_data()
    await bot.process_commands(message)

@bot.tree.command(name="ping", description="Replies with pong")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("pong")

@bot.tree.command(name="balance", description="Shows your balance")
async def balance(interaction: discord.Interaction):
    user_data = data["users"].get(str(interaction.user.id), None)
    if user_data:
        await interaction.response.send_message(f'{interaction.user.mention}, your balance is {user_data["balance"]} coins.')
    else:
        await interaction.response.send_message("User data not found.")

@bot.tree.command(name="shop", description="Displays shop items")
async def shop(interaction: discord.Interaction):
    shop_items = "\n".join([f"{item}: {price} coins" for item, price in data["shop"].items()])
    await interaction.response.send_message(f'Shop items:\n{shop_items}')

@bot.tree.command(name="buy", description="Buy an item from the shop")
@app_commands.describe(item="The item you want to buy")
async def buy(interaction: discord.Interaction, item: str):
    user_data = data["users"].get(str(interaction.user.id), None)
    if item in data["shop"]:
        if user_data["balance"] >= data["shop"][item]:
            user_data["balance"] -= data["shop"][item]
            user_data["inventory"].append(item)
            save_data()
            await interaction.response.send_message(f'{interaction.user.mention}, you have bought {item}!')
        else:
            await interaction.response.send_message(f'{interaction.user.mention}, you do not have enough coins.')
    else:
        await interaction.response.send_message(f'{interaction.user.mention}, that item does not exist in the shop.')

@bot.tree.command(name="work", description="Work to earn coins")
async def work(interaction: discord.Interaction):
    user_data = data["users"].get(str(interaction.user.id), None)
    if user_data:
        earnings = random.randint(50, 150)
        user_data["balance"] += earnings
        save_data()
        await interaction.response.send_message(f'{interaction.user.mention}, you earned {earnings} coins!')

bot.run(os.getenv('DISCORD_BOT_TOKEN'))
