import pandas as pd
import requests
from datetime import datetime
import json

class AlbumDataEnrichment:
    """
    Suggestions for additional data collection and enrichment
    """
    
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)
        self.spotify_base_url = "https://api.spotify.com/v1"
        
    def suggest_additional_data_points(self):
        """Generate suggestions for easy-to-gather additional data"""
        
        suggestions = {
            "easy_manual_additions": {
                "album_length_minutes": {
                    "description": "Total runtime of each album",
                    "value": "Quick to find on Spotify/Apple Music",
                    "insight": "Analyze listening commitment, find sweet spot lengths"
                },
                "track_count": {
                    "description": "Number of tracks per album",
                    "value": "Easy to count",
                    "insight": "Compare EP vs LP preferences"
                },
                "member_rating": {
                    "description": "1-10 rating from each member who listened",
                    "value": "Quick post-discussion survey",
                    "insight": "Find consensus favorites, most divisive albums"
                },
                "discussion_attendance": {
                    "description": "Which members attended each discussion",
                    "value": "Simple yes/no per member",
                    "insight": "Engagement tracking, favorite discussion albums"
                },
                "favorite_track": {
                    "description": "Each member's standout track",
                    "value": "Collected during discussion",
                    "insight": "Create ultimate playlist, track preferences"
                }
            },
            
            "spotify_playlist_data": {
                "playlist_order": {
                    "description": "Order albums appear in monthly playlist",
                    "value": "Document when creating playlist",
                    "insight": "See if order affects reception"
                },
                "date_added_to_playlist": {
                    "description": "When each album was added",
                    "value": "Available in Spotify playlist history",
                    "insight": "Track procrastination patterns"
                }
            },
            
            "discussion_metrics": {
                "discussion_duration": {
                    "description": "How long you discussed each album",
                    "value": "Rough estimate in minutes",
                    "insight": "Which albums sparked most conversation"
                },
                "key_themes": {
                    "description": "Main discussion points (production, lyrics, nostalgia, etc)",
                    "value": "Quick tags during/after discussion",
                    "insight": "What drives your group's engagement"
                },
                "introduced_new_artist": {
                    "description": "Was this a discovery for most members?",
                    "value": "Simple yes/no",
                    "insight": "Discovery vs nostalgia balance"
                }
            },
            
            "contextual_data": {
                "why_selected": {
                    "description": "Brief reason for selection",
                    "value": "One sentence when submitting",
                    "insight": "Selection motivations over time"
                },
                "pre_listen_familiarity": {
                    "description": "How well selector knew album (new/heard/favorite)",
                    "value": "Simple category",
                    "insight": "Risk-taking vs comfort picks"
                },
                "would_recommend_after": {
                    "description": "Would you recommend after group listen?",
                    "value": "Yes/Maybe/No",
                    "insight": "Which albums grew on people"
                }
            }
        }
        
        return suggestions
    
    def generate_collection_template(self):
        """Create a CSV template for collecting additional data"""
        
        # Create base template with existing data
        template_df = self.df.copy()
        
        # Add suggested new columns
        new_columns = [
            'album_length_minutes',
            'track_count',
            'avg_member_rating',
            'discussion_attendance_count',
            'standout_tracks',
            'discussion_themes',
            'new_discovery_for_most',
            'selector_familiarity',
            'would_recommend'
        ]
        
        for col in new_columns:
            template_df[col] = ''
        
        # Add sample data for first row to show format
        if len(template_df) > 0:
            template_df.loc[0, 'album_length_minutes'] = '45'
            template_df.loc[0, 'track_count'] = '12'
            template_df.loc[0, 'avg_member_rating'] = '7.5'
            template_df.loc[0, 'discussion_attendance_count'] = '4'
            template_df.loc[0, 'standout_tracks'] = 'Track 3, Track 7'
            template_df.loc[0, 'discussion_themes'] = 'production, nostalgia'
            template_df.loc[0, 'new_discovery_for_most'] = 'Yes'
            template_df.loc[0, 'selector_familiarity'] = 'Heard before'
            template_df.loc[0, 'would_recommend'] = 'Yes'
        
        return template_df
    
    def generate_spotify_api_template(self):
        """
        Template code for Spotify API integration
        Note: Requires Spotify Developer account and API credentials
        """
        
        template = '''
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
'''
        return template
    
    def create_enhanced_analytics(self):
        """Generate ideas for enhanced analytics with additional data"""
        
        analytics_ideas = {
            "Temporal Analysis": [
                "Album length trends over club lifetime",
                "Rating patterns by season/month",
                "Evolution of genre preferences",
                "New discovery rate over time"
            ],
            
            "Member Insights": [
                "Consistency score (rating variance per member)",
                "Discovery champion (who brings most new artists)",
                "Crowd pleaser (highest average ratings)",
                "Genre explorer (most diverse selections)",
                "Engagement score (attendance + participation)"
            ],
            
            "Album Insights": [
                "Sleeper hits (low familiarity, high rating)",
                "Divisive albums (high rating variance)",
                "Gateway albums (led to exploring artist further)",
                "Perfect length analysis",
                "Energy progression throughout the year"
            ],
            
            "Group Dynamics": [
                "Consensus trends over time",
                "Discussion length vs album complexity",
                "Theme clustering (what sparks conversation)",
                "Selection influence patterns"
            ],
            
            "Predictive Features": [
                "Predict discussion length from album features",
                "Predict ratings based on selector and genre",
                "Optimal album characteristics for your group",
                "Next selection recommendations"
            ]
        }
        
        return analytics_ideas

