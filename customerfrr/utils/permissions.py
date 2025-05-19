import discord
from discord.ext import commands
import logging

logger = logging.getLogger('discord_bot')

async def check_permissions(ctx, perms):
    """Check if user has all the required permissions
    
    Args:
        ctx: The command context
        perms: A dictionary of permissions to check
        
    Returns:
        bool: True if the user has all the permissions, False otherwise
    """
    if await ctx.bot.is_owner(ctx.author):
        return True
        
    if ctx.guild is None:
        return False
        
    # Get the resolved permissions for the user
    resolved = ctx.channel.permissions_for(ctx.author)
    return all(getattr(resolved, perm, None) == value for perm, value in perms.items())
    
def has_permissions(**perms):
    """Decorator that checks if the user has the required permissions
    
    Args:
        **perms: The permissions to check
        
    Returns:
        bool: Whether the user has the required permissions
    """
    async def predicate(ctx):
        return await check_permissions(ctx, perms)
    return commands.check(predicate)
    
def is_admin():
    """Decorator that checks if the user is an administrator
    
    Returns:
        bool: Whether the user is an administrator
    """
    return has_permissions(administrator=True)
    
def is_mod():
    """Decorator that checks if the user is a moderator (has manage messages)
    
    Returns:
        bool: Whether the user is a moderator
    """
    return has_permissions(manage_messages=True)