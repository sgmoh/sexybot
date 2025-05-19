import discord
from discord.ext import commands
import logging
import json
import os
from discord import ui, SelectOption
from config import CONFIG
from utils.embed_creator import EmbedCreator

logger = logging.getLogger('discord_bot')

import asyncio

class RoleDropdown(ui.Select):
    """Dropdown menu for role selection"""
        # Determine the target channel
        target_channel = channel or ctx.channel
        
        # Check bot permissions in the target channel
        if not target_channel.permissions_for(ctx.guild.me).send_messages:
            await ctx.send(embed=EmbedCreator.create_error_embed(
                "Missing Permissions",
                f"I don't have permission to send messages in {target_channel.mention}."
            ))
            return
            
        # Start the role menu creation process
        embed = EmbedCreator.create_info_embed(
            "Role Menu Setup (1/4)",
            "Please enter a title for your role menu, or type 'cancel' to abort."
        )
        
        await ctx.send(embed=embed)
        
        # Wait for the title
        try:
            title_message = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                timeout=60.0
            )
            
            title = title_message.content
            
            if title.lower() == "cancel":
                await ctx.send(embed=EmbedCreator.create_error_embed("Setup Cancelled", "Role menu creation has been cancelled."))
                return
                
            # Ask for description
            embed = EmbedCreator.create_info_embed(
                "Role Menu Setup (2/4)",
                "Please enter a description for your role menu, or type 'cancel' to abort."
            )
            
            await ctx.send(embed=embed)
            
            # Wait for the description
            description_message = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                timeout=60.0
            )
            
            description = description_message.content
            
            if description.lower() == "cancel":
                await ctx.send(embed=EmbedCreator.create_error_embed("Setup Cancelled", "Role menu creation has been cancelled."))
                return
            
            # Ask about multiple selection
            embed = EmbedCreator.create_info_embed(
                "Role Menu Setup (3/4)",
                "Should users be able to select multiple roles at once? (yes/no)"
            )
            
            await ctx.send(embed=embed)
            
            # Wait for multiple selection response
            multi_message = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                timeout=60.0
            )
            
            allow_multiple = multi_message.content.lower() in ["yes", "y", "true", "1"]
                
            # Ask for roles
            embed = EmbedCreator.create_info_embed(
                "Role Menu Setup (4/4)",
                "Now let's add some roles. For each role, send a message in this format:\n"
                "@Role Description of the role\n\n"
                "You can optionally include an emoji after the role mention:\n"
                "@Role 🎮 Gamers role\n\n"
                "Send 'done' when you're finished, or 'cancel' to abort."
            )
            
            await ctx.send(embed=embed)
            
            # Collect roles
            roles_data = {}
            
            while True:
                role_message = await self.bot.wait_for(
                    "message",
                    check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                    timeout=120.0
                )
                
                content = role_message.content
                
                if content.lower() == "cancel":
                    await ctx.send(embed=EmbedCreator.create_error_embed("Setup Cancelled", "Role menu creation has been cancelled."))
                    return
                    
                if content.lower() == "done":
                    if not roles_data:
                        await ctx.send(embed=EmbedCreator.create_error_embed("No Roles Added", "You need to add at least one role. Try again or type 'cancel' to abort."))
                        continue
                    else:
                        break
                
                # Parse role from the message
                if not role_message.role_mentions:
                    await ctx.send("Please mention a role with @Role.")
                    continue
                
                role = role_message.role_mentions[0]
                
                # Check bot permissions for the role
                if role >= ctx.guild.me.top_role:
                    await ctx.send(f"I cannot assign the role {role.mention} because it's higher than or equal to my highest role.")
                    continue
                    
                # Get description (everything after the role mention)
                parts = content.split(' ', 1)
                if len(parts) < 2:
                    await ctx.send("Please include a description for the role.")
                    continue
                    
                role_content = parts[1].strip()
                
                # Check if there's an emoji at the start of the description
                emoji = None
                description = role_content
                
                # Try to parse emoji from the start of the description
                for i, char in enumerate(role_content):
                    if char.isalpha() or char.isspace():
                        if i > 0:
                            emoji = role_content[:i].strip()
                            description = role_content[i:].strip()
                        break
                
                # Store role information
                roles_data[str(role.id)] = {
                    "name": role.name,
                    "description": description,
                }
                
                if emoji:
                    roles_data[str(role.id)]["emoji"] = emoji
                
                await ctx.send(f"Added role {role.mention}.")
            
            # Create the role menu embed
            menu_embed = discord.Embed(
                title=title,
                description=description,
                color=CONFIG['colors']['default']
            )
            
            # Add instructions based on selection type
            if allow_multiple:
                instructions = "You can select multiple roles from the dropdown menu below."
            else:
                instructions = "Select a role from the dropdown menu below."
                
            menu_embed.add_field(
                name="Available Roles",
                value=instructions,
                inline=False
            )
            
            # Create the view with the dropdown, handling single/multi selection
            view = RoleMenuView(roles_data)
            
            # Adjust max_values for the dropdown
            if not allow_multiple:
                for item in view.children:
                    if isinstance(item, RoleDropdown):
                        item.max_values = 1
            
            # Send the menu to the target channel
            try:
                menu_message = await target_channel.send(embed=menu_embed, view=view)
                
                # Save the menu to settings
                guild_id = str(ctx.guild.id)
                
                if guild_id not in self.role_menus:
                    self.role_menus[guild_id] = {}
                    
                self.role_menus[guild_id][str(menu_message.id)] = {
                    "title": title,
                    "description": description,
                    "roles": roles_data,
                    "channel_id": str(target_channel.id),
                    "author_id": str(ctx.author.id),
                    "multiple": allow_multiple
                }
                
                self.save_settings()
                
                # Send confirmation
                success_message = f"Your role menu has been created in {target_channel.mention}!"
                if target_channel != ctx.channel:
                    success_message += f" [Jump to Message]({menu_message.jump_url})"
                    
                await ctx.send(embed=EmbedCreator.create_success_embed(
                    "Role Menu Created",
                    success_message
                ))
            except Exception as e:
                await ctx.send(embed=EmbedCreator.create_error_embed(
                    "Error",
                    f"Failed to create role menu: {str(e)}"
                ))
            
        except asyncio.TimeoutError:
            await ctx.send(embed=EmbedCreator.create_error_embed("Setup Timed Out", "You took too long to respond. Please try again."))
            return
        except Exception as e:
            logger.error(f"Error creating role menu: {e}")
            await ctx.send(embed=EmbedCreator.create_error_embed("Error", f"An error occurred while creating the role menu: {str(e)}"))
            return
    
    @rolemenu.command(name="delete")
    @commands.has_permissions(manage_roles=True)
    async def delete_menu(self, ctx, message_id: str):
        """Delete a role menu"""
        guild_id = str(ctx.guild.id)
        
        # Check if the menu exists
        if (guild_id not in self.role_menus or
            message_id not in self.role_menus[guild_id]):
            
            await ctx.send(embed=EmbedCreator.create_error_embed(
                "Menu Not Found",
                f"Could not find a role menu with ID {message_id}."
            ))
            return
        
        # Get the menu data
        menu_data = self.role_menus[guild_id][message_id]
        
        # Check permissions to delete
        if (str(ctx.author.id) != menu_data["author_id"] and
            not ctx.author.guild_permissions.administrator):
            
            await ctx.send(embed=EmbedCreator.create_error_embed(
                "Permission Denied",
                "You can only delete role menus that you created, unless you are an administrator."
            ))
            return
        
        # Try to delete the message
        try:
            channel = ctx.guild.get_channel(int(menu_data["channel_id"]))
            if channel:
                try:
                    message = await channel.fetch_message(int(message_id))
                    if message:
                        await message.delete()
                except:
                    pass
        except Exception as e:
            logger.error(f"Error deleting role menu message: {e}")
        
        # Remove the menu from settings
        del self.role_menus[guild_id][message_id]
        if not self.role_menus[guild_id]:
            del self.role_menus[guild_id]
            
        self.save_settings()
        
        # Send confirmation
        await ctx.send(embed=EmbedCreator.create_success_embed(
            "Role Menu Deleted",
            f"The role menu with ID {message_id} has been deleted."
        ))
    
    @rolemenu.command(name="list")
    @commands.has_permissions(manage_roles=True)
    async def list_menus(self, ctx):
        """List all role menus in the server"""
        guild_id = str(ctx.guild.id)
        
        # Check if there are any menus
        if guild_id not in self.role_menus or not self.role_menus[guild_id]:
            await ctx.send(embed=EmbedCreator.create_info_embed(
                "No Role Menus",
                "There are no role menus in this server."
            ))
            return
        
        # Create embed
        embed = discord.Embed(
            title="🔽 Role Menus",
            description=f"There are {len(self.role_menus[guild_id])} role menus in this server.",
            color=CONFIG['colors']['info']
        )
        
        # Add each menu
        for message_id, menu_data in self.role_menus[guild_id].items():
            # Get channel
            channel = ctx.guild.get_channel(int(menu_data["channel_id"]))
            channel_mention = channel.mention if channel else "Unknown Channel"
            
            # Get author
            author_id = menu_data["author_id"]
            author = ctx.guild.get_member(int(author_id))
            author_name = author.display_name if author else "Unknown User"
            
            # Get role count
            role_count = len(menu_data["roles"])
            
            # Create field
            embed.add_field(
                name=f"Menu: {menu_data['title']}",
                value=f"**ID:** {message_id}\n"
                      f"**Channel:** {channel_mention}\n"
                      f"**Roles:** {role_count}\n"
                      f"**Created by:** {author_name}\n"
                      f"`{CONFIG['prefix']}rolemenu delete {message_id}` to delete",
                inline=False
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(RoleMenu(bot))