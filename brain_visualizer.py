import numpy as np
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import json
import random

class BrainVisualizer:
    def init(self):
        self.brain_regions = {
            'prefrontal': {'color': '#ff6b6b', 'activity': 0.5},
            'motor': {'color': '#4ecdc4', 'activity': 0.3},
            'sensory': {'color': '#45b7d1', 'activity': 0.4},
            'visual': {'color': '#96ceb4', 'activity': 0.7},
            'auditory': {'color': '#ffeaa7', 'activity': 0.2},
            'limbic': {'color': '#dfe6e9', 'activity': 0.6}
        }
        
    def generate_brain_activity(self, movie_id, user_id=None):
        activity = {}
        for region in self.brain_regions:
            base = self.brain_regions[region]['activity']
            noise = random.uniform(-0.2, 0.2)
            activity[region] = max(0, min(1, base + noise))
        return activity
    
    def create_brain_visualization(self, movie_id, user_id=None):
        activity = self.generate_brain_activity(movie_id, user_id)
        
        theta = np.linspace(0, 2*np.pi, 100)
        phi = np.linspace(0, np.pi, 100)
        theta, phi = np.meshgrid(theta, phi)
        
        r = 10
        x = r * np.sin(phi) * np.cos(theta)
        y = r * np.sin(phi) * np.sin(theta)
        z = r * np.cos(phi)
        
        activity_values = []
        for region, value in activity.items():
            region_size = value * 100
            activity_values.append(region_size)
        
        fig = go.Figure()
        
        fig.add_trace(go.Surface(
            x=x, y=y, z=z,
            opacity=0.3,
            colorscale='gray',
            showscale=False,
            name='Brain Structure'
        ))
        
        colors = [self.brain_regions[r]['color'] for r in activity.keys()]
        
        region_coords = [
            (5, 5, 5), (-5, 5, 5), (5, -5, 5),
            (-5, -5, 5), (5, 5, -5), (-5, 5, -5)
        ]
        
        for i, (region, coord) in enumerate(zip(activity.keys(), region_coords)):
            value = activity[region]
            size = 2 + value * 3
            
            fig.add_trace(go.Scatter3d(
                x=[coord[0]], y=[coord[1]], z=[coord[2]],
                mode='markers',
                marker=dict(
                    size=size * 3,
                    color=self.brain_regions[region]['color'],
                    opacity=0.8,
                    symbol='circle'
                ),
                name=region,
                text=f'{region}: {value:.2f}',
                hoverinfo='text'
            ))
            
            pulse_x = [coord[0] + np.sin(t) * value * 2 for t in np.linspace(0, 2*np.pi, 20)]
            pulse_y = [coord[1] + np.cos(t) * value * 2 for t in np.linspace(0, 2*np.pi, 20)]
            pulse_z = [coord[2] + np.sin(t*2) * value for t in np.linspace(0, 2*np.pi, 20)]
            
            fig.add_trace(go.Scatter3d(
                x=pulse_x, y=pulse_y, z=pulse_z,
                mode='lines',
                line=dict(
                    color=self.brain_regions[region]['color'],
                    width=2,
                    dash='dot'
                ),
                showlegend=False,
                hoverinfo='none'
            ))
        
        fig.update_layout(
            title={
                'text': ' Brain Activity Visualization',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24, 'color': 'white'}
            },
            scene=dict(
                xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, visible=False),
                yaxis=dict(showticklabels=False, showgrid=False, zeroline=False, visible=False),
                zaxis=dict(showticklabels=False, showgrid=False, zeroline=False, visible=False),
             bgcolor='black'
            ),
            paper_bgcolor='black',
            font={'color': 'white'},
            showlegend=True,
            legend=dict(
                x=0.02,
                y=0.98,
                bgcolor='rgba(0,0,0,0.7)',
                bordercolor='white',
                borderwidth=1
            )
        )
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)
    
    def analyze_brain_wave(self, activity_data):
        dominant_region = max(activity_data, key=activity_data.get)
        
        if dominant_region == 'prefrontal':
            return 'alpha', 'You need a thought-provoking movie'
        elif dominant_region == 'limbic':
            return 'gamma', 'You want emotional experience'
        elif dominant_region == 'visual':
            return 'beta', 'You want visually stunning cinema'
        elif dominant_region == 'auditory':
            return 'delta', 'Music and sound matter to you'
        else:
            return 'theta', 'You want something relaxing' 
