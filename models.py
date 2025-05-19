import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime, BigInteger, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Get the database URL from environment variables
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL environment variable not set")

# Create the SQLAlchemy engine
engine = create_engine(database_url)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Guild(Base):
    """Guild model for storing Discord server settings"""
    __tablename__ = 'guilds'
    
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    prefix = Column(String(10), default='.')
    autorole_id = Column(BigInteger, nullable=True)
    welcome_channel_id = Column(BigInteger, nullable=True)
    welcome_message = Column(Text, nullable=True)
    welcome_enabled = Column(Boolean, default=False)
    leveling_enabled = Column(Boolean, default=True)
    leveling_channel_id = Column(BigInteger, nullable=True)
    logging_enabled = Column(Boolean, default=False)
    logging_channel_id = Column(BigInteger, nullable=True)
    logging_events = Column(JSON, default=lambda: [])
    ticket_enabled = Column(Boolean, default=False)
    ticket_category_id = Column(BigInteger, nullable=True)
    ticket_channel_id = Column(BigInteger, nullable=True)
    ticket_message_id = Column(BigInteger, nullable=True)
    
    # Relationships
    users = relationship("User", back_populates="guild", cascade="all, delete-orphan")
    roles = relationship("Role", back_populates="guild", cascade="all, delete-orphan")
    giveaways = relationship("Giveaway", back_populates="guild", cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="guild", cascade="all, delete-orphan")
    reaction_roles = relationship("ReactionRole", back_populates="guild", cascade="all, delete-orphan")
    polls = relationship("Poll", back_populates="guild", cascade="all, delete-orphan")

class User(Base):
    """User model for storing user data per guild"""
    __tablename__ = 'users'
    
    id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey('guilds.id'), primary_key=True)
    xp = Column(Integer, default=0)
    level = Column(Integer, default=0)
    messages_count = Column(Integer, default=0)
    last_message_time = Column(DateTime, nullable=True)
    
    # Relationships
    guild = relationship("Guild", back_populates="users")
    tickets = relationship("Ticket", back_populates="user")

class Role(Base):
    """Role model for storing role settings"""
    __tablename__ = 'roles'
    
    id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey('guilds.id'))
    name = Column(String(255))
    level_requirement = Column(Integer, nullable=True)
    
    # Relationships
    guild = relationship("Guild", back_populates="roles")

class Giveaway(Base):
    """Giveaway model for storing giveaways"""
    __tablename__ = 'giveaways'
    
    message_id = Column(BigInteger, primary_key=True)
    channel_id = Column(BigInteger)
    guild_id = Column(BigInteger, ForeignKey('guilds.id'))
    host_id = Column(BigInteger)
    prize = Column(String(255))
    winners_count = Column(Integer, default=1)
    end_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    ended = Column(Boolean, default=False)
    participants = Column(JSON, default=lambda: [])
    
    # Relationships
    guild = relationship("Guild", back_populates="giveaways")

class Ticket(Base):
    """Ticket model for storing support tickets"""
    __tablename__ = 'tickets'
    
    channel_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey('guilds.id'))
    user_id = Column(BigInteger)  # Changed from foreign key to simple column
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    status = Column(String(20), default='open')
    
    # Relationships
    guild = relationship("Guild", back_populates="tickets")
    user = relationship("User", foreign_keys=[user_id, guild_id], 
                       primaryjoin="and_(Ticket.user_id == User.id, Ticket.guild_id == User.guild_id)", 
                       back_populates="tickets")

class ReactionRole(Base):
    """ReactionRole model for storing reaction roles"""
    __tablename__ = 'reaction_roles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, ForeignKey('guilds.id'))
    message_id = Column(BigInteger)
    channel_id = Column(BigInteger)
    emoji = Column(String(100))
    role_id = Column(BigInteger)  # Removed foreign key constraint
    
    # Relationships
    guild = relationship("Guild", back_populates="reaction_roles")
    # Removed role relationship

class Poll(Base):
    """Poll model for storing polls"""
    __tablename__ = 'polls'
    
    message_id = Column(BigInteger, primary_key=True)
    channel_id = Column(BigInteger)
    guild_id = Column(BigInteger, ForeignKey('guilds.id'))
    question = Column(Text)
    options = Column(JSON)
    votes = Column(JSON, default=lambda: {})
    end_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    ended = Column(Boolean, default=False)
    
    # Relationships
    guild = relationship("Guild", back_populates="polls")

def initialize_db():
    """Initialize the database by creating all tables"""
    Base.metadata.create_all(engine)

def get_session():
    """Get a new database session"""
    return Session()

# Initialize the database when the module is imported
initialize_db()