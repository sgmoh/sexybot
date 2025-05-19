import discord
from discord.ext import commands
import logging
import json
import os
from config import CONFIG

logger = logging.getLogger('discord_bot')

class Welcome(commands.Cog):
    """Welcome message system for new members"""
    
    def __init__(self, bot):
        self.bot = bot
        self.welcome_settings = {}
        self.load_welcome_settings()
        logger.info("Welcome cog initialized")
        
    def load_welcome_settings(self):
        """Load welcome settings from file"""
        try:
            with open('data/welcome_settings.json', 'r') as f:
                self.welcome_settings = json.load(f)
        except FileNotFoundError:
            self.welcome_settings = {}
            # Create the file
            self.save_welcome_settings()
        except Exception as e:
            logger.error(f"Error loading welcome settings: {e}")
            self.welcome_settings = {}
            
    def save_welcome_settings(self):
        """Save welcome settings to file"""
        try:
            os.makedirs('data', exist_ok=True)
            with open('data/welcome_settings.json', 'w') as f:
                json.dump(self.welcome_settings, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving welcome settings: {e}")
            
    @commands.command(name="welcome")
    @commands.has_permissions(manage_guild=True)
    async def welcome_command(self, ctx, channel: discord.TextChannel = None):
        """Set up welcome messages in a channel"""
        guild_id = str(ctx.guild.id)
        
        # Default to the current channel if none specified
        channel = channel or ctx.channel
        
        # Get or create settings for this guild
        if guild_id not in self.welcome_settings:
            self.welcome_settings[guild_id] = {
                'enabled': True,
                'channel_id': str(channel.id),
                'message': f"Welcome {{member}} to the server! We're glad to have you here."
            }
        else:
            self.welcome_settings[guild_id]['channel_id'] = str(channel.id)
            
        # Save updated settings
        self.save_settings()
        
        embed = discord.Embed(
            title="✅ Welcome Channel Set",
            description=f"Welcome messages will now be sent to {channel.mention}.",
            color=CONFIG['colors']['success']
        )
        
        # Enable welcome messages if they're not already
        if not self.welcome_settings[guild_id].get('enabled', False):
            self.welcome_settings[guild_id]['enabled'] = True
            self.save_settings()
            
            embed.add_field(
                name="ℹ️ Welcome Messages Enabled",
                value="Welcome messages have been automatically enabled.",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="welcomemessage")
    @commands.has_permissions(manage_guild=True)
    async def welcome_message(self, ctx, *, message):
        """Set the welcome message"""
        guild_id = str(ctx.guild.id)
        
        # Get or create settings for this guild
        if guild_id not in self.welcome_settings:
            self.welcome_settings[guild_id] = {
                'enabled': True,
                'channel_id': None,
                'message': message
            }
        else:
            self.welcome_settings[guild_id]['message'] = message
            
        # Save updated settings
        self.save_settings()
        
        embed = discord.Embed(
            title="✅ Welcome Message Set",
            description="Your custom welcome message has been saved.",
            color=CONFIG['colors']['success']
        )
        
        embed.add_field(
            name="Message Preview",
            value=message.replace('{member}', ctx.author.mention),
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Available Tags",
            value="`{member}` - Mentions the new member",
            inline=False
        )
        
        # Check if welcome channel is set
        if not self.welcome_settings[guild_id].get('channel_id'):
            embed.add_field(
                name="⚠️ Channel Not Set",
                value=f"Please set a welcome channel with `{CONFIG['prefix']}welcome channel #channel`",
                inline=False
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))