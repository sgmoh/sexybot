import discord
from discord.ext import commands
import logging
import json
import os
import asyncio
import datetime
import random
import platform
import time
from config import CONFIG

logger = logging.getLogger('discord_bot')

class Utility(commands.Cog):
    """Utility commands for server management and information"""
    
    def __init__(self, bot):
        self.bot = bot
        logger.info(f"Utility cog initialized")
    
    @commands.command(name="userinfo")
    async def userinfo(self, ctx, member: discord.Member = None):
        """Show information about a user"""
        # Default to the command invoker if no member specified
        member = member or ctx.author
        
        # Get join position
        join_position = sorted(ctx.guild.members, key=lambda m: m.joined_at or datetime.datetime.utcnow()).index(member) + 1
        
        # Create embed
        embed = discord.Embed(
            title=f"{member.name} User Information",
            color=member.color or CONFIG['colors']['info']
        )
        
        # Set user avatar as thumbnail
        embed.set_thumbnail(url=member.display_avatar.url)
        
        # Add user ID
        embed.add_field(
            name="🆔 User ID",
            value=member.id,
            inline=True
        )
        
        # Add nickname if exists
        if member.nick:
            embed.add_field(
                name="📝 Nickname",
                value=member.nick,
                inline=True
            )
        
        # Add account created date
        created_timestamp = int(member.created_at.timestamp())
        created_date = f"<t:{created_timestamp}:F>\n<t:{created_timestamp}:R>"
        
        embed.add_field(
            name="🔰 Account Created",
            value=created_date,
            inline=True
        )
        
        # Add server join date
        if member.joined_at:
            joined_timestamp = int(member.joined_at.timestamp())
            joined_date = f"<t:{joined_timestamp}:F>\n<t:{joined_timestamp}:R>"
            
            embed.add_field(
                name="📥 Joined Server",
                value=f"{joined_date}\n(#{join_position} to join)",
                inline=True
            )
        
        # Add status
        status_emojis = {
            discord.Status.online: "🟢 Online",
            discord.Status.idle: "🟡 Idle",
            discord.Status.dnd: "🔴 Do Not Disturb",
            discord.Status.offline: "⚫ Offline"
        }
        
        embed.add_field(
            name="📶 Status",
            value=status_emojis.get(member.status, "Unknown"),
            inline=True
        )
        
        # Add activity if available
        if member.activity:
            activity_type = {
                discord.ActivityType.playing: "Playing",
                discord.ActivityType.streaming: "Streaming",
                discord.ActivityType.listening: "Listening to",
                discord.ActivityType.watching: "Watching",
                discord.ActivityType.custom: "Custom Status",
                discord.ActivityType.competing: "Competing in"
            }
            
            activity_name = f"{activity_type.get(member.activity.type, 'Unknown')} {member.activity.name}"
            
            embed.add_field(
                name="🎮 Activity",
                value=activity_name,
                inline=True
            )
        
        # Add roles
        roles = [role.mention for role in reversed(member.roles) if role.name != "@everyone"]
        if roles:
            embed.add_field(
                name=f"👑 Roles ({len(roles)})",
                value=" ".join(roles) if len(" ".join(roles)) < 1024 else f"{len(roles)} roles",
                inline=False
            )
        
        # Add permissions if available
        key_permissions = {
            "administrator": "Administrator",
            "manage_guild": "Manage Server",
            "manage_roles": "Manage Roles",
            "manage_channels": "Manage Channels",
            "manage_messages": "Manage Messages",
            "manage_webhooks": "Manage Webhooks",
            "manage_nicknames": "Manage Nicknames",
            "manage_emojis": "Manage Emojis",
            "kick_members": "Kick Members",
            "ban_members": "Ban Members",
            "mention_everyone": "Mention Everyone"
        }
        
        permissions = []
        for perm, name in key_permissions.items():
            if getattr(member.guild_permissions, perm):
                permissions.append(name)
        
        if permissions:
            embed.add_field(
                name="🔑 Key Permissions",
                value=", ".join(permissions),
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="avatar")
    async def avatar(self, ctx, member: discord.Member = None):
        """Show a user's avatar"""
        # Default to the command invoker if no member specified
        member = member or ctx.author
        
        # Create embed
        embed = discord.Embed(
            title=f"{member.name}'s Avatar",
            color=member.color or CONFIG['colors']['info']
        )
        
        # Set avatar image
        embed.set_image(url=member.display_avatar.url)
        
        # Add links to different formats
        formats = ["png", "jpg", "webp"]
        if member.display_avatar.is_animated():
            formats.append("gif")
            
        links = [f"[{fmt.upper()}]({member.display_avatar.with_format(fmt).url})" for fmt in formats]
        
        embed.add_field(
            name="Download",
            value=" | ".join(links),
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="ping")
    async def ping(self, ctx):
        """Check the bot's latency"""
        # Calculate latency and format it
        latency = round(self.bot.latency * 1000)
        
        # Create embed
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Bot latency: **{latency}ms**",
            color=CONFIG['colors']['info']
        )
        
        # Add additional info if needed
        embed.add_field(
            name="API Latency",
            value=f"{latency}ms",
            inline=True
        )
        
        embed.add_field(
            name="Status",
            value="✅ Online" if latency < 300 else "⚠️ High Latency",
            inline=True
        )
        
        # Send the embed
        await ctx.send(embed=embed)
    
    @commands.command(name="channelinfo")
    async def channel_info(self, ctx, channel: discord.TextChannel = None):
        """Show information about a channel"""
        # Default to the current channel if none specified
        channel = channel or ctx.channel
        
        # Create embed
        embed = discord.Embed(
            title=f"#{channel.name} Channel Information",
            description=channel.topic or "No topic set",
            color=CONFIG['colors']['info']
        )
        
        # Add channel ID
        embed.add_field(
            name="🆔 Channel ID",
            value=channel.id,
            inline=True
        )
        
        # Add category
        embed.add_field(
            name="📁 Category",
            value=channel.category.name if channel.category else "None",
            inline=True
        )
        
        # Add creation date
        created_timestamp = int(channel.created_at.timestamp())
        created_date = f"<t:{created_timestamp}:F>\n<t:{created_timestamp}:R>"
        
        embed.add_field(
            name="📅 Created",
            value=created_date,
            inline=True
        )
        
        # Add position
        embed.add_field(
            name="📊 Position",
            value=channel.position,
            inline=True
        )
        
        # Add slowmode
        slowmode = channel.slowmode_delay
        if slowmode > 0:
            # Format slowmode (e.g. 5s, 1m, 1h)
            if slowmode < 60:
                slowmode_str = f"{slowmode}s"
            elif slowmode < 3600:
                slowmode_str = f"{slowmode // 60}m"
            else:
                slowmode_str = f"{slowmode // 3600}h"
        else:
            slowmode_str = "Off"
            
        embed.add_field(
            name="⏱️ Slowmode",
            value=slowmode_str,
            inline=True
        )
        
        # Add NSFW status
        embed.add_field(
            name="🔞 NSFW",
            value="Yes" if channel.is_nsfw() else "No",
            inline=True
        )
        
        # Add news status (if applicable)
        if hasattr(channel, 'is_news'):
            embed.add_field(
                name="📰 Announcement Channel",
                value="Yes" if channel.is_news() else "No",
                inline=True
            )
        
        # Add permission synced status
        if hasattr(channel, 'permissions_synced'):
            synced = await channel.permissions_synced() if callable(channel.permissions_synced) else channel.permissions_synced
            embed.add_field(
                name="🔄 Synced Permissions",
                value="Yes" if synced else "No",
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="emojis")
    async def emojis(self, ctx):
        """Show all emojis in the server"""
        try:
            # Parse dice format
            if 'd' not in dice:
                # Assume it's just the number of sides
                num_dice = 1
                num_sides = int(dice)
            else:
                num_dice, num_sides = map(int, dice.split('d'))
            
            # Validate inputs
            if num_dice <= 0 or num_sides <= 0:
                raise ValueError("Number of dice and sides must be positive")
                
            if num_dice > 100:
                raise ValueError("Cannot roll more than 100 dice at once")
                
            if num_sides > 1000:
                raise ValueError("Cannot roll dice with more than 1000 sides")
            
            # Roll the dice
            rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
            total = sum(rolls)
            
            # Create embed
            embed = discord.Embed(
                title="🎲 Dice Roll",
                description=f"Rolled {dice}",
                color=CONFIG['colors']['info']
            )
            
            # Add rolls
            if num_dice > 1:
                embed.add_field(
                    name="Rolls",
                    value=", ".join(str(r) for r in rolls),
                    inline=False
                )
                
                embed.add_field(
                    name="Total",
                    value=total,
                    inline=False
                )
            else:
                embed.add_field(
                    name="Result",
                    value=total,
                    inline=False
                )
            
            await ctx.send(embed=embed)
            
        except ValueError as e:
            # Invalid format
            embed = discord.Embed(
                title="❌ Invalid Dice Format",
                description=f"Error: {str(e)}\nUse format 'NdN' like '1d6', '2d20', etc.",
                color=CONFIG['colors']['error']
            )
            
            await ctx.send(embed=embed)
    
    @commands.command(name="choose")
    async def choose(self, ctx, *options):
        """Choose between multiple options"""
        # Check if enough options were provided
        if len(options) < 2:
            embed = discord.Embed(
                title="❌ Not Enough Options",
                description="Please provide at least 2 options to choose from.",
                color=CONFIG['colors']['error']
            )
            
            await ctx.send(embed=embed)
            return
        
        # Choose a random option
        choice = random.choice(options)
        
        # Create embed
        embed = discord.Embed(
            title="🤔 Choice Made",
            description=f"I choose: **{choice}**",
            color=CONFIG['colors']['success']
        )
        
        embed.add_field(
            name="Options",
            value="\n".join(f"• {option}" for option in options),
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="remind")
    async def remind(self, ctx, time: str, *, reminder: str):
        """Set a reminder"""
        # Parse time
        seconds = 0
        time_units = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400
        }
        
        try:
            unit = time[-1].lower()
            value = int(time[:-1])
            
            if unit in time_units:
                seconds = value * time_units[unit]
            else:
                seconds = int(time)  # Try to parse as seconds
                
            if seconds < 1 or seconds > 86400 * 7:  # Between 1 second and 7 days
                raise ValueError("Invalid time")
                
        except:
            embed = discord.Embed(
                title="❌ Invalid Time",
                description="Please specify a valid time (e.g. 10s, 5m, 1h, 1d).",
                color=CONFIG['colors']['error']
            )
            await ctx.send(embed=embed)
            return
        
        # Calculate when the reminder will be triggered
        now = datetime.datetime.utcnow()
        remind_time = now + datetime.timedelta(seconds=seconds)
        
        # Format times
        timestamp = int(remind_time.timestamp())
        remind_time_str = f"<t:{timestamp}:F>"
        relative_time = f"<t:{timestamp}:R>"
        
        # Create confirmation embed
        embed = discord.Embed(
            title="⏰ Reminder Set",
            description=f"I'll remind you about: **{reminder}**",
            color=CONFIG['colors']['success']
        )
        
        embed.add_field(
            name="When",
            value=f"{remind_time_str}\n{relative_time}",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
        # Wait for the specified time
        await asyncio.sleep(seconds)
        
        # Create reminder embed
        reminder_embed = discord.Embed(
            title="⏰ Reminder",
            description=reminder,
            color=CONFIG['colors']['info'],
            timestamp=now  # When the reminder was set
        )
        
        reminder_embed.add_field(
            name="Reminder Set",
            value=f"{seconds_to_time_string(seconds)} ago",
            inline=False
        )
        
        # Send the reminder
        try:
            await ctx.author.send(f"{ctx.author.mention} Here's your reminder!", embed=reminder_embed)
            
            # If the reminder was set in a guild, also send a message there
            if ctx.guild:
                await ctx.send(f"{ctx.author.mention} I've sent your reminder to your DMs!")
                
        except discord.Forbidden:
            # Can't DM the user
            if ctx.guild:
                await ctx.send(f"{ctx.author.mention} Here's your reminder!", embed=reminder_embed)
            
        except Exception as e:
            logger.error(f"Error sending reminder: {e}")
            if ctx.guild:
                await ctx.send(f"{ctx.author.mention} I tried to send your reminder, but something went wrong.")

def seconds_to_time_string(seconds):
    """Convert seconds to a human-readable time string"""
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds > 0:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
    
    return ", ".join(parts)

async def setup(bot):
    await bot.add_cog(Utility(bot))