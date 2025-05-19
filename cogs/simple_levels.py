import discord
from discord.ext import commands
import random
import json
import os
import logging
import math
from datetime import datetime

# Set up logging
logger = logging.getLogger('discord_bot')

class SimpleLevel:
    def __init__(self, user_id, xp=0, level=0, messages=0):
        self.user_id = user_id
        self.xp = xp
        self.level = level
        self.messages = messages
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "xp": self.xp,
            "level": self.level,
            "messages": self.messages
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            user_id=data.get("user_id", 0),
            xp=data.get("xp", 0),
            level=data.get("level", 0),
            messages=data.get("messages", 0)
        )

class SimpleLevels(commands.Cog):
    """Level tracking system with dedicated notification channel"""
    def __init__(self, bot):
        self.bot = bot
        logger.info(f"SimpleLevels cog initialized")
    
    @commands.command(name="unknown_method")
    @commands.has_permissions(manage_guild=True)
    async def unknown_method(self, ctx, *args):
        """Auto-generated method from fixing indentation"""

        # Use command invoker if no member specified
        if not member:
            member = ctx.author
            
        # Get user data
        user_data = self.get_user_data(ctx.guild.id, member.id)
        
        # Calculate progress to next level
        current_level_xp = self.get_xp_for_level(user_data.level)
        next_level_xp = self.get_xp_for_level(user_data.level + 1)
        xp_progress = user_data.xp - current_level_xp
        xp_needed = next_level_xp - current_level_xp
        
        # Calculate percentage (avoid division by zero)
        if xp_needed == 0:
            percentage = 100
        else:
            percentage = int((xp_progress / xp_needed) * 100)
            
        # Create progress bar
        bar_length = 20
        filled_blocks = int(bar_length * percentage / 100)
        progress_bar = "█" * filled_blocks + "░" * (bar_length - filled_blocks)
        
        # Create embed
        embed = discord.Embed(
            title=f"{member.display_name}'s Level Stats",
            description=f"**Level:** {user_data.level}\n**XP:** {user_data.xp}/{next_level_xp}\n**Messages:** {user_data.messages}",
            color=0x5865F2,
            timestamp=datetime.utcnow()
        )
        
        # Add progress bar
        embed.add_field(
            name=f"Progress to Level {user_data.level + 1}",
            value=f"`{progress_bar}` {percentage}%",
            inline=False
        )
        
        # Set thumbnail to member avatar
        embed.set_thumbnail(url=member.display_avatar.url)
        
        # Set footer
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="leaderboard", aliases=["lb", "top"])
    async def leaderboard_command(self, ctx, type="level"):
        """Show the server leaderboard"""
        guild_id = ctx.guild.id
        guild_data_file = f"data/guild_{guild_id}_levels.json"
        
        if not os.path.exists(guild_data_file):
            await ctx.send("No leveling data found for this server.")
            return
            
        try:
            with open(guild_data_file, 'r') as f:
                data = json.load(f)
                
            # Convert to list of user data objects
            users = [SimpleLevel.from_dict({**user_data, "user_id": int(user_id)}) 
                    for user_id, user_data in data.items()]
            
            # Sort based on type
            if type.lower() in ["message", "messages", "msg"]:
                users.sort(key=lambda x: x.messages, reverse=True)
                title = "Messages Leaderboard"
                value_key = "messages"
            else:
                # Sort by level and then by XP
                users.sort(key=lambda x: (x.level, x.xp), reverse=True)
                title = "Levels Leaderboard"
                value_key = "level"
            
            # Take top 10
            top_users = users[:10]
            
            # Create embed
            embed = discord.Embed(
                title=title,
                description=f"Top members in {ctx.guild.name}",
                color=0x5865F2,
                timestamp=datetime.utcnow()
            )
            
            # Generate leaderboard text
            lb_text = ""
            for i, user in enumerate(top_users):
                # Get medal emoji based on position
                if i == 0:
                    medal = "🥇"
                elif i == 1:
                    medal = "🥈"
                elif i == 2:
                    medal = "🥉"
                else:
                    medal = f"`{i+1}.`"
                    
                value = getattr(user, value_key)
                lb_text += f"{medal} <@{user.user_id}> - **{value}**\n"
                
            # Add leaderboard text to embed
            if lb_text:
                embed.add_field(name="Rankings", value=lb_text, inline=False)
            else:
                embed.add_field(name="No Data", value="No users have gained XP yet.", inline=False)
                
            # Set footer
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error retrieving leaderboard: {e}")
            await ctx.send("An error occurred while generating the leaderboard.")
    
    @commands.group(name="levelchannel", invoke_without_command=True)
    @commands.has_permissions(manage_channels=True)
    async def level_channel(self, ctx):
        """Configure the channel for level-up notifications"""
        # Save the channel
        guild_id = str(ctx.guild.id)
        self.level_up_channels[guild_id] = channel.id
        self.save_data()
        
        # Send confirmation
        embed = discord.Embed(
            title="✅ Level-Up Channel Set",
            description=f"Level-up notifications will now be sent to {channel.mention}.",
            color=0x57F287
        )
        
        await ctx.send(embed=embed)
    
    @level_channel.command(name="reset")
    @commands.has_permissions(manage_channels=True)
    async def level_channel_reset(self, ctx):
        """Reset to use the message channel for level-up notifications"""
        guild_id = str(ctx.guild.id)
        
        # Remove the channel setting
        if guild_id in self.level_up_channels:
            del self.level_up_channels[guild_id]
            self.save_data()
            
        # Send confirmation
        embed = discord.Embed(
            title="ℹ️ Level-Up Channel Reset",
            description="Level-up notifications will now be sent in the same channel where the message was sent.",
            color=0x3498DB
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SimpleLevels(bot))