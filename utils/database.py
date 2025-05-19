import json
import os
import logging
import time
from datetime import datetime

logger = logging.getLogger('discord_bot')

class Database:
    """Simple JSON-based database for the bot"""
    
    def __init__(self, file_path='bot_database.json'):
        """Initialize the database
        
        Args:
            file_path: Path to the database file
        """
        self.file_path = file_path
        self.data = self._load_data()
        self._migrate_if_needed()
    
    def _load_data(self):
        """Load data from the database file"""
        if not os.path.exists(self.file_path):
            logger.info(f"Database file {self.file_path} not found, creating new one")
            return {
                "guilds": {},
                "users": {},
                "giveaways": {},
                "autoroles": {},
                "levels": {},
                "tickets": {},
                "invites": {},
                "message_counts": {},
                "reaction_roles": {}
            }
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Failed to decode {self.file_path}, creating new database")
            return {
                "guilds": {},
                "users": {},
                "giveaways": {},
                "autoroles": {},
                "levels": {},
                "tickets": {},
                "invites": {},
                "message_counts": {},
                "reaction_roles": {}
            }
    
    def _migrate_if_needed(self):
        """Migrate database structure if needed"""
        # Make sure all required top-level keys exist
        required_keys = ["guilds", "users", "giveaways", "autoroles", "levels", 
                         "tickets", "invites", "message_counts", "reaction_roles"]
        
        for key in required_keys:
            if key not in self.data:
                self.data[key] = {}
        
        self._save_data()
    
    def _save_data(self):
        """Save data to the database file"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Failed to save database: {e}")
            return False
    
    def _get_guild(self, guild_id):
        """Get a guild's data, creating it if it doesn't exist"""
        guild_id = str(guild_id)  # Convert to string for JSON
        if "guilds" not in self.data:
            self.data["guilds"] = {}
            
        if guild_id not in self.data["guilds"]:
            self.data["guilds"][guild_id] = {
                "settings": {},
                "autorole": None,
                "welcome": {
                    "enabled": False,
                    "channel_id": None,
                    "message": "Welcome {user} to {server}!"
                },
                "logging": {
                    "enabled": False,
                    "channel_id": None,
                    "events": []
                },
                "levels": {
                    "enabled": True,
                    "channel_id": None,
                    "roles": {}
                },
                "reaction_roles": {},
                "ticket_system": {
                    "enabled": False,
                    "category_id": None,
                    "message_id": None,
                    "channel_id": None
                }
            }
        return self.data["guilds"][guild_id]
    
    def _get_user(self, user_id):
        """Get a user's data, creating it if it doesn't exist"""
        user_id = str(user_id)  # Convert to string for JSON
        if "users" not in self.data:
            self.data["users"] = {}
            
        if user_id not in self.data["users"]:
            self.data["users"][user_id] = {
                "xp": {},
                "settings": {}
            }
        return self.data["users"][user_id]
    
    # Autorole methods
    def get_autorole(self, guild_id):
        """Get the autorole for a guild"""
        guild_id = str(guild_id)
        if "autoroles" not in self.data:
            self.data["autoroles"] = {}
            return None
            
        return self.data["autoroles"].get(guild_id)
    
    def set_autorole(self, guild_id, role_id):
        """Set the autorole for a guild"""
        guild_id = str(guild_id)
        role_id = str(role_id)
        
        if "autoroles" not in self.data:
            self.data["autoroles"] = {}
            
        self.data["autoroles"][guild_id] = role_id
        return self._save_data()
    
    def remove_autorole(self, guild_id):
        """Remove the autorole for a guild"""
        guild_id = str(guild_id)
        
        if "autoroles" not in self.data or guild_id not in self.data["autoroles"]:
            return False
            
        del self.data["autoroles"][guild_id]
        return self._save_data()
    
    # Welcome message methods
    def get_welcome_settings(self, guild_id):
        """Get welcome settings for a guild"""
        guild = self._get_guild(guild_id)
        return guild.get("welcome", {})
    
    def set_welcome_settings(self, guild_id, enabled=None, channel_id=None, message=None):
        """Set welcome settings for a guild"""
        guild = self._get_guild(guild_id)
        if "welcome" not in guild:
            guild["welcome"] = {
                "enabled": False,
                "channel_id": None,
                "message": "Welcome {user} to {server}!"
            }
        
        if enabled is not None:
            guild["welcome"]["enabled"] = enabled
        if channel_id is not None:
            guild["welcome"]["channel_id"] = str(channel_id)
        if message is not None:
            guild["welcome"]["message"] = message
        
        return self._save_data()
    
    # XP and leveling methods
    def get_xp(self, user_id, guild_id):
        """Get a user's XP in a guild"""
        user_id = str(user_id)
        guild_id = str(guild_id)
        
        if "levels" not in self.data:
            self.data["levels"] = {}
            
        if guild_id not in self.data["levels"]:
            self.data["levels"][guild_id] = {}
            
        if user_id not in self.data["levels"][guild_id]:
            self.data["levels"][guild_id][user_id] = {
                "level": 0,
                "xp": 0
            }
            
        return self.data["levels"][guild_id][user_id]
    
    def add_xp(self, user_id, guild_id, xp_amount):
        """Add XP to a user in a guild, returns new level if leveled up"""
        user_xp = self.get_xp(user_id, guild_id)
        old_level = user_xp["level"]
        
        user_xp["xp"] += xp_amount
        
        # Calculate new level based on total XP
        # Formula: level = sqrt(total_xp / 100)
        import math
        new_level = math.floor(math.sqrt(user_xp["xp"] / 100))
        
        user_xp["level"] = new_level
        self._save_data()
        
        # Return the new level if leveled up, otherwise None
        if new_level > old_level:
            return new_level
        return None
    
    def set_last_message_time(self, user_id, guild_id, timestamp):
        """Set the last message time for XP cooldown"""
        user_id = str(user_id)
        guild_id = str(guild_id)
        
        if "levels" not in self.data:
            self.data["levels"] = {}
            
        if guild_id not in self.data["levels"]:
            self.data["levels"][guild_id] = {}
            
        if user_id not in self.data["levels"][guild_id]:
            self.data["levels"][guild_id][user_id] = {
                "level": 0,
                "xp": 0,
                "last_message_time": timestamp
            }
        else:
            self.data["levels"][guild_id][user_id]["last_message_time"] = timestamp
            
        return self._save_data()
    
    def get_level_settings(self, guild_id):
        """Get level settings for a guild"""
        guild = self._get_guild(guild_id)
        return guild.get("levels", {})
    
    def set_level_settings(self, guild_id, enabled=None, channel_id=None, roles=None):
        """Set level settings for a guild"""
        guild = self._get_guild(guild_id)
        if "levels" not in guild:
            guild["levels"] = {
                "enabled": True,
                "channel_id": None,
                "roles": {}
            }
        
        if enabled is not None:
            guild["levels"]["enabled"] = enabled
        if channel_id is not None:
            guild["levels"]["channel_id"] = str(channel_id) if channel_id else None
        if roles is not None:
            guild["levels"]["roles"] = roles
        
        return self._save_data()
    
    # Message tracking methods
    def increment_message_count(self, guild_id, user_id):
        """Increment message count for a user in a guild"""
        user_id = str(user_id)
        guild_id = str(guild_id)
        today = datetime.now().strftime("%Y-%m-%d")
        
        if "message_counts" not in self.data:
            self.data["message_counts"] = {}
            
        if guild_id not in self.data["message_counts"]:
            self.data["message_counts"][guild_id] = {}
            
        if user_id not in self.data["message_counts"][guild_id]:
            self.data["message_counts"][guild_id][user_id] = {
                "all_time": 0,
                "daily": {}
            }
            
        # Increment all-time count
        self.data["message_counts"][guild_id][user_id]["all_time"] += 1
        
        # Increment daily count
        if "daily" not in self.data["message_counts"][guild_id][user_id]:
            self.data["message_counts"][guild_id][user_id]["daily"] = {}
            
        if today not in self.data["message_counts"][guild_id][user_id]["daily"]:
            self.data["message_counts"][guild_id][user_id]["daily"][today] = 0
            
        self.data["message_counts"][guild_id][user_id]["daily"][today] += 1
        
        return self._save_data()
    
    def get_message_count(self, guild_id, user_id):
        """Get message count for a user in a guild"""
        user_id = str(user_id)
        guild_id = str(guild_id)
        
        if ("message_counts" not in self.data or 
            guild_id not in self.data["message_counts"] or 
            user_id not in self.data["message_counts"][guild_id]):
            return 0
            
        return self.data["message_counts"][guild_id][user_id]["all_time"]
    
    def get_top_users_by_messages(self, guild_id, limit=10):
        """Get top users by message count in a guild"""
        guild_id = str(guild_id)
        
        if "message_counts" not in self.data or guild_id not in self.data["message_counts"]:
            return []
            
        sorted_users = sorted(
            self.data["message_counts"][guild_id].items(),
            key=lambda x: x[1]["all_time"],
            reverse=True
        )
        
        return sorted_users[:limit]
        
    # Poll methods
    def create_poll(self, message_id, guild_id, channel_id, question, options, end_time=None):
        """Create a new poll"""
        guild = self._get_guild(guild_id)
        
        if "polls" not in guild:
            guild["polls"] = {}
        
        guild["polls"][str(message_id)] = {
            "channel_id": str(channel_id),
            "question": question,
            "options": options,
            "votes": {},
            "end_time": end_time
        }
        
        return self._save_data()
    
    def get_poll(self, message_id, guild_id):
        """Get a poll by message ID"""
        guild = self._get_guild(guild_id)
        if "polls" not in guild:
            return None
        
        return guild["polls"].get(str(message_id))
    
    def add_poll_vote(self, message_id, guild_id, user_id, option_index):
        """Add a vote to a poll"""
        poll = self.get_poll(message_id, guild_id)
        if not poll:
            return False
        
        user_id = str(user_id)
        
        # Remove existing vote if any
        for option in poll["votes"]:
            if user_id in poll["votes"][option]:
                poll["votes"][option].remove(user_id)
        
        # Add the new vote
        option_str = str(option_index)
        if option_str not in poll["votes"]:
            poll["votes"][option_str] = []
        
        poll["votes"][option_str].append(user_id)
        
        return self._save_data()
    
    def end_poll(self, message_id, guild_id):
        """End a poll and return the results"""
        poll = self.get_poll(message_id, guild_id)
        if not poll:
            return None
        
        results = []
        for i, option in enumerate(poll["options"]):
            vote_count = len(poll["votes"].get(str(i), []))
            results.append((option, vote_count))
        
        # Remove the poll from the database
        self.data["guilds"][str(guild_id)]["polls"].pop(str(message_id))
        self._save_data()
        
        return results
        
    # Giveaway methods
    def create_giveaway(self, message_id, channel_id, guild_id, prize, host_id, end_time, winners=1):
        """Create a new giveaway"""
        if "giveaways" not in self.data:
            self.data["giveaways"] = {}
            
        self.data["giveaways"][str(message_id)] = {
            "channel_id": str(channel_id),
            "guild_id": str(guild_id),
            "prize": prize,
            "host_id": str(host_id),
            "end_time": end_time,
            "winners": winners,
            "participants": []
        }
        
        return self._save_data()
        
    def get_giveaway(self, message_id):
        """Get a giveaway by message ID"""
        if "giveaways" not in self.data:
            return None
            
        return self.data["giveaways"].get(str(message_id))
        
    def get_active_giveaways(self):
        """Get all active giveaways"""
        if "giveaways" not in self.data:
            return {}
            
        current_time = int(time.time())
        return {
            message_id: giveaway 
            for message_id, giveaway in self.data["giveaways"].items() 
            if giveaway["end_time"] > current_time
        }
        
    def add_giveaway_participant(self, message_id, user_id):
        """Add a participant to a giveaway"""
        giveaway = self.get_giveaway(message_id)
        if not giveaway:
            return False
            
        user_id = str(user_id)
        if user_id not in giveaway["participants"]:
            giveaway["participants"].append(user_id)
            return self._save_data()
        
        return True
        
    def end_giveaway(self, message_id):
        """End a giveaway and return the winners"""
        giveaway = self.get_giveaway(message_id)
        if not giveaway:
            return None
            
        # Remove the giveaway from active giveaways
        self.data["giveaways"].pop(str(message_id))
        self._save_data()
        
        return giveaway

# Create a global database instance
db = Database()