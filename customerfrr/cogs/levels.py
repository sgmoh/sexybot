import discord
from discord.ext import commands
import random
import logging
import datetime
import json
import os
from utils.helpers import Helpers
from utils.data_manager import DataManager
from utils.embed_creator import EmbedCreator
from config import CONFIG

logger = logging.getLogger('discord_bot')

class Levels(commands.Cog):
    """Level tracking system"""
        if member is None:
            member = ctx.author
            
        # Get user data
        user_key = f"user_{ctx.guild.id}_{member.id}"
        user_data = await self.data_manager.get(user_key, {'xp': 0, 'level': 0, 'messages': 0})
        
        xp = user_data.get('xp', 0)
        level = user_data.get('level', 0)
        messages = user_data.get('messages', 0)
        
        # Calculate XP for next level
        next_level_xp = Helpers.get_xp_for_level(level + 1)
        current_level_xp = Helpers.get_xp_for_level(level)
        
        # Calculate progress to next level
        xp_needed = next_level_xp - current_level_xp
        xp_progress = xp - current_level_xp
        
        # Calculate percentage
        progress_percentage = min(100, int((xp_progress / max(1, xp_needed)) * 100))
        
        # Create progress bar
        bar_length = 20
        filled_blocks = int(bar_length * progress_percentage / 100)
        progress_bar = "█" * filled_blocks + "░" * (bar_length - filled_blocks)
        
        # Create embed
        embed = discord.Embed(
            title=f"{member.display_name}'s Level Stats",
            description=f"**Level:** {level}\n**XP:** {xp}/{next_level_xp}\n**Messages:** {messages}",
            color=CONFIG['colors']['default'],
            timestamp=datetime.datetime.utcnow()
        )
        
        # Add progress bar
        embed.add_field(
            name=f"Progress to Level {level+1}",
            value=f"`{progress_bar}` {progress_percentage}%",
            inline=False
        )
        
        # Set thumbnail to member avatar
        embed.set_thumbnail(url=member.display_avatar.url)
        
        # Set footer
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="leaderboard", aliases=["lb", "top"])
    async def leaderboard(self, ctx, type: str = "levels"):
        """Show the server leaderboard"""
        if type.lower() not in ["levels", "messages", "invites"]:
            type = "levels"  # Default to levels
            
        # Get all data
        all_data = await self.data_manager.get_all()
        
        # Filter users from this guild
        guild_users = []
        for key, data in all_data.items():
            if key.startswith(f"user_{ctx.guild.id}_"):
                try:
                    user_id = int(key.split('_')[2])
                    
                    if type.lower() == "levels":
                        value = data.get('level', 0)
                        secondary = data.get('xp', 0)
                    elif type.lower() == "messages":
                        value = data.get('messages', 0)
                        secondary = 0
                    # Invites are handled by a different cog
                    else:
                        continue
                        
                    guild_users.append({
                        'user_id': user_id,
                        'value': value,
                        'secondary': secondary
                    })
                except (IndexError, ValueError):
                    continue
        
        # Sort users by value (descending)
        guild_users.sort(key=lambda x: (x['value'], x['secondary']), reverse=True)
        
        # Take top 10
        top_users = guild_users[:10]
        
        if not top_users:
            await ctx.send(f"No data available for the {type} leaderboard.")
            return
            
        # Create embed
        embed = discord.Embed(
            title=f"{type.title()} Leaderboard",
            description=f"Top members in {ctx.guild.name}",
            color=CONFIG['colors']['default'],
            timestamp=datetime.datetime.utcnow()
        )
        
        # Format leaderboard entries
        lb_text = ""
        for i, user_data in enumerate(top_users):
            user_id = user_data['user_id']
            value = user_data['value']
            
            # Get medal emoji based on position
            if i == 0:
                medal = "🥇"
            elif i == 1:
                medal = "🥈"
            elif i == 2:
                medal = "🥉"
            else:
                medal = f"`{i+1}.`"
                
            lb_text += f"{medal} <@{user_id}> - **{value}**\n"
            
        embed.add_field(name="Rankings", value=lb_text, inline=False)
        
        # Set footer
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.group(name="leveling", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def leveling(self, ctx):
        """Manage leveling system settings"""
        guild_key = f"guild_{ctx.guild.id}"
        guild_settings = await self.data_manager.get(guild_key, {})
        
        # Check if resetting to default
        if isinstance(channel, str) and channel.lower() == "reset":
            if 'level_up_channel_id' in guild_settings:
                del guild_settings['level_up_channel_id']
                
            embed = discord.Embed(
                title="ℹ️ Level-Up Channel Reset",
                description="Level-up messages will now be sent in the same channel where the message was sent.",
                color=CONFIG['colors']['info']
            )
        elif channel:
            # Set new channel
            guild_settings['level_up_channel_id'] = channel.id
            
            embed = discord.Embed(
                title="✅ Level-Up Channel Set",
                description=f"Level-up messages will now be sent in {channel.mention}.",
                color=CONFIG['colors']['success']
            )
        else:
            # Show current setting
            current_channel_id = guild_settings.get('level_up_channel_id')
            current_channel = ctx.guild.get_channel(current_channel_id) if current_channel_id else None
            
            if current_channel:
                description = f"Level-up messages are currently sent in {current_channel.mention}."
            else:
                description = "Level-up messages are currently sent in the same channel where the message was sent."
                
            embed = discord.Embed(
                title="ℹ️ Level-Up Channel",
                description=description,
                color=CONFIG['colors']['info']
            )
            
            # Add usage example
            embed.add_field(
                name="Usage",
                value=f"`{CONFIG['prefix']}leveling channel #channel` - Set a specific channel\n"
                     f"`{CONFIG['prefix']}leveling channel reset` - Use message channel (default)",
                inline=False
            )
            
            await ctx.send(embed=embed)
            return
            
        # Save settings
        await self.data_manager.set(guild_key, guild_settings)
        
        # Send confirmation
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Levels(bot))