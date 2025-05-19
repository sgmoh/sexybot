import discord
from discord.ext import commands, tasks
import asyncio
import random
import logging
import re
from datetime import datetime, timedelta

from utils.database import db
from utils.embed_creator import EmbedCreator
from config import CONFIG

logger = logging.getLogger('discord_bot')

# Time conversion constants
TIME_REGEX = re.compile(r"(\d+)([smhdw])")
TIME_DICT = {
    "s": 1,
    "m": 60,
    "h": 3600,
    "d": 86400,
    "w": 604800
}

class Giveaway(commands.Cog):
    """Giveaway system"""
    def __init__(self, bot):
        self.bot = bot
        logger.info(f"Giveaway cog initialized")
    
    @commands.command(name="unknown_method")
    @commands.has_permissions(manage_guild=True)
    async def unknown_method(self, ctx, *args):
        """Auto-generated method from fixing indentation"""

        # Check duration format
        seconds = self.convert_time_to_seconds(duration)
        if not seconds:
            embed = EmbedCreator.create_error_embed(
                "Invalid Duration",
                "Please provide a valid duration (e.g. 1h, 30m, 1d)."
            )
            await ctx.send(embed=embed)
            return
        
        # Check winners
        if winners < 1:
            embed = EmbedCreator.create_error_embed(
                "Invalid Winner Count",
                "The number of winners must be at least 1."
            )
            await ctx.send(embed=embed)
            return
        
        # Calculate end time
        end_time = datetime.now() + timedelta(seconds=seconds)
        
        # Create embed
        embed = EmbedCreator.create_giveaway_embed(prize, ctx.author, end_time, winners)
        
        # Send message
        message = await ctx.send(embed=embed)
        
        # Add reaction
        await message.add_reaction(CONFIG['emojis']['giveaway'])
        
        # Store giveaway in database
        db.create_giveaway(
            ctx.guild.id,
            ctx.channel.id,
            message.id,
            prize,
            ctx.author.id,
            end_time,
            winners
        )
        
        # Send confirmation to command user if different from giveaway channel
        if ctx.channel.id != message.channel.id:
            confirm_embed = EmbedCreator.create_success_embed(
                "Giveaway Started",
                f"Giveaway for **{prize}** has been started in {message.channel.mention}."
            )
            await ctx.send(embed=confirm_embed)
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Handle reactions for giveaways"""
        # Get the giveaway
        giveaway = db.get_giveaway(ctx.guild.id, message_id)
        if not giveaway:
            embed = EmbedCreator.create_error_embed(
                "Giveaway Not Found",
                "Could not find an active giveaway with that message ID."
            )
            await ctx.send(embed=embed)
            return
        
        # End the giveaway
        channel_id = int(giveaway['channel_id'])
        channel = ctx.guild.get_channel(channel_id)
        
        if not channel:
            embed = EmbedCreator.create_error_embed(
                "Channel Not Found",
                "The channel containing this giveaway no longer exists."
            )
            await ctx.send(embed=embed)
            return
        
        embed = EmbedCreator.create_info_embed(
            "Ending Giveaway",
            f"Ending the giveaway for **{giveaway['prize']}**..."
        )
        await ctx.send(embed=embed)
        
        # Force end time to now
        giveaway_data = {
            'guild_id': str(ctx.guild.id),
            'channel_id': str(channel_id),
            'message_id': message_id,
            'end_time': datetime.now(),
            'data': giveaway
        }
        
        await self.end_giveaway(giveaway_data)
    
    @commands.hybrid_command(name="greroll", description="Reroll a giveaway")
    @commands.has_permissions(manage_guild=True)
    async def greroll(self, ctx, message_id: str):
        """Reroll a giveaway to select new winners"""
        # Get the giveaway
        giveaway = db.get_giveaway(ctx.guild.id, message_id)
        if not giveaway:
            embed = EmbedCreator.create_error_embed(
                "Giveaway Not Found",
                "Could not find a giveaway with that message ID."
            )
            await ctx.send(embed=embed)
            return
        
        # Check if giveaway has participants
        if not giveaway.get('participants'):
            embed = EmbedCreator.create_error_embed(
                "No Participants",
                "This giveaway doesn't have any participants to reroll."
            )
            await ctx.send(embed=embed)
            return
        
        # Select new winners
        winners_count = min(giveaway['winners'], len(giveaway['participants']))
        winner_ids = random.sample(giveaway['participants'], winners_count)
        
        winners = []
        for winner_id in winner_ids:
            winner = ctx.guild.get_member(int(winner_id))
            if winner:
                winners.append(winner)
        
        if not winners:
            embed = EmbedCreator.create_error_embed(
                "No Valid Winners",
                "Could not find any valid members to select as winners."
            )
            await ctx.send(embed=embed)
            return
        
        # Announce new winners
        winners_text = ", ".join(winner.mention for winner in winners)
        
        embed = EmbedCreator.create_success_embed(
            "Giveaway Rerolled",
            f"New winners for **{giveaway['prize']}**: {winners_text}"
        )
        
        await ctx.send(embed=embed)
        
        # Send notification in the original channel
        channel = ctx.guild.get_channel(int(giveaway['channel_id']))
        if channel:
            await channel.send(
                f"🎉 The giveaway for **{giveaway['prize']}** has been rerolled!\n"
                f"New winners: {winners_text}",
                allowed_mentions=discord.AllowedMentions(users=True)
            )

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
