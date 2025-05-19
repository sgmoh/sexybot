import discord
from discord.ext import commands
import logging
import asyncio

from utils.database import db
from utils.embed_creator import EmbedCreator
from config import CONFIG

logger = logging.getLogger('discord_bot')

class RoleSelect(discord.ui.Select):
    """Dropdown for selecting roles"""
        try:
            # Check if message exists in the database
            reaction_roles = db.data.get('reaction_roles', {}).get(str(ctx.guild.id), {}).get(message_id)
            
            if not reaction_roles:
                embed = EmbedCreator.create_error_embed(
                    "Not Found",
                    "Could not find a reaction role message with that ID."
                )
                await ctx.send(embed=embed)
                return
            
            # Try to delete the message
            try:
                for channel in ctx.guild.text_channels:
                    try:
                        message = await channel.fetch_message(int(message_id))
                        await message.delete()
                        break
                    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                        continue
            except Exception as e:
                logger.error(f"Error deleting message: {e}")
                await ctx.send("Could not delete the message, but will remove it from the database.")
            
            # Remove from database
            if str(ctx.guild.id) in db.data.get('reaction_roles', {}) and message_id in db.data['reaction_roles'][str(ctx.guild.id)]:
                del db.data['reaction_roles'][str(ctx.guild.id)][message_id]
                db._save_data()
            
            embed = EmbedCreator.create_success_embed(
                "Deleted",
                "Reaction role message has been deleted."
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in reaction role delete: {e}")
            embed = EmbedCreator.create_error_embed(
                "Error",
                f"An error occurred: {e}"
            )
            await ctx.send(embed=embed)
    
    @reactionrole.command(name="list", description="List all reaction role messages")
    @commands.has_permissions(manage_roles=True)
    async def list(self, ctx):
        """List all reaction role messages in the server"""
        reaction_roles = db.data.get('reaction_roles', {}).get(str(ctx.guild.id), {})
        
        if not reaction_roles:
            embed = EmbedCreator.create_info_embed(
                "No Reaction Roles",
                "This server has no reaction role messages."
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="Reaction Role Messages",
            description="Here are all the reaction role messages in this server:",
            color=CONFIG['colors']['default']
        )
        
        for message_id, roles in reaction_roles.items():
            role_count = len(roles)
            
            # Try to get the channel
            channel_id = None
            for channel in ctx.guild.text_channels:
                try:
                    message = await channel.fetch_message(int(message_id))
                    channel_id = channel.id
                    break
                except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                    continue
            
            channel_text = f"<#{channel_id}>" if channel_id else "Unknown channel"
            
            embed.add_field(
                name=f"Message ID: {message_id}",
                value=f"Channel: {channel_text}\nRoles: {role_count}",
                inline=False
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))
