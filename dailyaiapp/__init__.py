import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# Initialize application
app = Flask(__name__, static_folder='static')

# Import the application views
from dailyaiapp import news_feed_views
