import discord
from discord.ext import commands
import logging
from typing import Dict, List, Optional
from config import CONFIG

logger = logging.getLogger('discord_bot')

# Command information for the enhanced help menu
COMMAND_CATEGORIES = {
    "general": {
        "name": "General",
        "emoji": "<:help:1373370856239267940>",
        "description": "General bot commands"
    },
    "moderation": {
        "name": "Moderation",
        "emoji": "<:Multipurpose:1373371000271409416>",
        "description": "Server moderation commands"
    },
    "levels": {
        "name": "Levels",
        "emoji": "<:Clipboard:1373605336820220097>",
        "description": "Level tracking and rewards"
    },
    "invites": {
        "name": "Invites",
        "emoji": "<:Join:1373605236354056346>",
        "description": "Invite tracking and statistics"
    },
    "messages": {
        "name": "Messages",
        "emoji": "<:Logs:1373372085866598550>",
        "description": "Message tracking and leaderboards"
    },
    "giveaways": {
        "name": "Giveaways",
        "emoji": "<:giveaway:1373607514112790610>",
        "description": "Create and manage giveaways"
    },
    "roles": {
        "name": "Roles",
        "emoji": "<:ReactionRole:1373607898730725469>",
        "description": "Self-assignable reaction roles"
    },
    "welcome": {
        "name": "Welcome",
        "emoji": "<:joinleave:1373607445439709225>",
        "description": "Welcome messages for new members"
    },
    "tickets": {
        "name": "Tickets",
        "emoji": "<:ticket:1373371061340606594>",
        "description": "Support ticket system"
    },
    "polls": {
        "name": "Polls",
        "emoji": "<:Clipboard:1373605336820220097>",
        "description": "Create and manage polls"
    },
    "islamic": {
        "name": "Islamic",
        "emoji": "☪️",
        "description": "Islamic commands and resources"
    },
    "logging": {
        "name": "Logging",
        "emoji": "<:Logs:1373372085866598550>",
        "description": "Server logging system"
    }
}

# Category colors for better visual organization
CATEGORY_COLORS = {
    "general": 0x7289DA,    # Discord Blue
    "moderation": 0xE74C3C,  # Red
    "levels": 0x2ECC71,     # Green
    "invites": 0x3498DB,    # Blue
    "messages": 0x9B59B6,   # Purple
    "giveaways": 0xF1C40F,  # Yellow
    "roles": 0xE67E22,      # Orange
    "tickets": 0x1ABC9C,    # Teal
    "welcome": 0xF39C12,    # Orange-Yellow
    "polls": 0x11806A,      # Dark Teal
    "islamic": 0x2ECC71,    # Green
    "logging": 0x607D8B     # Blue Grey
}

