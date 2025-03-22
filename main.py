import disnake
from disnake.ext import commands
import config
from modules.hypixel import HypixelAPI

# Initialize bot with required intents
bot = commands.InteractionBot(
    intents=disnake.Intents(
        guilds=True,
        guild_messages=True,
        message_content=True,
        members=True
    )
)

# Initialize Hypixel API client
hypixel = HypixelAPI()

@bot.event
async def on_ready():
    print(f"Bot is ready! Logged in as {bot.user}")

@bot.slash_command(
    name="skins",
    description="Check what skins a Minecraft player owns"
)
async def check_skins(
    inter: disnake.ApplicationCommandInteraction,
    username: str = commands.Param(description="The Minecraft username to check")
):
    await inter.response.defer()

    # Get player data
    player_data = await hypixel.get_player_skins(username)
    
    if not player_data:
        await inter.followup.send(config.ERROR_MESSAGES["invalid_username"])
        return
    
    if "error" in player_data:
        await inter.followup.send(config.ERROR_MESSAGES[player_data["error"]])
        return

    # Create embed
    embed = disnake.Embed(
        title=f"Skins for {player_data['username']}",
        color=disnake.Color.blue()
    )

    # Add player info
    embed.add_field(
        name="Player Info",
        value=f"UUID: `{player_data['uuid']}`\n"
              f"First Login: <t:{player_data['first_login']//1000}:R>\n"
              f"Last Login: <t:{player_data['last_login']//1000}:R>",
        inline=False
    )

    # Add skins
    skins = player_data.get("skins", [])
    if not skins:
        embed.add_field(
            name="Skins",
            value=config.ERROR_MESSAGES["no_skins"],
            inline=False
        )
    else:
        # Group skins by location
        skins_by_location = {}
        for skin in skins:
            location = skin.get("location", "Unknown")
            if location not in skins_by_location:
                skins_by_location[location] = []
            skins_by_location[location].append(skin)

        # Add each location's skins to the embed
        for location, location_skins in skins_by_location.items():
            skins_text = ""
            for skin in location_skins:
                skins_text += f"• {skin.get('name', 'Unknown Item')}\n"
            embed.add_field(
                name=f"Skins in {location}",
                value=skins_text or "No skins found",
                inline=False
            )

    await inter.followup.send(embed=embed)

# Run the bot
if __name__ == "__main__":
    bot.run(config.BOT_TOKEN) 