# RolldDice Discord Bot

A complete Discord bot for rolling dice in your RPG sessions with advanced features including modifiers, advantage/disadvantage rolls, and success counting.

## Features

- 🎲 Basic dice rolls (e.g., `3d6`, `1d20`)
- ➕ Modifier support (e.g., `1d20+5`, `2d8-3`)
- 🔄 Advantage and disadvantage rolls (e.g., `1d20adv`, `2d20dis`)
- ✅ Success counting for systems like World of Darkness (e.g., `5d10cd6`)
- 📊 Statistics tracking and monitoring
- 💬 Works both with slash commands and direct chat input

## Getting Started

### Prerequisites

- Python 3.8 or higher
- A Discord account and a registered Discord application/bot
- Administrative permissions on the Discord server where you want to add the bot

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/rolldice-discord-bot.git
   cd rolldice-discord-bot
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root directory with your Discord bot token:
   ```
   DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
   ```

   > ⚠️ **Security Note**: Never share your Discord token publicly or commit it to your repository.

4. Run the bot:
   ```bash
   python main.py
   ```

### Creating a Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give your bot a name
3. Navigate to the "Bot" tab and click "Add Bot"
4. Under the "TOKEN" section, click "Copy" to copy your bot's token
5. Enable "MESSAGE CONTENT INTENT" under the Privileged Gateway Intents section
6. Use this token in your `.env` file

### Adding the Bot to Your Server

1. Go to the "OAuth2" > "URL Generator" tab in the Discord Developer Portal
2. Select the "bot" scope and the following permissions:
   - Send Messages
   - Read Message History
   - Use Slash Commands
3. Copy the generated URL and open it in your browser
4. Select the server where you want to add the bot and authorize it

## Usage

### Rolling Dice

#### Basic Rolls
Roll dice using standard RPG notation:
- `/rolld 3d6` - Roll 3 six-sided dice
- `4d10` - Also works by simply typing in chat
- `/rolld 2d20` - Roll 2 twenty-sided dice
- `/rolld 1d100` - Roll 1 d100/percentile die

#### With Modifiers
Add bonuses or penalties to your rolls:
- `/rolld 1d20+5` - Roll 1d20 and add 5 to the result
- `2d8-3` - Roll 2d8 and subtract 3 from the result
- `/rolld 3d6+2` - Roll 3d6 and add 2 to the final result

#### Advantage and Disadvantage
Roll with advantage (best of two) or disadvantage (worst of two):
- `/rolld 1d20adv` - Roll 1d20 with advantage (roll twice, take the higher result)
- `2d20dis` - Roll 2d20 with disadvantage (roll twice for each die, take the lower result)
- `/rolld 1d20adv+4` - Combine advantage with modifiers

#### Success Counting
Count how many dice meet or exceed a difficulty class (DC):
- `/rolld 5d10cd6` - Roll 5d10 and count how many results are ≥ 6
- `7d8cd4` - Roll 7d8 and count how many results are ≥ 4
- `/rolld 10d6cd5` - Perfect for systems like World of Darkness

### Bot Commands

- `/rolld [dice]` - Roll dice using the specified notation
- `/stats` - Show bot statistics (number of servers and total rolls)
- `/ajuda` or `/help` - Display help information in Portuguese or English

## How It Works

The bot uses regular expressions to parse dice notation and process different types of rolls:

1. **Parsing**: The `parse_dice_notation()` function identifies the number of dice, dice sides, advantage/disadvantage, modifiers, and success counting parameters.

2. **Rolling**: The `roll_dice()` function generates random numbers based on the parsed parameters and calculates the final results.

3. **Formatting**: The `format_roll_result()` function creates a readable message showing the individual dice results and the final outcome.

4. **Statistics**: The bot tracks the total number of rolls made and displays this in its status message, which updates every 5 minutes.

## Limitations

- Maximum of 100 dice per roll
- Maximum of 1000 sides per die
- The bot does not support complex dice expressions like "2d6+1d8"

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Built with [discord.py](https://discordpy.readthedocs.io/)
- Thanks to the RPG community for inspiration

---

Made with ❤️ for RPG enthusiasts
