# Minecraft Skin Checker Bot

A Discord bot that checks what skins a Minecraft player owns using the Hypixel API.

## Features

- Check what skins a Minecraft player owns
- View player information including UUID and login dates
- Clean and organized Discord embed responses
- Rate limit handling
- Error handling for invalid usernames

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with the following variables:
   ```
   BOT_TOKEN=your_discord_bot_token
   HYPIXEL_API_KEY=your_hypixel_api_key
   ```
4. Add your Discord user ID to the `BOT_OWNERS` set in `config.py`
5. Run the bot:
   ```bash
   python main.py
   ```

## Usage

Use the `/skins` slash command followed by a Minecraft username to check their skins:
```
/skins username:PlayerName
```

## Requirements

- Python 3.8 or higher
- Discord Bot Token
- Hypixel API Key
- Required Python packages (listed in requirements.txt) 