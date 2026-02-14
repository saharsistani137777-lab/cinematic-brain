import numpy as np
import pandas as pd
from surprise import SVD, Dataset, Reader
from surprise.model_selection import train_test_split
from surprise import accuracy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json

class HybridRecommender:
    def init(self, db_manager):
        self.db = db_manager
        self.svd_model = None
        self.movies_df = None
        self.ratings_df = None
        self.tfidf_matrix = None
        self.cosine_sim = None
        
    def load_data(self):
        self.movies_df = self.db.get_all_movies()
        self.ratings_df = self.db.get_all_ratings()
        
        self.movies_df['genres'] = self.movies_df['genres'].apply(
            lambda x: ' '.join([str(g) for g in json.loads(x)]) if x else ''
        )
        
    def train_collaborative(self):
        reader = Reader(rating_scale=(0.5, 5.0))
        data = Dataset.load_from_df(
            self.ratings_df[['user_id', 'movie_id', 'rating']], 
            reader
        )
        
        trainset, testset = train_test_split(data, test_size=0.2, random_state=42)
        
        self.svd_model = SVD(n_factors=100, n_epochs=20, random_state=42)
        self.svd_model.fit(trainset)
        
        predictions = self.svd_model.test(testset)
        rmse = accuracy.rmse(predictions)
        
        return rmse
    
    def prepare_content_features(self):
        tfidf = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = tfidf.fit_transform(
            self.movies_df['genres'] + ' ' + self.movies_df['overview'].fillna('')
        )
        self.cosine_sim = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)
    
    def get_content_recommendations(self, movie_id, n=10):
        if self.cosine_sim is None:
            self.prepare_content_features()
        
        idx = self.movies_df[self.movies_df['id'] == movie_id].index[0]
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:n+1]
        movie_indices = [i[0] for i in sim_scores]
        
        return self.movies_df.iloc[movie_indices][['id', 'title', 'vote_average']]
    
    def get_collaborative_recommendations(self, user_id, n=10):
        if self.svd_model is None:
            self.train_collaborative()
        
        all_movies = self.movies_df['id'].tolist()
        user_rated = self.ratings_df[self.ratings_df['user_id'] == user_id]['movie_id'].tolist()
        unrated = [m for m in all_movies if m not in user_rated]
        
        predictions = []
        for movie_id in unrated:
            pred = self.svd_model.predict(user_id, movie_id)
            predictions.append((movie_id, pred.est))
        
        predictions.sort(key=lambda x: x[1], reverse=True)
        top_movies = [p[0] for p in predictions[:n]]
        
        return self.movies_df[self.movies_df['id'].isin(top_movies)][['id', 'title', 'vote_average']]
    
    def hybrid_recommend(self, user_id, movie_id=None, n=10, alpha=0.5):
        if movie_id:
            content_recs = self.get_content_recommendations(movie_id, n*2)
            collab_recs = self.get_collaborative_recommendations(user_id, n*2)
            
            content_ids = set(content_recs['id'].tolist())
            collab_ids = set(collab_recs['id'].tolist())
            
            hybrid_ids = list(content_ids.intersection(collab_ids))
            
            if len(hybrid_ids) < n:
                remaining = n - len(hybrid_ids)
                more_content = [m for m in content_ids if m not in hybrid_ids][:remaining//2]
                more_collab = [m for m in collab_ids if m not in hybrid_ids][:remaining//2]
                hybrid_ids.extend(more_content)
hybrid_ids.extend(more_collab)
            
            return self.movies_df[self.movies_df['id'].isin(hybrid_ids[:n])]
        else:
            return self.get_collaborative_recommendations(user_id, n)
    
    def get_brain_wave_recommendations(self, user_id, brain_wave_type, n=10):
        wave_ratings = self.ratings_df[
            (self.ratings_df['brain_wave_type'] == brain_wave_type) & 
            (self.ratings_df['rating'] >= 4.0)
        ]
        
        if len(wave_ratings) > 0:
            top_movies = wave_ratings.groupby('movie_id').size().sort_values(ascending=False).head(n).index
            return self.movies_df[self.movies_df['id'].isin(top_movies)]
        else:
            return self.get_collaborative_recommendations(user_id, n)
