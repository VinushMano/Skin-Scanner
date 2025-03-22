@bot.command(name="skins")
async def skins(ctx, username: str):
    """Check a player's skins"""
    try:
        # Get player data
        player_data = await hypixel.get_player_skins(username)
        
        if not player_data:
            await ctx.send(f"❌ Could not find data for player: {username}")
            return
            
        if not player_data.get('api_enabled', False):
            await ctx.send("⚠️ Warning: Hypixel API is currently disabled. Some data may be incomplete.")
            
        # Create embed
        embed = discord.Embed(
            title=f"🎭 Skins for {player_data['username']}",
            color=discord.Color.blue()
        )
        
        # Add applied skins
        applied_skins = player_data['skins']['applied']
        if applied_skins:
            embed.add_field(
                name="Applied Skins",
                value="\n".join(f"• {skin}" for skin in applied_skins[:10]),
                inline=False
            )
            if len(applied_skins) > 10:
                embed.add_field(
                    name="More Applied Skins",
                    value=f"... and {len(applied_skins) - 10} more",
                    inline=False
                )
        else:
            embed.add_field(
                name="Applied Skins",
                value="No applied skins found",
                inline=False
            )
            
        # Add non-applied skins
        non_applied_skins = player_data['skins']['non_applied']
        if non_applied_skins:
            embed.add_field(
                name="Non-Applied Skins",
                value="\n".join(f"• {skin}" for skin in non_applied_skins[:10]),
                inline=False
            )
            if len(non_applied_skins) > 10:
                embed.add_field(
                    name="More Non-Applied Skins",
                    value=f"... and {len(non_applied_skins) - 10} more",
                    inline=False
                )
        else:
            embed.add_field(
                name="Non-Applied Skins",
                value="No non-applied skins found",
                inline=False
            )
            
        # Add login times if available
        if player_data['first_login'] > 0:
            first_login = datetime.fromtimestamp(player_data['first_login'] / 1000)
            embed.add_field(
                name="First Login",
                value=first_login.strftime("%Y-%m-%d %H:%M:%S"),
                inline=True
            )
            
        if player_data['last_login'] > 0:
            last_login = datetime.fromtimestamp(player_data['last_login'] / 1000)
            embed.add_field(
                name="Last Login",
                value=last_login.strftime("%Y-%m-%d %H:%M:%S"),
                inline=True
            )
            
        # Add total counts
        embed.set_footer(text=f"Total Applied: {len(applied_skins)} | Total Non-Applied: {len(non_applied_skins)}")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        print(f"Error in skins command: {e}")
        await ctx.send("❌ An error occurred while fetching skin data.") 