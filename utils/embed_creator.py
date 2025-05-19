import discord
from config import CONFIG

class EmbedCreator:
    """Utility class to create standardized embeds for the bot"""
    
    @staticmethod
    def create_embed(title, description=None, color=None, footer=None, thumbnail=None, image=None, fields=None):
        """Create a Discord embed with standardized formatting
        
        Args:
            title: The embed title
            description: The embed description
            color: The embed color (integer)
            footer: The embed footer text
            thumbnail: The embed thumbnail URL
            image: The embed image URL
            fields: List of tuples (name, value, inline) for fields
            
        Returns:
            discord.Embed: The created embed
        """
        # Use default color if none specified
        if color is None:
            color = CONFIG['colors']['default']
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )
        
        if footer:
            embed.set_footer(text=footer)
        else:
            embed.set_footer(text=f"Use {CONFIG['prefix']}help for more commands")
        
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        
        if image:
            embed.set_image(url=image)
        
        if fields:
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
        
        return embed
    
    @staticmethod
    def create_success_embed(title, description=None, **kwargs):
        """Create a success (green) embed"""
        return EmbedCreator.create_embed(
            f"{CONFIG['emojis']['success']} {title}",
            description,
            CONFIG['colors']['success'],
            **kwargs
        )
    
    @staticmethod
    def create_error_embed(title, description=None, **kwargs):
        """Create an error (red) embed"""
        return EmbedCreator.create_embed(
            f"{CONFIG['emojis']['error']} {title}",
            description,
            CONFIG['colors']['error'],
            **kwargs
        )
    
    @staticmethod
    def create_warning_embed(title, description=None, **kwargs):
        """Create a warning (yellow) embed"""
        return EmbedCreator.create_embed(
            f"{CONFIG['emojis']['warning']} {title}",
            description,
            CONFIG['colors']['warning'],
            **kwargs
        )
    
    @staticmethod
    def create_info_embed(title, description=None, **kwargs):
        """Create an info (blue) embed"""
        return EmbedCreator.create_embed(
            f"{CONFIG['emojis']['info']} {title}",
            description,
            CONFIG['colors']['info'],
            **kwargs
        )
    
    @staticmethod
    def create_loading_embed(title, description=None, **kwargs):
        """Create a loading embed"""
        return EmbedCreator.create_embed(
            f"{CONFIG['emojis']['loading']} {title}",
            description,
            CONFIG['colors']['default'],
            **kwargs
        )