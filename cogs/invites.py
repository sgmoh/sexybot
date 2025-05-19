import discord
from discord.ext import commands
import logging
from datetime import datetime, timedelta

from utils.database import db
from utils.embed_creator import EmbedCreator
from config import CONFIG

logger = logging.getLogger('discord_bot')

class Invites(commands.Cog):
    """Invite tracking system"""
    def __init__(self, bot):
        self.bot = bot
        logger.info(f"Invites cog initialized")
    
    @commands.command(name="unknown_method")
    @commands.has_permissions(manage_guild=True)
    async def unknown_method(self, ctx, *args):
        """Auto-generated method from fixing indentation"""

        # Default to command author if no member specified
        if member is None:
            member = ctx.author
        
        # Get invite stats
        stats = db.get_invite_stats(ctx.guild.id, member.id)
        
        # Create embed
        embed = EmbedCreator.create_invite_stats_embed(member, stats)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Invites(bot))
