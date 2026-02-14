Sahar Sistani, [2/14/2026 3:11 PM]
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

Sahar Sistani, [2/14/2026 3:12 PM]
import requests
import sqlite3
import json
from datetime import datetime
from config import Config

class TMDBFetcher:
    def init(self):
        self.api_key = Config.TMDB_API_KEY
        self.base_url = 'https://api.themoviedb.org/3'
        self.conn = sqlite3.connect(Config.DATABASE_PATH, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY,
                title TEXT,
                overview TEXT,
                release_date TEXT,
                vote_average REAL,
                vote_count INTEGER,
                genres TEXT,
                poster_path TEXT,
                popularity REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                user_id INTEGER,
                movie_id INTEGER,
                rating REAL,
                timestamp INTEGER,
                brain_wave_type TEXT,
                FOREIGN KEY(movie_id) REFERENCES movies(id)
            )
        ''')
        self.conn.commit()
    
    def fetch_popular_movies(self, pages=5):
        movies = []
        for page in range(1, pages + 1):
            response = requests.get(
                f'{self.base_url}/movie/popular',
                params={'api_key': self.api_key, 'page': page}
            )
            if response.status_code == 200:
                movies.extend(response.json()['results'])
        return movies
    
    def fetch_movie_details(self, movie_id):
        response = requests.get(
            f'{self.base_url}/movie/{movie_id}',
            params={'api_key': self.api_key}
        )
        if response.status_code == 200:
            return response.json()
        return None
    
    def save_movies_to_db(self, movies):
        cursor = self.conn.cursor()
        for movie in movies:
            cursor.execute('''
                INSERT OR REPLACE INTO movies 
                (id, title, overview, release_date, vote_average, vote_count, genres, poster_path, popularity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                movie['id'],
                movie['title'],
                movie.get('overview', ''),
                movie.get('release_date', ''),
                movie.get('vote_average', 0),
                movie.get('vote_count', 0),
                json.dumps(movie.get('genre_ids', [])),
                movie.get('poster_path', ''),
                movie.get('popularity', 0)
            ))
        self.conn.commit()
    
    def generate_synthetic_ratings(self, num_users=100, ratings_per_user=20):
        import random
        import time
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM movies")
        movie_ids = [row[0] for row in cursor.fetchall()]
        
        brain_waves = ['alpha', 'beta', 'gamma', 'delta', 'theta']
        
        for user_id in range(1, num_users + 1):
            sampled_movies = random.sample(movie_ids, min(ratings_per_user, len(movie_ids)))
            for movie_id in sampled_movies:
                rating = random.uniform(0.5, 5.0)
                rating = round(rating * 2) / 2
                timestamp = int(time.time()) - random.randint(0, 31536000)
                brain_wave = random.choice(brain_waves)
                
                cursor.execute('''
                    INSERT INTO ratings (user_id, movie_id, rating, timestamp, brain_wave_type)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, movie_id, rating, timestamp, brain_wave))
        
        self.conn.commit()
