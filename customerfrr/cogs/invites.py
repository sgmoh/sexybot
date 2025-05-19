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