# Create documentation for data collection
def create_data_dictionary():
    """Create a data dictionary for the enhanced dataset"""
    
    dictionary = {
        "Original Fields": {
            "Month": "Month of album club meeting",
            "Year": "Year of album club meeting",
            "album_name": "Name of the album",
            "album_artist": "Artist/band name",
            "album_release_date": "Year album was released",
            "select_member": "Member who selected this album",
            "Genre": "Musical genre(s), comma-separated",
            "score": "Album score/rating (if tracked)",
            "Blurb": "Brief notes or selection reason"
        },
        
        "Suggested Additions": {
            "album_length_minutes": "Total album runtime in minutes",
            "track_count": "Number of tracks on album",
            "avg_member_rating": "Average rating from all members (1-10)",
            "individual_ratings": "JSON object with {member: rating}",
            "discussion_attendance": "List of members who attended discussion",
            "favorite_tracks": "JSON object with {member: track_name}",
            "discussion_duration": "Approximate discussion time in minutes",
            "discussion_themes": "Key topics discussed (comma-separated tags)",
            "new_discovery_percentage": "% of members who hadn't heard album before",
            "selector_familiarity": "new/heard_once/familiar/favorite",
            "would_recommend": "Percentage who would recommend to others",
            "playlist_position": "Order in monthly Spotify playlist",
            "days_before_discussion": "Days between adding to playlist and discussion"
        },
        
        "Spotify API Fields": {
            "spotify_album_id": "Unique Spotify identifier",
            "spotify_popularity": "Spotify popularity score (0-100)",
            "spotify_duration_ms": "Exact duration in milliseconds",
            "danceability": "Spotify danceability score (0-1)",
            "energy": "Spotify energy score (0-1)",
            "valence": "Musical positivity score (0-1)",
            "acousticness": "Spotify acousticness score (0-1)",
            "instrumentalness": "Likelihood of no vocals (0-1)",
            "spotify_url": "Direct link to Spotify album"
        }
    }
    
    return dictionary

if __name__ == "__main__":
    enricher = AlbumDataEnrichment("ac.csv")
    
    # Generate suggestions
    suggestions = enricher.suggest_additional_data_points()
    print("=== EASY DATA POINTS TO COLLECT ===\n")
    for category, items in suggestions.items():
        print(f"\n{category.replace('_', ' ').title()}:")
        for field, details in items.items():
            print(f"\n  📊 {field}")
            print(f"     What: {details['description']}")
            print(f"     How: {details['value']}")
            print(f"     Why: {details['insight']}")
    
    # Create collection template
    template = enricher.generate_collection_template()
    template.to_csv("album_club_enhanced_template.csv", index=False)
    print("\n\n✅ Created 'album_club_enhanced_template.csv' for data collection")
    
    # Save Spotify integration template
    with open("spotify_integration.py", "w") as f:
        f.write(enricher.generate_spotify_api_template())
    print("✅ Created 'spotify_integration.py' template for Spotify API integration")
    
    # Generate analytics ideas
    analytics = enricher.create_enhanced_analytics()
    with open("analytics_ideas.json", "w") as f:
        json.dump(analytics, f, indent=2)
    print("✅ Created 'analytics_ideas.json' with enhanced analytics possibilities")
    
    # Create data dictionary
    dictionary = create_data_dictionary()
    with open("data_dictionary.json", "w") as f:
        json.dump(dictionary, f, indent=2)
    print("✅ Created 'data_dictionary.json' for documentation")