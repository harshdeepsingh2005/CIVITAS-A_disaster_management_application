import sys
import os

# Add parent directory to the path so we can import the main app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel expects a WSGI callable named `app`
# app is already the Flask application object
