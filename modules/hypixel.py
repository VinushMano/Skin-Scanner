import aiohttp
from typing import Optional, Dict, Any, List
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
                    
                    # Get all items with skins
                    skins = []
                    
                    # Check wardrobe
                    wardrobe = player_data.get("wardrobe", {})
                    for wardrobe_item in wardrobe.values():
                        if isinstance(wardrobe_item, dict):
                            item_data = wardrobe_item.get("data", {})
                            if "skin" in item_data:
                                skins.append({
                                    "name": item_data.get("name", "Unknown Item"),
                                    "skin": item_data["skin"],
                                    "location": "Wardrobe"
                                })

                    # Check backpacks
                    backpacks = player_data.get("backpack_contents", {})
                    for backpack in backpacks.values():
                        if isinstance(backpack, dict):
                            items = backpack.get("data", {}).get("items", [])
                            for item in items:
                                if isinstance(item, dict) and "skin" in item:
                                    skins.append({
                                        "name": item.get("name", "Unknown Item"),
                                        "skin": item["skin"],
                                        "location": "Backpack"
                                    })

                    # Check enderchest
                    enderchest = player_data.get("enderchest_contents", {}).get("data", {}).get("items", [])
                    for item in enderchest:
                        if isinstance(item, dict) and "skin" in item:
                            skins.append({
                                "name": item.get("name", "Unknown Item"),
                                "skin": item["skin"],
                                "location": "Enderchest"
                            })

                    # Check vault
                    vault = player_data.get("vault_contents", {}).get("data", {}).get("items", [])
                    for item in vault:
                        if isinstance(item, dict) and "skin" in item:
                            skins.append({
                                "name": item.get("name", "Unknown Item"),
                                "skin": item["skin"],
                                "location": "Vault"
                            })

                    # Check equipped armor
                    armor = player_data.get("armor", {})
                    for armor_item in armor.values():
                        if isinstance(armor_item, dict) and "skin" in armor_item:
                            skins.append({
                                "name": armor_item.get("name", "Unknown Item"),
                                "skin": armor_item["skin"],
                                "location": "Equipped"
                            })

                    return {
                        "username": username,
                        "uuid": uuid,
                        "skins": skins,
                        "last_login": player_data.get("lastLogin"),
                        "first_login": player_data.get("firstLogin")
                    }

            except Exception as e:
                print(f"Error fetching player data: {e}")
                return None 