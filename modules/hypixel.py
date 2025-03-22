import aiohttp
from typing import Optional, Dict, Any
import config
import json
import time

class HypixelAPI:
    def __init__(self):
        self.api_key = config.HYPIXEL_API_KEY
        self.base_url = config.HYPIXEL_API_BASE
        self.headers = {
            "API-Key": self.api_key,
            "User-Agent": config.USER_AGENT
        }
        self.cache = {}
        self.cache_duration = 60  # Assuming a default cache duration

    async def get_player_skins(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get all skins owned by a player from Hypixel API
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                # First get the player's UUID
                uuid_data = await self.ensure_data(f"/users/profiles/minecraft/{username}", {}, session=session)
                if not uuid_data:
                    print(f"Could not find UUID for username: {username}")
                    return None
                uuid = uuid_data.get("id")
                if not uuid:
                    print(f"No UUID found in response for username: {username}")
                    return None

                # Get SkyBlock profiles
                profiles_data = await self.ensure_data('/skyblock/profiles', {"uuid": uuid}, session=session)
                if not profiles_data:
                    print(f"No profiles data found for UUID: {uuid}")
                    return None
                if not profiles_data.get('profiles'):
                    print(f"No SkyBlock profiles found for UUID: {uuid}")
                    return None

                # Get museum data for all profiles in parallel
                museum_tasks = []
                for profile in profiles_data['profiles']:
                    museum_data = await self.ensure_data('/skyblock/museum', {"profile": profile['profile_id']}, session=session)
                    if museum_data:
                        museum_tasks.append(museum_data)

                # Collect all items and skins
                items = {}
                applied_items = []
                non_applied_items = []
                first_login = None
                last_login = None

                # Process each profile
                for profile in profiles_data['profiles']:
                    # Get member data
                    member_data = profile['members'].get(uuid, {})
                    
                    # Update login times
                    member_first_login = member_data.get('firstLogin')
                    member_last_login = member_data.get('lastLogin')
                    
                    if member_first_login and (first_login is None or member_first_login < first_login):
                        first_login = member_first_login
                    if member_last_login and (last_login is None or member_last_login > last_login):
                        last_login = member_last_login
                    
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
                                # Check for non-applied skins in item name
                                if 'skin' in item.get('name', '').lower():
                                    non_applied_items.append(item['name'])

                # Check museum items
                for museum_data in museum_tasks:
                    for item in museum_data.get('items', []):
                        if not item.get('ExtraAttributes', {}).get('uuid'):
                            continue
                        items[item['ExtraAttributes']['uuid']] = item
                        if item.get('ExtraAttributes', {}).get('skin'):
                            applied_items.append(item['ExtraAttributes']['skin'])
                        # Check for non-applied skins in item name
                        if 'skin' in item.get('name', '').lower():
                            non_applied_items.append(item['name'])

                # Remove duplicates
                applied_items = list(set(applied_items))
                non_applied_items = list(set(non_applied_items))

                # Check if API is enabled
                api_status = await self.ensure_data('/status', {}, session=session)
                api_enabled = api_status.get('success', False) if api_status else False

                return {
                    "username": username,
                    "uuid": uuid,
                    "skins": {
                        "applied": applied_items,
                        "non_applied": non_applied_items
                    },
                    "last_login": last_login or 0,
                    "first_login": first_login or 0,
                    "api_enabled": api_enabled
                }

            except Exception as e:
                print(f"Error fetching player data: {e}")
                return None 

    async def ensure_data(self, endpoint: str, params: Dict[str, Any], session: aiohttp.ClientSession) -> Optional[Dict[str, Any]]:
        """
        Ensure we have data for an endpoint, using cache if available
        """
        # Create cache key from endpoint and params
        cache_key = f"{endpoint}:{json.dumps(params, sort_keys=True)}"
        
        # Check cache first
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry['timestamp'] < self.cache_duration:
                return cache_entry['data']
        
        # If not in cache or expired, fetch from API
        try:
            # Handle Mojang API endpoint differently
            if endpoint.startswith('/users/profiles/minecraft/'):
                url = f"{config.MOJANG_API_BASE}{endpoint}"
            else:
                url = f"{self.base_url}{endpoint}"
                
            async with session.get(url, params=params) as response:
                if response.status == 429:
                    print(f"Rate limit hit for endpoint: {endpoint}")
                    return None
                if response.status != 200:
                    print(f"Error {response.status} for endpoint: {endpoint}")
                    return None
                    
                data = await response.json()
                
                # Cache the response
                self.cache[cache_key] = {
                    'data': data,
                    'timestamp': time.time()
                }
                
                return data
                
        except Exception as e:
            print(f"Error fetching data from {endpoint}: {e}")
            return None 