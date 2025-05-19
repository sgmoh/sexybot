import os
import logging
import time
from datetime import datetime
import json
from sqlalchemy.exc import SQLAlchemyError
from models import get_session, Guild, User, Role, Giveaway, Ticket, ReactionRole, Poll

# Set up logging
logger = logging.getLogger('discord_bot')

class PostgresDatabase:
    """PostgreSQL database handler for the Discord bot"""
    
    def __init__(self, json_backup_path='bot_database.json'):
        """Initialize the database connection"""
        self.json_backup_path = json_backup_path
        self._migrate_json_if_needed()
    
    def _migrate_json_if_needed(self):
        """Migrate data from JSON to PostgreSQL if needed"""
        try:
            if not os.path.exists(self.json_backup_path):
                logger.info("No JSON database to migrate")
                return
                
            # Check if the database already has data
            session = get_session()
            guild_count = session.query(Guild).count()
            session.close()
            
            if guild_count > 0:
                logger.info("PostgreSQL database already contains data, skipping migration")
                return
                
            logger.info("Starting migration from JSON to PostgreSQL")
            with open(self.json_backup_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Start a new session for the migration
            session = get_session()
            
            try:
                # Process guild data
                if "autoroles" in data:
                    for guild_id, role_id in data["autoroles"].items():
                        guild = Guild(
                            id=int(guild_id),
                            autorole_id=int(role_id) if role_id else None
                        )
                        session.merge(guild)
                
                # Process user/level data
                if "levels" in data:
                    for guild_id, users in data["levels"].items():
                        for user_id, user_data in users.items():
                            user = User(
                                id=int(user_id),
                                guild_id=int(guild_id),
                                xp=user_data.get("xp", 0),
                                level=user_data.get("level", 0)
                            )
                            session.merge(user)
                
                # Process ticket data
                if "tickets" in data:
                    for guild_id, tickets in data["tickets"].items():
                        for channel_id, ticket_data in tickets.items():
                            ticket = Ticket(
                                channel_id=int(channel_id),
                                guild_id=int(guild_id),
                                user_id=int(ticket_data.get("user_id", 0)),
                                created_at=datetime.fromisoformat(ticket_data.get("created_at", datetime.utcnow().isoformat())),
                                closed_at=datetime.fromisoformat(ticket_data.get("closed_at")) if ticket_data.get("closed_at") else None,
                                status=ticket_data.get("status", "open")
                            )
                            session.merge(ticket)
                
                # Process message counts
                if "message_counts" in data:
                    for guild_id, users in data["message_counts"].items():
                        for user_id, message_data in users.items():
                            user = session.query(User).filter_by(
                                id=int(user_id),
                                guild_id=int(guild_id)
                            ).first()
                            
                            if not user:
                                user = User(
                                    id=int(user_id),
                                    guild_id=int(guild_id)
                                )
                                session.add(user)
                                
                            user.messages_count = message_data.get("all_time", 0)
                
                # Process giveaways
                if "giveaways" in data:
                    for message_id, giveaway_data in data["giveaways"].items():
                        end_time = datetime.fromtimestamp(giveaway_data.get("end_time", int(time.time())))
                        
                        giveaway = Giveaway(
                            message_id=int(message_id),
                            channel_id=int(giveaway_data.get("channel_id", 0)),
                            guild_id=int(giveaway_data.get("guild_id", 0)),
                            host_id=int(giveaway_data.get("host_id", 0)),
                            prize=giveaway_data.get("prize", ""),
                            winners_count=giveaway_data.get("winners", 1),
                            end_time=end_time,
                            participants=[int(p) for p in giveaway_data.get("participants", [])]
                        )
                        session.merge(giveaway)
                
                # Commit the changes
                session.commit()
                logger.info("Successfully migrated data from JSON to PostgreSQL")
                
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Error during migration: {e}")
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Failed to migrate JSON data to PostgreSQL: {e}")
    
    # Autorole methods
    def get_autorole(self, guild_id):
        """Get the autorole for a guild"""
        session = get_session()
        try:
            guild = session.query(Guild).filter_by(id=guild_id).first()
            return str(guild.autorole_id) if guild and guild.autorole_id else None
        except SQLAlchemyError as e:
            logger.error(f"Database error getting autorole: {e}")
            return None
        finally:
            session.close()
    
    def set_autorole(self, guild_id, role_id):
        """Set the autorole for a guild"""
        session = get_session()
        try:
            guild = session.query(Guild).filter_by(id=guild_id).first()
            if not guild:
                guild = Guild(id=guild_id)
                session.add(guild)
            
            guild.autorole_id = int(role_id)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error setting autorole: {e}")
            return False
        finally:
            session.close()
    
    def remove_autorole(self, guild_id):
        """Remove the autorole for a guild"""
        session = get_session()
        try:
            guild = session.query(Guild).filter_by(id=guild_id).first()
            if guild and guild.autorole_id:
                guild.autorole_id = None
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error removing autorole: {e}")
            return False
        finally:
            session.close()
    
    # Welcome message methods
    def get_welcome_settings(self, guild_id):
        """Get welcome settings for a guild"""
        session = get_session()
        try:
            guild = session.query(Guild).filter_by(id=guild_id).first()
            if not guild:
                return {
                    "enabled": False,
                    "channel_id": None,
                    "message": "Welcome {user} to {server}!"
                }
            
            return {
                "enabled": guild.welcome_enabled,
                "channel_id": str(guild.welcome_channel_id) if guild.welcome_channel_id else None,
                "message": guild.welcome_message or "Welcome {user} to {server}!"
            }
        except SQLAlchemyError as e:
            logger.error(f"Database error getting welcome settings: {e}")
            return {
                "enabled": False,
                "channel_id": None,
                "message": "Welcome {user} to {server}!"
            }
        finally:
            session.close()
    
    def set_welcome_settings(self, guild_id, enabled=None, channel_id=None, message=None):
        """Set welcome settings for a guild"""
        session = get_session()
        try:
            guild = session.query(Guild).filter_by(id=guild_id).first()
            if not guild:
                guild = Guild(id=guild_id)
                session.add(guild)
            
            if enabled is not None:
                guild.welcome_enabled = enabled
            if channel_id is not None:
                guild.welcome_channel_id = int(channel_id) if channel_id else None
            if message is not None:
                guild.welcome_message = message
            
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error setting welcome settings: {e}")
            return False
        finally:
            session.close()
    
    # XP and leveling methods
    def get_xp(self, user_id, guild_id):
        """Get a user's XP in a guild"""
        session = get_session()
        try:
            user = session.query(User).filter_by(id=user_id, guild_id=guild_id).first()
            if not user:
                return {
                    "xp": 0,
                    "level": 0,
                    "last_message_time": 0
                }
            
            return {
                "xp": user.xp,
                "level": user.level,
                "last_message_time": int(user.last_message_time.timestamp()) if user.last_message_time else 0
            }
        except SQLAlchemyError as e:
            logger.error(f"Database error getting XP: {e}")
            return {
                "xp": 0,
                "level": 0,
                "last_message_time": 0
            }
        finally:
            session.close()
    
    def add_xp(self, user_id, guild_id, xp_amount):
        """Add XP to a user in a guild, returns new level if leveled up"""
        import math
        
        session = get_session()
        try:
            user = session.query(User).filter_by(id=user_id, guild_id=guild_id).first()
            if not user:
                user = User(id=user_id, guild_id=guild_id, xp=0, level=0)
                session.add(user)
            
            old_level = user.level
            user.xp += xp_amount
            
            # Calculate new level based on total XP
            # Formula: level = sqrt(total_xp / 100)
            new_level = math.floor(math.sqrt(user.xp / 100))
            user.level = new_level
            
            session.commit()
            
            # Return the new level if leveled up, otherwise None
            if new_level > old_level:
                return new_level
            return None
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error adding XP: {e}")
            return None
        finally:
            session.close()
    
    def set_last_message_time(self, user_id, guild_id, timestamp):
        """Set the last message time for XP cooldown"""
        session = get_session()
        try:
            user = session.query(User).filter_by(id=user_id, guild_id=guild_id).first()
            if not user:
                user = User(id=user_id, guild_id=guild_id, xp=0, level=0)
                session.add(user)
            
            user.last_message_time = datetime.fromtimestamp(timestamp)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error setting last message time: {e}")
            return False
        finally:
            session.close()
    
    def get_level_settings(self, guild_id):
        """Get level settings for a guild"""
        session = get_session()
        try:
            guild = session.query(Guild).filter_by(id=guild_id).first()
            if not guild:
                return {
                    "enabled": True,
                    "channel_id": None,
                    "roles": {}
                }
            
            # Get level roles
            roles = session.query(Role).filter_by(guild_id=guild_id).filter(Role.level_requirement != None).all()
            level_roles = {str(role.level_requirement): str(role.id) for role in roles if role.level_requirement}
            
            return {
                "enabled": guild.leveling_enabled,
                "channel_id": str(guild.leveling_channel_id) if guild.leveling_channel_id else None,
                "roles": level_roles
            }
        except SQLAlchemyError as e:
            logger.error(f"Database error getting level settings: {e}")
            return {
                "enabled": True,
                "channel_id": None,
                "roles": {}
            }
        finally:
            session.close()
    
    def set_level_settings(self, guild_id, enabled=None, channel_id=None, roles=None):
        """Set level settings for a guild"""
        session = get_session()
        try:
            guild = session.query(Guild).filter_by(id=guild_id).first()
            if not guild:
                guild = Guild(id=guild_id)
                session.add(guild)
            
            if enabled is not None:
                guild.leveling_enabled = enabled
            if channel_id is not None:
                guild.leveling_channel_id = int(channel_id) if channel_id else None
            
            if roles is not None:
                # Clear existing level roles
                session.query(Role).filter_by(guild_id=guild_id).filter(Role.level_requirement != None).delete()
                
                # Add new level roles
                for level, role_id in roles.items():
                    role = Role(
                        id=int(role_id),
                        guild_id=guild_id,
                        level_requirement=int(level)
                    )
                    session.add(role)
            
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error setting level settings: {e}")
            return False
        finally:
            session.close()
    
    # Message tracking methods
    def increment_message_count(self, guild_id, user_id):
        """Increment message count for a user in a guild"""
        session = get_session()
        try:
            user = session.query(User).filter_by(id=user_id, guild_id=guild_id).first()
            if not user:
                user = User(id=user_id, guild_id=guild_id, messages_count=0)
                session.add(user)
            
            user.messages_count += 1
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error incrementing message count: {e}")
            return False
        finally:
            session.close()
    
    def get_message_count(self, guild_id, user_id):
        """Get message count for a user in a guild"""
        session = get_session()
        try:
            user = session.query(User).filter_by(id=user_id, guild_id=guild_id).first()
            return user.messages_count if user else 0
        except SQLAlchemyError as e:
            logger.error(f"Database error getting message count: {e}")
            return 0
        finally:
            session.close()
    
    def get_top_users_by_messages(self, guild_id, limit=10):
        """Get top users by message count in a guild"""
        session = get_session()
        try:
            users = session.query(User).filter_by(guild_id=guild_id).order_by(User.messages_count.desc()).limit(limit).all()
            return [(str(user.id), user.messages_count) for user in users]
        except SQLAlchemyError as e:
            logger.error(f"Database error getting top users: {e}")
            return []
        finally:
            session.close()
    
    # Giveaway methods
    def create_giveaway(self, message_id, channel_id, guild_id, prize, host_id, end_time, winners=1):
        """Create a new giveaway"""
        session = get_session()
        try:
            giveaway = Giveaway(
                message_id=message_id,
                channel_id=channel_id,
                guild_id=guild_id,
                host_id=host_id,
                prize=prize,
                winners_count=winners,
                end_time=datetime.fromtimestamp(end_time),
                participants=[]
            )
            session.add(giveaway)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error creating giveaway: {e}")
            return False
        finally:
            session.close()
    
    def get_giveaway(self, message_id):
        """Get a giveaway by message ID"""
        session = get_session()
        try:
            giveaway = session.query(Giveaway).filter_by(message_id=message_id).first()
            if not giveaway:
                return None
                
            return {
                "channel_id": str(giveaway.channel_id),
                "guild_id": str(giveaway.guild_id),
                "prize": giveaway.prize,
                "host_id": str(giveaway.host_id),
                "end_time": int(giveaway.end_time.timestamp()),
                "winners": giveaway.winners_count,
                "participants": [str(p) for p in giveaway.participants]
            }
        except SQLAlchemyError as e:
            logger.error(f"Database error getting giveaway: {e}")
            return None
        finally:
            session.close()
    
    def get_active_giveaways(self):
        """Get all active giveaways"""
        session = get_session()
        try:
            current_time = datetime.utcnow()
            giveaways = session.query(Giveaway).filter(Giveaway.end_time > current_time, Giveaway.ended == False).all()
            
            result = {}
            for giveaway in giveaways:
                result[str(giveaway.message_id)] = {
                    "channel_id": str(giveaway.channel_id),
                    "guild_id": str(giveaway.guild_id),
                    "prize": giveaway.prize,
                    "host_id": str(giveaway.host_id),
                    "end_time": int(giveaway.end_time.timestamp()),
                    "winners": giveaway.winners_count,
                    "participants": [str(p) for p in giveaway.participants]
                }
            
            return result
        except SQLAlchemyError as e:
            logger.error(f"Database error getting active giveaways: {e}")
            return {}
        finally:
            session.close()
    
    def add_giveaway_participant(self, message_id, user_id):
        """Add a participant to a giveaway"""
        session = get_session()
        try:
            giveaway = session.query(Giveaway).filter_by(message_id=message_id).first()
            if not giveaway:
                return False
                
            if int(user_id) not in giveaway.participants:
                giveaway.participants.append(int(user_id))
                session.commit()
            
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error adding giveaway participant: {e}")
            return False
        finally:
            session.close()
    
    def end_giveaway(self, message_id):
        """End a giveaway and return the winners"""
        session = get_session()
        try:
            giveaway = session.query(Giveaway).filter_by(message_id=message_id).first()
            if not giveaway:
                return None
                
            giveaway.ended = True
            session.commit()
            
            return {
                "channel_id": str(giveaway.channel_id),
                "guild_id": str(giveaway.guild_id),
                "prize": giveaway.prize,
                "host_id": str(giveaway.host_id),
                "end_time": int(giveaway.end_time.timestamp()),
                "winners": giveaway.winners_count,
                "participants": [str(p) for p in giveaway.participants]
            }
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error ending giveaway: {e}")
            return None
        finally:
            session.close()
    
    # Poll methods
    def create_poll(self, message_id, guild_id, channel_id, question, options, end_time=None):
        """Create a new poll"""
        session = get_session()
        try:
            poll = Poll(
                message_id=message_id,
                guild_id=guild_id,
                channel_id=channel_id,
                question=question,
                options=options,
                votes={},
                end_time=datetime.fromtimestamp(end_time) if end_time else None
            )
            session.add(poll)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error creating poll: {e}")
            return False
        finally:
            session.close()
    
    def get_poll(self, message_id, guild_id):
        """Get a poll by message ID"""
        session = get_session()
        try:
            poll = session.query(Poll).filter_by(message_id=message_id, guild_id=guild_id).first()
            if not poll:
                return None
                
            return {
                "channel_id": str(poll.channel_id),
                "question": poll.question,
                "options": poll.options,
                "votes": poll.votes,
                "end_time": int(poll.end_time.timestamp()) if poll.end_time else None
            }
        except SQLAlchemyError as e:
            logger.error(f"Database error getting poll: {e}")
            return None
        finally:
            session.close()
    
    def add_poll_vote(self, message_id, guild_id, user_id, option_index):
        """Add a vote to a poll"""
        session = get_session()
        try:
            poll = session.query(Poll).filter_by(message_id=message_id, guild_id=guild_id).first()
            if not poll:
                return False
                
            # Remove existing vote if any
            for option in poll.votes:
                if str(user_id) in poll.votes[option]:
                    poll.votes[option].remove(str(user_id))
            
            # Add the new vote
            option_str = str(option_index)
            if option_str not in poll.votes:
                poll.votes[option_str] = []
            
            poll.votes[option_str].append(str(user_id))
            session.commit()
            
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error adding poll vote: {e}")
            return False
        finally:
            session.close()
    
    def end_poll(self, message_id, guild_id):
        """End a poll and return the results"""
        session = get_session()
        try:
            poll = session.query(Poll).filter_by(message_id=message_id, guild_id=guild_id).first()
            if not poll:
                return None
                
            results = []
            for i, option in enumerate(poll.options):
                vote_count = len(poll.votes.get(str(i), []))
                results.append((option, vote_count))
            
            # Mark the poll as ended
            poll.ended = True
            session.commit()
            
            return results
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error ending poll: {e}")
            return None
        finally:
            session.close()

# Create a global database instance
db = PostgresDatabase()