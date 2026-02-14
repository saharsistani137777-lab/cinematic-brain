import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TMDB_API_KEY = os.getenv('TMDB_API_KEY', 'your_tmdb_api_key_here')
    DATABASE_PATH = 'movies.db'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-2026')
    DEBUG = True
    PORT = 5000
    HOST = '0.0.0.0'
