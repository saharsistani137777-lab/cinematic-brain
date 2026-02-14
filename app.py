from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import sqlite3
import random

from config import Config
from database import DatabaseManager
from data_fetcher import TMDBFetcher
from recommender import HybridRecommender
from brain_visualizer import BrainVisualizer

app = Flask(name, static_url_path='', static_folder='.')
app.config.from_object(Config)
CORS(app)

db_manager = DatabaseManager(Config.DATABASE_PATH)
fetcher = TMDBFetcher()
recommender = HybridRecommender(db_manager)
visualizer = BrainVisualizer()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

@app.route('/api/init', methods=['GET'])
def initialize():
    try:
        movies = fetcher.fetch_popular_movies(pages=3)
        fetcher.save_movies_to_db(movies)
        
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM ratings")
        count = cursor.fetchone()[0]
        conn.close()
        
        if count == 0:
            fetcher.generate_synthetic_ratings(num_users=50, ratings_per_user=15)
        
        recommender.load_data()
        recommender.train_collaborative()
        recommender.prepare_content_features()
        
        return jsonify({'status': 'success', 'message': 'System initialized'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/movies/popular', methods=['GET'])
def get_popular_movies():
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        conn = sqlite3.connect(Config.DATABASE_PATH)
        df = conn.execute(
            "SELECT * FROM movies ORDER BY popularity DESC LIMIT ? OFFSET ?",
            (limit, (page-1)*limit)
        ).fetchall()
        conn.close()
        
        movies = []
        for row in df:
            movies.append({
                'id': row[0],
                'title': row[1],
                'overview': row[2][:200] + '...' if len(row[2]) > 200 else row[2],
                'release_date': row[3],
                'rating': row[4],
                'poster': f"https://image.tmdb.org/t/p/w500{row[7]}" if row[7] else None
            })
        
        return jsonify({'movies': movies})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommend/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    try:
        movie_id = request.args.get('movie_id', type=int)
        n = request.args.get('n', 10, type=int)
        
        recommender.load_data()
        
        if movie_id:
            recommendations = recommender.hybrid_recommend(user_id, movie_id, n)
        else:
            recommendations = recommender.get_collaborative_recommendations(user_id, n)
        
        result = []
        for _, movie in recommendations.iterrows():
            result.append({
                'id': int(movie['id']),
                'title': movie['title'],
                'rating': float(movie['vote_average'])
            })
        
        return jsonify({'recommendations': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/brain/analyze/<int:movie_id>', methods=['GET'])
def analyze_brain(movie_id):
    try:
        user_id = request.args.get('user_id', 1, type=int)
        
        brain_data = visualizer.create_brain_visualization(movie_id, user_id)
        activity = visualizer.generate_brain_activity(movie_id, user_id)
        wave_type, mood = visualizer.analyze_brain_wave(activity)
        
        return jsonify({
            'visualization': json.loads(brain_data),
            'activity': activity,
            'wave_type': wave_type,
            'mood': mood
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
     @app.route('/api/brain/recommend/<int:user_id>', methods=['GET'])
def get_brain_recommendations(user_id):
    try:
        wave_type = request.args.get('wave', 'alpha')
        n = request.args.get('n', 10, type=int)
        
        recommender.load_data()
        recommendations = recommender.get_brain_wave_recommendations(user_id, wave_type, n)
        
        result = []
        for _, movie in recommendations.iterrows():
            result.append({
                'id': int(movie['id']),
                'title': movie['title'],
                'rating': float(movie['vote_average'])
            })
        
        return jsonify({'recommendations': result, 'wave': wave_type})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rate', methods=['POST'])
def rate_movie():
    try:
        data = request.json
        user_id = data.get('user_id')
        movie_id = data.get('movie_id')
        rating = data.get('rating')
        brain_wave = data.get('brain_wave', 'alpha')
        
        db_manager.add_rating(user_id, movie_id, rating, brain_wave)
        
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if name == 'main':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG) 
