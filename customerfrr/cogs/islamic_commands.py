import discord
from discord.ext import commands
import logging
import json
import os
import random
import datetime
from config import CONFIG

logger = logging.getLogger('discord_bot')

class IslamicCommands(commands.Cog):
    """Islamic commands and utilities"""
        if dua_name:
            # Look for specific dua
            matching_duas = [d for d in self.duas if d["name"].lower() == dua_name.lower()]
            
            if not matching_duas:
                # Try partial match
                matching_duas = [d for d in self.duas if dua_name.lower() in d["name"].lower()]
                
            if not matching_duas:
                embed = discord.Embed(
                    title="❌ Dua Not Found",
                    description=f"Could not find a dua with the name '{dua_name}'. Try using one of the following:\n" + 
                                "\n".join([f"• {d['name']}" for d in self.duas]),
                    color=CONFIG['colors']['error']
                )
                await ctx.send(embed=embed)
                return
                
            dua = matching_duas[0]
        else:
            # Select a random dua
            dua = random.choice(self.duas)
        
        embed = discord.Embed(
            title=f"🤲 {dua['name']}",
            color=CONFIG['colors']['default']
        )
        
        embed.add_field(
            name="Arabic",
            value=dua["arabic"],
            inline=False
        )
        
        embed.add_field(
            name="Translation",
            value=dua["translation"],
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @islamic.command(name="reminder")
    async def quran_reminder(self, ctx):
        """Get a random Quranic reminder"""
        # Simply show a random verse instead of requiring specific input
        verse = random.choice(self.quran_verses)
        
        embed = discord.Embed(
            title="📖 Quran Verse",
            description=verse["verse"],
            color=CONFIG['colors']['default']
        )
        
        embed.set_footer(text=f"Surah {verse['surah']}")
        
        await ctx.send(embed=embed)
    
    @islamic.command(name="calendar")
    async def islamic_calendar(self, ctx):
        """View current Islamic calendar date"""
        try:
            # For simplicity, provide the current date without external API
            # In a full implementation, this would fetch the actual Hijri date
            current_date = datetime.datetime.now()
            
            embed = discord.Embed(
                title="📅 Islamic Calendar",
                description="Islamic date information",
                color=CONFIG['colors']['default']
            )
            
            embed.add_field(
                name="Gregorian Date",
                value=current_date.strftime("%d %B %Y"),
                inline=True
            )
            
            embed.add_field(
                name="Note",
                value="This is a placeholder for the Islamic date. A full implementation would convert or fetch the actual Hijri date.",
                inline=False
            )
            
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Error displaying Islamic calendar: {e}")
            
            embed = discord.Embed(
                title="⚠️ Could not display Islamic calendar",
                description="An error occurred while trying to display the Islamic calendar.",
                color=CONFIG['colors']['error']
            )
            
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(IslamicCommands(bot))