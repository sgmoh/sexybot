#!/bin/bash

# This script is used for deploying the Discord bot on Render
pip install discord.py python-dotenv psycopg2-binary sqlalchemy requests

# Start the bot
python main.py