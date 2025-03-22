import aiohttp
from typing import Optional, Dict, Any, List, Tuple
import config
import json
import asyncio

class HypixelAPI:
    def __init__(self):
        self.api_key = config.HYPIXEL_API_KEY
        self.base_url = config.HYPIXEL_API_BASE
        self.headers = {
            "API-Key": self.api_key,
            "User-Agent": config.USER_AGENT
        }

    async def ensure_data(self, endpoint: str, params: dict, session: Optional[aiohttp.ClientSession] = None) -> Optional[dict]:
        """Get data from Hypixel API with retries"""
        if session is None:
            session = aiohttp.ClientSession(headers=self.headers)
        
        while True:
            async with session.get(f"{self.base_url}{endpoint}", params=params) as response:
                if response.status == 429:  # Rate limit
                    await asyncio.sleep(1)
                    continue
                if response.status != 200:
                    return None
                return await response.json()

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

                # Get SkyBlock profiles
                profiles_data = await self.ensure_data('/skyblock/profiles', {"uuid": uuid}, session=session)
                if not profiles_data or not profiles_data.get('profiles'):
                    return None

                # Get museum data for all profiles
                museum_datas = await asyncio.gather(*[
                    self.ensure_data('/skyblock/museum', {"profile": profile['profile_id']}, session=session)
                    for profile in profiles_data['profiles']
                ])

                # Collect all items and skins
                items = {}
                applied_items = []

                # Process each profile
                for profile in profiles_data['profiles']:
                    # Get member data
                    member_data = profile['members'].get(uuid, {})
                    
                    # Check pets for skins
                    for pet in member_data.get('pets_data', {}).get('pets', []):
                        if pet.get('skin'):
                            applied_items.append('PET_SKIN_' + pet['skin'])

                    # Check inventory items
                    for inventory_type in ['inventory', 'ender_chest_contents', 'backpack_contents', 'vault_contents']:
                        if inventory_type in member_data:
                            items_data = member_data[inventory_type].get('data', {}).get('items', [])
                            for item in items_data:
                                if not item.get('ExtraAttributes', {}).get('uuid'):
                                    continue
                                items[item['ExtraAttributes']['uuid']] = item
                                if item.get('ExtraAttributes', {}).get('skin'):
                                    applied_items.append(item['ExtraAttributes']['skin'])

                # Check museum items
                for museum_data in museum_datas:
                    if not museum_data:
                        continue
                    for item in museum_data.get('items', []):
                        if not item.get('ExtraAttributes', {}).get('uuid'):
                            continue
                        items[item['ExtraAttributes']['uuid']] = item
                        if item.get('ExtraAttributes', {}).get('skin'):
                            applied_items.append(item['ExtraAttributes']['skin'])

                # Remove duplicates
                applied_items = list(set(applied_items))

                return {
                    "username": username,
                    "uuid": uuid,
                    "skins": applied_items,
                    "last_login": member_data.get('lastLogin'),
                    "first_login": member_data.get('firstLogin')
                }

            except Exception as e:
                print(f"Error fetching player data: {e}")
                return None 