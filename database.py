import sqlite3
import pandas as pd
import time
from contextlib import contextmanager

class DatabaseManager:
    def init(self, db_path='movies.db'):
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def get_all_movies(self):
        with self.get_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM movies", conn)
        return df
    
    def get_all_ratings(self):
        with self.get_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM ratings", conn)
        return df
    
    def get_user_ratings(self, user_id):
        with self.get_connection() as conn:
            df = pd.read_sql_query(
                f"SELECT * FROM ratings WHERE user_id = {user_id}", 
                conn
            )
        return df
    
    def get_movie_by_id(self, movie_id):
        with self.get_connection() as conn:
            df = pd.read_sql_query(
                f"SELECT * FROM movies WHERE id = {movie_id}", 
                conn
            )
        return df.iloc[0] if not df.empty else None
    
    def add_rating(self, user_id, movie_id, rating, brain_wave):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO ratings (user_id, movie_id, rating, timestamp, brain_wave_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, movie_id, rating, int(time.time()), brain_wave))
            conn.commit()
