import discord
from discord import app_commands
import re
import random
import os
import json
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Estrutura para armazenar estatísticas
class Stats:
    def __init__(self):
        self.total_rolls = 0
        self.load_stats()
    
    def load_stats(self):
        try:
            if os.path.exists('stats.json'):
                with open('stats.json', 'r') as f:
                    data = json.load(f)
                    self.total_rolls = data.get('total_rolls', 0)
        except Exception as e:
            print(f"Erro ao carregar estatísticas: {e}")
    
    def save_stats(self):
        try:
            with open('stats.json', 'w') as f:
                json.dump({
                    'total_rolls': self.total_rolls
                }, f)
        except Exception as e:
            print(f"Erro ao salvar estatísticas: {e}")
    
    def increment_rolls(self, count=1):
        self.total_rolls += count
        self.save_stats()

# Instanciar as estatísticas
stats = Stats()

def parse_dice_notation(notation):
    # Padrão para rolagem normal com vantagem/desvantagem e modificadores
    base_pattern = r'(\d+)d(\d+)([adv|dis]*)([+-]\d+)?'
    
    # Padrão para rolagem com contagem de sucessos (ex: 5d10cd6)
    success_pattern = r'(\d+)d(\d+)cd(\d+)'
    
    # Tentativa com contagem de sucessos primeiro
    success_match = re.match(success_pattern, notation)
    if success_match:
        num_dice = int(success_match.group(1))
        dice_value = int(success_match.group(2))
        difficulty = int(success_match.group(3))
        return num_dice, dice_value, "", 0, "success", difficulty
    
    # Tentativa com rolagem normal
    base_match = re.match(base_pattern, notation)
    if base_match:
        num_dice = int(base_match.group(1))
        dice_value = int(base_match.group(2))
        advantage_type = base_match.group(3) if base_match.group(3) else ""
        modifier = int(base_match.group(4)) if base_match.group(4) else 0
        return num_dice, dice_value, advantage_type, modifier, "normal", 0
    
    return None

def roll_dice(num_dice, dice_value, advantage_type="", modifier=0, roll_type="normal", difficulty=0):
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
    
    if roll_type == "success":
        successes = sum(1 for roll in rolls if roll >= difficulty)
        return rolls, detailed_rolls, successes, difficulty
    else:
        total = sum(rolls) + modifier
        return rolls, detailed_rolls, total, modifier

def format_roll_result(notation, rolls, detailed_rolls, result, modifier_or_difficulty, roll_type="normal"):
    base_result = f"🎲 **{notation}**: ["
    base_result += ", ".join(detailed_rolls)
    base_result += "]"
    
    if roll_type == "success":
        difficulty = modifier_or_difficulty
        base_result += f" (CD {difficulty})"
        base_result += f" = **{result} sucessos**"
    else:
        modifier = modifier_or_difficulty
        if modifier != 0:
            base_result += f" {'+' if modifier > 0 else ''}{modifier}"
        base_result += f" = **{result}**"
    
    return base_result

@tree.command(name="rolld", description="Roll dice using standard notation (e.g. 3d6+2 or 5d10cd6)")
async def rolld(interaction, dice: str):
    result = process_dice_command(dice)
    if result:
        stats.increment_rolls()
        await update_presence()
        await interaction.response.send_message(result)
    else:
        await interaction.response.send_message("Notação de dados inválida. Use formatos como '3d6+2', '1d20adv' ou '5d10cd6'.")

@tree.command(name="stats", description="Mostra estatísticas do bot")
async def bot_stats(interaction):
    server_count = len(client.guilds)
    embed = discord.Embed(
        title="🎲 Estatísticas do RollDice",
        color=discord.Color.blue()
    )
    embed.add_field(name="Servidores", value=f"{server_count}", inline=True)
    embed.add_field(name="Total de Rolagens", value=f"{stats.total_rolls:,}", inline=True)
    
    await interaction.response.send_message(embed=embed)

def process_dice_command(dice_notation):
    dice_notation = dice_notation.lower().replace(" ", "")
    parsed = parse_dice_notation(dice_notation)
    
    if not parsed:
        return None
    
    num_dice, dice_value, advantage_type, modifier, roll_type, difficulty = parsed
    
    # Limit reasonable values to prevent abuse
    if num_dice > 100 or dice_value > 1000:
        return "Por favor, use valores razoáveis (máximo 100 dados com até 1000 lados)"
    
    if roll_type == "success":
        rolls, detailed_rolls, successes, difficulty = roll_dice(
            num_dice, dice_value, advantage_type, modifier, roll_type, difficulty
        )
        return format_roll_result(dice_notation, rolls, detailed_rolls, successes, difficulty, roll_type)
    else:
        rolls, detailed_rolls, total, modifier = roll_dice(
            num_dice, dice_value, advantage_type, modifier
        )
        return format_roll_result(dice_notation, rolls, detailed_rolls, total, modifier)

async def update_presence():
    server_count = len(client.guilds)
    activity = discord.Activity(
        type=discord.ActivityType.playing,
        name=f"🎲 em {server_count} servidores | {stats.total_rolls:,} rolagens"
    )
    await client.change_presence(activity=activity)

async def presence_updater():
    while True:
        await update_presence()
        await asyncio.sleep(300)  # Atualiza a cada 5 minutos

@client.event
async def on_ready():
    await tree.sync()
    print(f'{client.user} está conectado e pronto!')
    
    # Iniciar o loop de atualização de presença
    client.loop.create_task(presence_updater())
    await update_presence()

@client.event
async def on_guild_join(guild):
    # Atualiza a presença quando o bot entra em um novo servidor
    await update_presence()

@client.event
async def on_guild_remove(guild):
    # Atualiza a presença quando o bot sai de um servidor
    await update_presence()

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    content = message.content.strip()
    
    # Verifica se a mensagem contém apenas notação de dados sem prefixo de comando
    dice_pattern = r'^\d+d\d+([adv|dis]*)([+-]\d+)?$|^\d+d\d+cd\d+$'
    if re.match(dice_pattern, content):
        result = process_dice_command(content)
        if result:
            stats.increment_rolls()
            await update_presence()
            await message.channel.send(result)

client.run(TOKEN)