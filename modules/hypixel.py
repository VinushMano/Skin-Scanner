import aiohttp
from typing import Optional, Dict, Any
import config

class HypixelAPI:
    def __init__(self):
        self.api_key = config.HYPIXEL_API_KEY
        self.base_url = config.HYPIXEL_API_BASE
        self.headers = {
            "API-Key": self.api_key,
            "User-Agent": config.USER_AGENT
        }

    async def get_player_skins(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get all skins owned by a player from Hypixel API
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                # First get the player's UUID
                async with session.get(f"{config.MOJANG_API_BASE}/{username}") as response:
                    if response.status != 200:
                        return None
                    uuid_data = await response.json()
                    uuid = uuid_data.get("id")

                # Then get their Hypixel data
                async with session.get(f"{self.base_url}/player?uuid={uuid}") as response:
                    if response.status == 429:
                        return {"error": "rate_limit"}
                    if response.status != 200:
                        return None
                    
                    data = await response.json()
                    if not data.get("success"):
                        return None

                    player_data = data.get("player", {})
                    return {
                        "username": username,
                        "uuid": uuid,
                        "skins": player_data.get("skins", []),
                        "last_login": player_data.get("lastLogin"),
                        "first_login": player_data.get("firstLogin")
                    }

            except Exception as e:
                print(f"Error fetching player data: {e}")
                return None 