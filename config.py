import os
from typing import Any
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
HYPIXEL_API_KEY = os.getenv('HYPIXEL_API_KEY')

# API Endpoints
HYPIXEL_API_BASE = "https://api.hypixel.net/v2"
MOJANG_API_BASE = "https://api.mojang.com/users/profiles/minecraft"

# User Agent for API requests
USER_AGENT = "SkinCheckerBot"

# Bot Owners (Discord User IDs)
BOT_OWNERS = set()  # Add your Discord ID here

# Error Messages
ERROR_MESSAGES = {
    "invalid_username": "Invalid Minecraft username provided.",
    "api_error": "An error occurred while fetching data from the API.",
    "no_skins": "No skins found for this player.",
    "rate_limit": "API rate limit reached. Please try again later."
} 