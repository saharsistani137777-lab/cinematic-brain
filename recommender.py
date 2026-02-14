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
