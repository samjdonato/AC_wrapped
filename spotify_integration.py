
# Spotify API Integration Template
# Prerequisites: 
# 1. Create Spotify Developer account
# 2. Create an app to get client_id and client_secret
# 3. Install spotipy: pip install spotipy

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

class SpotifyEnricher:
    def __init__(self, client_id, client_secret):
        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
        )
    
    def get_album_details(self, artist_name, album_name):
        # Search for album
        results = self.sp.search(
            q=f"artist:{artist_name} album:{album_name}", 
            type='album', 
            limit=1
        )
        
        if results['albums']['items']:
            album = results['albums']['items'][0]
            album_id = album['id']
            
            # Get full album details
            album_info = self.sp.album(album_id)
            tracks = self.sp.album_tracks(album_id)
            
            # Calculate total duration
            total_ms = sum(track['duration_ms'] for track in tracks['items'])
            total_minutes = total_ms / 1000 / 60
            
            # Get audio features for all tracks
            track_ids = [track['id'] for track in tracks['items']]
            audio_features = self.sp.audio_features(track_ids)
            
            # Calculate average features
            avg_features = {
                'danceability': 0,
                'energy': 0,
                'valence': 0,  # musical positivity
                'acousticness': 0,
                'instrumentalness': 0
            }
            
            valid_tracks = [f for f in audio_features if f]
            for features in valid_tracks:
                for key in avg_features:
                    avg_features[key] += features[key]
            
            for key in avg_features:
                avg_features[key] /= len(valid_tracks)
            
            return {
                'spotify_album_id': album_id,
                'release_date_precision': album['release_date_precision'],
                'total_tracks': album['total_tracks'],
                'duration_minutes': round(total_minutes, 1),
                'popularity': album['popularity'],
                'avg_danceability': round(avg_features['danceability'], 3),
                'avg_energy': round(avg_features['energy'], 3),
                'avg_valence': round(avg_features['valence'], 3),
                'avg_acousticness': round(avg_features['acousticness'], 3),
                'avg_instrumentalness': round(avg_features['instrumentalness'], 3),
                'label': album.get('label', 'Unknown'),
                'spotify_url': album['external_urls']['spotify']
            }
        
        return None

# Usage example:
# enricher = SpotifyEnricher('your_client_id', 'your_client_secret')
# album_data = enricher.get_album_details('B.B. King', 'Live At The Regal')