class CategorySelect(discord.ui.Select):
    """Dropdown for selecting help categories"""
    
    def __init__(self, bot):
        self.bot = bot
        
        # Create options for each category
        options = []
        for category_id, category_info in COMMAND_CATEGORIES.items():
            options.append(
                discord.SelectOption(
                    label=category_info["name"],
                    description=category_info["description"],
                    emoji=category_info["emoji"],
                    value=category_id
                )
            )
        
        super().__init__(
            placeholder="Select a command category...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="help_category_select",
            row=0
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Handle category selection"""
        category = self.values[0]
        
        # Get the theme color for this category
        color = CATEGORY_COLORS.get(category, CONFIG['colors']['default'])
        emoji = COMMAND_CATEGORIES[category]["emoji"]
        
        # Create embed for the selected category - NO IMAGE
        embed = discord.Embed(
            title=f"{emoji} {COMMAND_CATEGORIES[category]['name']} Commands",
            description=f"Use {CONFIG['prefix']}help <command> for more details on a command.",
            color=color
        )
        
        # Dynamically get all commands in the selected category
        commands_in_category = []
        
        for cmd in self.bot.commands:
            # Skip commands that start with _ or are hidden
            if cmd.name.startswith('_') or cmd.hidden:
                continue
                
            # Try to determine category based on cog name or command name
            cmd_category = None
            
            # If command has a cog, check if cog name matches a category
            if cmd.cog:
                cog_name = cmd.cog.qualified_name.lower()
                
                # Check for exact category names
                if cog_name == category:
                    cmd_category = category
                # Special cases for categories that might have different cog names
                elif category == "general" and cog_name in ["help", "utility", "info"]:
                    cmd_category = "general"
                elif category == "moderation" and cog_name in ["mod", "admin", "direct_moderation", "timeout", "channel_management"]:
                    cmd_category = "moderation"
                elif category == "giveaways" and cog_name == "giveaway":
                    cmd_category = "giveaways"
                elif category == "welcome" and cog_name in ["welcome", "greetings"]:
                    cmd_category = "welcome"
                elif category == "polls" and cog_name in ["poll", "polls"]:
                    cmd_category = "polls"
                elif category == "islamic" and cog_name in ["islamic", "islamic_commands"]:
                    cmd_category = "islamic"
                elif category == "logging" and cog_name in ["logging", "logs"]:
                    cmd_category = "logging"
            
            # If no category determined yet, try by command name
            if cmd_category is None:
                if category == "general" and cmd.name in ["help", "ping", "info"]:
                    cmd_category = "general"
                elif category == "moderation" and cmd.name in ["kick", "ban", "mute", "warn", "clear", "purge", "timeout", "lock", "unlock", "slowmode"]:
                    cmd_category = "moderation"
                elif category == "levels" and cmd.name in ["level", "rank", "leaderboard"]:
                    cmd_category = "levels"
                elif category == "invites" and cmd.name in ["invites", "invite"]:
                    cmd_category = "invites"
                elif category == "messages" and cmd.name in ["messages", "topmessages", "resetmessages"]:
                    cmd_category = "messages"
                elif category == "giveaways" and cmd.name in ["gstart", "gend", "greroll"]:
                    cmd_category = "giveaways"
                elif category == "roles" and cmd.name in ["reactionrole", "rolereaction", "rolemenu"]:
                    cmd_category = "roles"
                elif category == "welcome" and cmd.name in ["welcome", "setwelcome"]:
                    cmd_category = "welcome"
                elif category == "tickets" and cmd.name in ["ticket", "close"]:
                    cmd_category = "tickets"
                elif category == "polls" and cmd.name in ["poll"]:
                    cmd_category = "polls"
                elif category == "islamic" and cmd.name in ["islamic", "hadith", "quran", "dua"]:
                    cmd_category = "islamic"
                elif category == "logging" and cmd.name in ["logs", "log"]:
                    cmd_category = "logging"
            
            # If we determined this command belongs in the selected category
            if cmd_category == category:
                commands_in_category.append(cmd)
        
        if commands_in_category:
            command_text = ""
            
            # Get the category emoji
            category_emoji = COMMAND_CATEGORIES[category]["emoji"]
            
            # Command-specific emojis
            command_emojis = {
                # General
                "help": "<:help:1373370856239267940>",
                "ping": "<:Prefix:1373605377609957426>",
                "info": "<:help:1373370856239267940>",
                
                # Moderation
                "kick": "<:kick:1373370930440569073>",
                "ban": "<:banned:1373370889235726407>",
                "warn": "<:Warn:1373605418315677807>",
                "clear": "<:clear:1373370955279110245>",
                "purge": "<:clear:1373370955279110245>",
                "timeout": "<:timeout:1373371114155413504>",
                "untimeout": "<:timeout:1373371114155413504>",
                "timeoutinfo": "<:timeout:1373371114155413504>",
                "lock": "<:Multipurpose:1373371000271409416>",
                "unlock": "<:Multipurpose:1373371000271409416>",
                "slowmode": "<:mute:1373372051024248832>",
                
                # Levels
                "level": "<:Clipboard:1373605336820220097>",
                "leaderboard": "<:Clipboard:1373605336820220097>",
                
                # Invites
                "invites": "<:Join:1373605236354056346>",
                
                # Messages
                "messages": "<:Logs:1373372085866598550>",
                "topmessages": "<:Logs:1373372085866598550>",
                "resetmessages": "<:Logs:1373372085866598550>",
                
                # Giveaways
                "gstart": "<:giveaway:1373607514112790610>",
                "gend": "<:giveaway:1373607514112790610>",
                "greroll": "<:giveaway:1373607514112790610>",
                
                # Roles
                "reactionrole": "<:ReactionRole:1373607898730725469>",
                "rolemenu": "<:ReactionRole:1373607898730725469>",
                
                # Welcome
                "welcome": "<:joinleave:1373607445439709225>",
                "setwelcome": "<:joinleave:1373607445439709225>",
                
                # Tickets
                "ticket": "<:ticket:1373371061340606594>",
                "close": "<:ticket:1373371061340606594>",
                
                # Polls
                "poll": "<:Clipboard:1373605336820220097>",
                
                # Logging
                "logs": "<:Logs:1373372085866598550>",
                "log": "<:Logs:1373372085866598550>"
            }
            
            for cmd in sorted(commands_in_category, key=lambda x: x.name):
                # Get brief description or full help text
                desc = cmd.brief or cmd.help
                if desc:
                    # Truncate long descriptions
                    if len(desc) > 70:
                        desc = desc[:67] + "..."
                else:
                    desc = "No description available"
                
                # Get appropriate emoji for this command
                cmd_emoji = command_emojis.get(cmd.name, category_emoji)
                
                command_text += f"{cmd_emoji} `{CONFIG['prefix']}{cmd.name}` - {desc}\n"
            
            embed.description = f"{embed.description}\n\n{command_text}"
        else:
            embed.description = f"{embed.description}\n\nNo commands available in this category."
        
        # Add footer
        embed.set_footer(text="Created by gh_sman",
                        icon_url=self.bot.user.display_avatar.url)
        
        await interaction.response.edit_message(embed=embed, view=self.view)

class HelpView(discord.ui.View):
    """View containing the help menu components"""
    
    def __init__(self, bot):
        super().__init__(timeout=180)  # 3 minute timeout
        self.bot = bot
        
        # Add category select
        self.add_item(CategorySelect(bot))
        
        # Add home button
        self.home_button = discord.ui.Button(
            label="Home",
            emoji="🏠",
            style=discord.ButtonStyle.secondary,
            custom_id="help_home_button",
            row=1
        )
        self.home_button.callback = self.home_callback
        self.add_item(self.home_button)
        
        # Add invite button
        self.invite_button = discord.ui.Button(
            label="Invite",
            emoji="📨",
            style=discord.ButtonStyle.link,
            url="https://discord.com/api/oauth2/authorize?client_id=1373013347590602944&permissions=1099511627775&scope=bot%20applications.commands",
            row=1
        )
        self.add_item(self.invite_button)
        
        # Add support button
        self.support_button = discord.ui.Button(
            label="Support",
            emoji="❓",
            style=discord.ButtonStyle.link,
            url="https://discord.gg/gazaguild",
            row=1
        )
        self.add_item(self.support_button)
    
    async def home_callback(self, interaction: discord.Interaction):
        """Handle home button clicks"""
        embed = await self.create_home_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def create_home_embed(self):
        """Create the main help menu embed"""
        embed = discord.Embed(
            title="Bot Help Menu",
            description=f"Created by gh_sman\nMy prefix is {CONFIG['prefix']}\nUse the dropdown menu below to browse commands.",
            color=CONFIG['colors']['default']
        )
        
        # Set footer with bot avatar
        embed.set_footer(
            text="Created by gh_sman", 
            icon_url=self.bot.user.display_avatar.url
        )
        
        return embed

class EnhancedHelpMenu(commands.Cog):
    """Enhanced help menu with complete command listings"""
    
    def __init__(self, bot):
        self.bot = bot
        logger.info("EnhancedHelpMenu cog initialized")
    
    @commands.command(name="help", description="Shows the help menu with interactive dropdown")
    async def help_command(self, ctx, command=None):
        """Show the help menu with interactive dropdown"""
        if command is not None:
            # Show help for a specific command
            await self.show_command_help(ctx, command)
            return
        
        # Show the main help menu
        view = HelpView(self.bot)
        embed = await view.create_home_embed()
        
        # Simple help menu with no GIF, just the dropdown
        await ctx.send(embed=embed, view=view)
    
    async def show_command_help(self, ctx, command_name):
        """Show detailed help for a specific command"""
        cmd = self.bot.get_command(command_name)
        if not cmd:
            embed = discord.Embed(
                title="Command Not Found",
                description=f"Cannot find command `{command_name}`. Use `{CONFIG['prefix']}help` to see all available commands.",
                color=CONFIG['colors']['error']
            )
            await ctx.send(embed=embed)
            return
        
        # Command-specific emojis
        command_emojis = {
            # General
            "help": "<:help:1373370856239267940>",
            "ping": "<:Prefix:1373605377609957426>",
            "info": "<:help:1373370856239267940>",
            
            # Moderation
            "kick": "<:kick:1373370930440569073>",
            "ban": "<:banned:1373370889235726407>",
            "warn": "<:Warn:1373605418315677807>",
            "clear": "<:clear:1373370955279110245>",
            "purge": "<:clear:1373370955279110245>",
            "timeout": "<:timeout:1373371114155413504>",
            "untimeout": "<:timeout:1373371114155413504>",
            "timeoutinfo": "<:timeout:1373371114155413504>",
            "lock": "<:Multipurpose:1373371000271409416>",
            "unlock": "<:Multipurpose:1373371000271409416>",
            "slowmode": "<:mute:1373372051024248832>",
            
            # Levels
            "level": "<:Clipboard:1373605336820220097>",
            "leaderboard": "<:Clipboard:1373605336820220097>",
            
            # Invites
            "invites": "<:Join:1373605236354056346>",
            
            # Messages
            "messages": "<:Logs:1373372085866598550>",
            "topmessages": "<:Logs:1373372085866598550>",
            "resetmessages": "<:Logs:1373372085866598550>",
            
            # Giveaways
            "gstart": "<:giveaway:1373607514112790610>",
            "gend": "<:giveaway:1373607514112790610>",
            "greroll": "<:giveaway:1373607514112790610>",
            
            # Roles
            "reactionrole": "<:ReactionRole:1373607898730725469>",
            "rolemenu": "<:ReactionRole:1373607898730725469>",
            
            # Welcome
            "welcome": "<:joinleave:1373607445439709225>",
            "setwelcome": "<:joinleave:1373607445439709225>",
            
            # Tickets
            "ticket": "<:ticket:1373371061340606594>",
            "close": "<:ticket:1373371061340606594>",
            
            # Polls
            "poll": "<:Clipboard:1373605336820220097>",
            
            # Logging
            "logs": "<:Logs:1373372085866598550>",
            "log": "<:Logs:1373372085866598550>"
        }
        
        # Get emoji for this command
        cmd_emoji = command_emojis.get(cmd.name, "")
        
        # Clean up the help text by removing Args section
        help_text = cmd.help or "No description available."
        
        # Remove the Args: section which can look ugly when truncated
        if "Args:" in help_text:
            help_text = help_text.split("Args:")[0].strip()
        
        # Create detailed command help
        embed = discord.Embed(
            title=f"{cmd_emoji} Help: {CONFIG['prefix']}{cmd.name}",
            description=help_text,
            color=CONFIG['colors']['default']
        )
        
        # Add aliases if any
        if cmd.aliases:
            aliases_text = ", ".join([f"`{CONFIG['prefix']}{alias}`" for alias in cmd.aliases])
            embed.add_field(name="Aliases", value=aliases_text, inline=False)
        
        # Add parameters in a cleaner format
        if cmd.signature:
            param_parts = cmd.signature.split()
            param_text = ""
            
            for part in param_parts:
                if part.startswith('<') and part.endswith('>'):
                    # Format parameter nicely
                    param_name = part[1:-1]
                    # Check if there's a type hint like member: discord.Member
                    if ':' in param_name:
                        name, type_hint = param_name.split(':', 1)
                        param_text += f"• **{name}** - {type_hint.strip()}\n"
                    else:
                        param_text += f"• **{param_name}**\n"
            
            if param_text:
                embed.add_field(name="Parameters", value=param_text, inline=False)
        
        # Add usage
        usage = f"{CONFIG['prefix']}{cmd.name}"
        if cmd.signature:
            usage += f" {cmd.signature}"
        
        embed.add_field(name="Usage", value=f"`{usage}`", inline=False)
        
        # Try to determine the category
        category = None
        if cmd.cog:
            cog_name = cmd.cog.qualified_name.lower()
            # Try to match cog name to a category
            for cat_id, cat_info in COMMAND_CATEGORIES.items():
                if cog_name == cat_id or (cat_id == "giveaways" and cog_name == "giveaway"):
                    category = cat_id
                    break
        
        # If no category found by cog, try by command name
        if category is None:
            for cat_id, commands_list in [
                ("general", ["help", "ping", "info"]),
                ("moderation", ["kick", "ban", "mute", "warn", "clear", "purge", "timeout"]),
                ("levels", ["level", "rank", "leaderboard"]),
                ("invites", ["invites", "invite"]),
                ("messages", ["messages", "topmessages"]),
                ("giveaways", ["gstart", "gend", "greroll"]),
                ("roles", ["reactionrole", "rolereaction"]),
                ("welcome", ["welcome", "setwelcome"]),
                ("tickets", ["ticket", "close"]),
                ("polls", ["poll"]),
                ("islamic", ["islamic", "hadith", "quran", "dua"]),
                ("logging", ["logs", "log"])
            ]:
                if cmd.name in commands_list:
                    category = cat_id
                    break
        
        # If we found a category
        if category:
            cat_info = COMMAND_CATEGORIES[category]
            embed.add_field(
                name="Category",
                value=f"{cat_info['emoji']} {cat_info['name']}",
                inline=True
            )
        
        # Add examples section with emoji
        examples_text = f"{cmd_emoji} `{CONFIG['prefix']}{cmd.name}`"
        if cmd.signature:
            param_parts = cmd.signature.split()
            example_params = []
            for part in param_parts:
                if part.startswith('<') and part.endswith('>'):
                    # Replace parameter with example value
                    param_name = part[1:-1].split(':', 1)[0]  # Remove type hints if any
                    if param_name == "member":
                        example_params.append("@user")
                    elif param_name == "amount":
                        example_params.append("10")
                    elif param_name == "channel":
                        example_params.append("#channel")
                    elif param_name == "role":
                        example_params.append("@role")
                    elif param_name == "duration":
                        example_params.append("1h")
                    elif param_name == "reason":
                        example_params.append("\"breaking rules\"")
                    elif param_name == "message_id":
                        example_params.append("123456789012345678")
                    elif param_name == "prize":
                        example_params.append("\"Nitro\"")
                    elif param_name == "winners":
                        example_params.append("1")
                    else:
                        example_params.append(f"[{param_name}]")
                else:
                    example_params.append(part)
                    
            examples_text = f"{cmd_emoji} `{CONFIG['prefix']}{cmd.name} {' '.join(example_params)}`"
            
        embed.add_field(
            name="Example",
            value=examples_text,
            inline=False
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    # Remove the old help command
    bot.remove_command('help')
    # Add the new help command
    await bot.add_cog(EnhancedHelpMenu(bot))