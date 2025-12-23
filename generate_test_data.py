import pandas as pd
import numpy as np
import random

def enhance_album_data(input_csv='ac.csv', output_csv='ac_enhanced.csv'):
    """
    Add semi-realistic enhanced data columns to test visualizations
    """
    # Read existing data
    df = pd.read_csv(input_csv)
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Add album_length_minutes (realistic range: 25-75 minutes)
    # Jazz and classical tend to be longer
    df['album_length_minutes'] = df.apply(lambda row: 
        np.random.randint(40, 75) if 'Jazz' in str(row.get('Genre', '')) or 'Classical' in str(row.get('Genre', ''))
        else np.random.randint(25, 55), axis=1)
    
    # Add track_count (realistic range: 8-20)
    df['track_count'] = np.random.randint(8, 20, size=len(df))
    
    # Add avg_member_rating (6.0-9.5, normally distributed around 7.5)
    base_ratings = np.random.normal(7.5, 1.0, size=len(df))
    # Clip to realistic range and round to 1 decimal
    df['avg_member_rating'] = np.clip(base_ratings, 6.0, 9.5).round(1)
    
    # Add discussion_attendance_count (3-5 people)
    df['discussion_attendance_count'] = np.random.randint(3, 6, size=len(df))
    
    # Add standout_tracks (random track numbers)
    df['standout_tracks'] = df.apply(lambda row: 
        f"Track {random.randint(1, row['track_count'])}, Track {random.randint(1, row['track_count'])}", 
        axis=1)
    
    # Add discussion_themes
    themes_options = [
        'production, nostalgia',
        'lyrics, melody',
        'innovation, energy',
        'emotion, storytelling',
        'rhythm, atmosphere',
        'cultural impact, history',
        'instrumentation, vocals'
    ]
    df['discussion_themes'] = np.random.choice(themes_options, size=len(df))
    
    # Add new_discovery_for_most (60% Yes)
    df['new_discovery_for_most'] = np.random.choice(['Yes', 'No'], size=len(df), p=[0.6, 0.4])
    
    # Add selector_familiarity
    familiarity_options = ['New to me', 'Heard before', 'Familiar', 'Old favorite']
    df['selector_familiarity'] = np.random.choice(familiarity_options, size=len(df), 
                                                 p=[0.3, 0.3, 0.25, 0.15])
    
    # Add would_recommend (correlated with rating)
    df['would_recommend'] = df['avg_member_rating'].apply(
        lambda rating: 'Yes' if rating >= 7.5 else ('Maybe' if rating >= 6.5 else 'No')
    )
    
    # Add discussion_duration (20-90 minutes, longer for higher rated albums)
    df['discussion_duration'] = df['avg_member_rating'].apply(
        lambda rating: int(20 + (rating - 6) * 15 + np.random.randint(-10, 10))
    )
    
    # Add some individual ratings as JSON (for future use)
    members = ['Sam', 'Steph', 'Glenn', 'Claire', 'Jamie']
    df['individual_ratings'] = df.apply(lambda row: 
        str({member: round(row['avg_member_rating'] + np.random.uniform(-1.5, 1.5), 1) 
             for member in random.sample(members, k=random.randint(3, 5))}),
        axis=1)
    
    # Save enhanced data
    df.to_csv(output_csv, index=False)
    print(f"Enhanced data saved to {output_csv}")
    
    # Print summary
    print("\nData Enhancement Summary:")
    print(f"Total albums: {len(df)}")
    print(f"Average rating: {df['avg_member_rating'].mean():.1f}")
    print(f"Discovery rate: {(df['new_discovery_for_most'] == 'Yes').sum() / len(df) * 100:.0f}%")
    print(f"Recommend rate: {(df['would_recommend'] == 'Yes').sum() / len(df) * 100:.0f}%")
    print(f"Average album length: {df['album_length_minutes'].mean():.0f} minutes")

if __name__ == "__main__":
    enhance_album_data()