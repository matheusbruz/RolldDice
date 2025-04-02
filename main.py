import discord
from discord import app_commands
import re
import random
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

def parse_dice_notation(notation):
    pattern = r'(\d+)d(\d+)([adv|dis]*)([+-]\d+)?'
    match = re.match(pattern, notation)
    
    if not match:
        return None
    
    num_dice = int(match.group(1))
    dice_value = int(match.group(2))
    advantage_type = match.group(3) if match.group(3) else ""
    modifier = int(match.group(4)) if match.group(4) else 0
    
    return num_dice, dice_value, advantage_type, modifier

def roll_dice(num_dice, dice_value, advantage_type="", modifier=0):
    rolls = []
    
    if advantage_type == "adv":
        # Roll with advantage (roll twice, take highest)
        roll1 = [random.randint(1, dice_value) for _ in range(num_dice)]
        roll2 = [random.randint(1, dice_value) for _ in range(num_dice)]
        rolls = [max(r1, r2) for r1, r2 in zip(roll1, roll2)]
        detailed_rolls = [f"{r1},{r2}→{max(r1, r2)}" for r1, r2 in zip(roll1, roll2)]
    elif advantage_type == "dis":
        # Roll with disadvantage (roll twice, take lowest)
        roll1 = [random.randint(1, dice_value) for _ in range(num_dice)]
        roll2 = [random.randint(1, dice_value) for _ in range(num_dice)]
        rolls = [min(r1, r2) for r1, r2 in zip(roll1, roll2)]
        detailed_rolls = [f"{r1},{r2}→{min(r1, r2)}" for r1, r2 in zip(roll1, roll2)]
    else:
        # Normal roll
        rolls = [random.randint(1, dice_value) for _ in range(num_dice)]
        detailed_rolls = [str(roll) for roll in rolls]
    
    total = sum(rolls) + modifier
    
    return rolls, detailed_rolls, total

def format_roll_result(notation, rolls, detailed_rolls, total, modifier):
    result = f"🎲 **{notation}**: ["
    result += ", ".join(detailed_rolls)
    result += "]"
    
    if modifier != 0:
        result += f" {'+' if modifier > 0 else ''}{modifier}"
    
    result += f" = **{total}**"
    return result

@tree.command(name="rolld", description="Roll dice using standard notation (e.g. 3d6+2)")
async def rolld(interaction, dice: str):
    result = process_dice_command(dice)
    if result:
        await interaction.response.send_message(result)
    else:
        await interaction.response.send_message("Invalid dice notation. Use format like '3d6+2' or '1d20adv'.")

def process_dice_command(dice_notation):
    dice_notation = dice_notation.lower().replace(" ", "")
    parsed = parse_dice_notation(dice_notation)
    
    if not parsed:
        return None
    
    num_dice, dice_value, advantage_type, modifier = parsed
    
    # Limit reasonable values to prevent abuse
    if num_dice > 100 or dice_value > 1000:
        return "Please use reasonable dice values (max 100 dice with up to 1000 sides)"
    
    rolls, detailed_rolls, total = roll_dice(num_dice, dice_value, advantage_type, modifier)
    return format_roll_result(dice_notation, rolls, detailed_rolls, total, modifier)

@client.event
async def on_ready():
    await tree.sync()
    print(f'{client.user} is connected and ready!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    content = message.content.strip()
    
    # Check if the message contains only dice notation without command prefix
    dice_pattern = r'^\d+d\d+([adv|dis]*)([+-]\d+)?$'
    if re.match(dice_pattern, content):
        result = process_dice_command(content)
        if result:
            await message.channel.send(result)

client.run(TOKEN)