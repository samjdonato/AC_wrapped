import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from datetime import datetime
import json

class AlbumClubWrapped:
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)
        # Clean column names
        self.df.columns = self.df.columns.str.strip()
        # Clean the 'March ' entries with trailing space
        self.df['Month'] = self.df['Month'].str.strip()
        # Convert Year to int
        self.df['Year'] = pd.to_numeric(self.df['Year'], errors='coerce')
        # Parse release dates
        self.df['album_release_date'] = pd.to_numeric(self.df['album_release_date'], errors='coerce')
        # Clean genre column name
        if 'Genera' in self.df.columns:
            self.df.rename(columns={'Genera': 'Genre'}, inplace=True)
        
    def generate_wrapped_stats(self):
        stats = {}
        
        # Member statistics
        stats['member_stats'] = self._get_member_stats()
        
        # Genre analysis
        stats['genre_stats'] = self._get_genre_stats()
        
        # Decade analysis
        stats['decade_stats'] = self._get_decade_stats()
        
        # Album age analysis
        stats['album_age_stats'] = self._get_album_age_stats()
        
        # Monthly patterns
        stats['monthly_patterns'] = self._get_monthly_patterns()
        
        # Artist repeat analysis
        stats['artist_stats'] = self._get_artist_stats()
        
        # Superlatives
        stats['superlatives'] = self._get_superlatives()
        
        # Club evolution
        stats['club_evolution'] = self._get_club_evolution()
        
        return stats
    
    def _get_member_stats(self):
        member_counts = self.df['select_member'].value_counts().to_dict()
        
        # Genre preferences by member
        genre_by_member = defaultdict(list)
        for _, row in self.df.iterrows():
            if pd.notna(row['Genre']):
                genres = [g.strip() for g in str(row['Genre']).split(',')]
                genre_by_member[row['select_member']].extend(genres)
        
        member_genre_prefs = {}
        for member, genres in genre_by_member.items():
            if genres:
                genre_counter = Counter(genres)
                member_genre_prefs[member] = {
                    'top_genre': genre_counter.most_common(1)[0],
                    'genre_diversity': len(set(genres))
                }
        
        # Era preferences (based on release dates)
        era_by_member = defaultdict(list)
        for _, row in self.df.iterrows():
            if pd.notna(row['album_release_date']):
                era_by_member[row['select_member']].append(row['album_release_date'])
        
        member_era_stats = {}
        for member, years in era_by_member.items():
            if years:
                member_era_stats[member] = {
                    'avg_release_year': np.mean(years),
                    'oldest_pick': min(years),
                    'newest_pick': max(years),
                    'year_span': max(years) - min(years)
                }
        
        return {
            'selection_counts': member_counts,
            'genre_preferences': member_genre_prefs,
            'era_preferences': member_era_stats
        }
    
    def _get_genre_stats(self):
        # Flatten all genres
        all_genres = []
        for genres in self.df['Genre'].dropna():
            all_genres.extend([g.strip() for g in str(genres).split(',')])
        
        genre_counts = Counter(all_genres)
        
        # Genre diversity by month
        monthly_genre_diversity = {}
        for month in self.df['Month'].unique():
            month_df = self.df[self.df['Month'] == month]
            month_genres = []
            for genres in month_df['Genre'].dropna():
                month_genres.extend([g.strip() for g in str(genres).split(',')])
            monthly_genre_diversity[month] = len(set(month_genres))
        
        return {
            'top_genres': genre_counts.most_common(10),
            'total_unique_genres': len(set(all_genres)),
            'monthly_diversity': monthly_genre_diversity
        }
    
    def _get_decade_stats(self):
        decades = defaultdict(int)
        for year in self.df['album_release_date'].dropna():
            decade = int(year // 10) * 10
            decades[f"{decade}s"] += 1
        
        return dict(sorted(decades.items()))
    
    def _get_album_age_stats(self):
        current_year = 2025
        ages = []
        for _, row in self.df.iterrows():
            if pd.notna(row['album_release_date']):
                age = current_year - row['album_release_date']
                ages.append(age)
        
        if ages:
            return {
                'avg_album_age': np.mean(ages),
                'median_album_age': np.median(ages),
                'oldest_album': self.df.loc[self.df['album_release_date'].idxmin()],
                'newest_album': self.df.loc[self.df['album_release_date'].idxmax()]
            }
        return {}
    
    def _get_monthly_patterns(self):
        # Albums per month
        albums_per_month = self.df.groupby('Month').size().to_dict()
        
        # Average selections per person per month
        avg_per_person = {}
        for month in self.df['Month'].unique():
            month_df = self.df[self.df['Month'] == month]
            unique_selectors = month_df['select_member'].nunique()
            avg_per_person[month] = len(month_df) / unique_selectors if unique_selectors > 0 else 0
        
        return {
            'albums_per_month': albums_per_month,
            'avg_selections_per_person': avg_per_person
        }
    
    def _get_artist_stats(self):
        artist_counts = self.df['album_artist'].value_counts()
        repeat_artists = artist_counts[artist_counts > 1].to_dict()
        
        return {
            'total_unique_artists': len(artist_counts),
            'repeat_artists': repeat_artists
        }
    
    def _get_superlatives(self):
        superlatives = {}
        
        # Member with most eclectic taste (genre diversity)
        genre_diversity = {}
        for member in self.df['select_member'].unique():
            member_df = self.df[self.df['select_member'] == member]
            member_genres = []
            for genres in member_df['Genre'].dropna():
                member_genres.extend([g.strip() for g in str(genres).split(',')])
            genre_diversity[member] = len(set(member_genres))
        
        if genre_diversity:
            superlatives['most_eclectic'] = max(genre_diversity.items(), key=lambda x: x[1])
        
        # Time traveler (biggest year span in selections)
        year_spans = {}
        for member in self.df['select_member'].unique():
            member_df = self.df[self.df['select_member'] == member]
            years = member_df['album_release_date'].dropna()
            if len(years) > 0:
                year_spans[member] = years.max() - years.min()
        
        if year_spans:
            superlatives['time_traveler'] = max(year_spans.items(), key=lambda x: x[1])
        
        # Vintage collector (oldest average release year)
        avg_years = {}
        for member in self.df['select_member'].unique():
            member_df = self.df[self.df['select_member'] == member]
            years = member_df['album_release_date'].dropna()
            if len(years) > 0:
                avg_years[member] = years.mean()
        
        if avg_years:
            superlatives['vintage_collector'] = min(avg_years.items(), key=lambda x: x[1])
        
        # Trendsetter (newest average release year)
        if avg_years:
            superlatives['trendsetter'] = max(avg_years.items(), key=lambda x: x[1])
        
        return superlatives
    
    def _get_club_evolution(self):
        # Track participation over time
        monthly_participation = []
        
        # Create proper date column
        self.df['date'] = pd.to_datetime(self.df['Year'].astype(str) + '-' + self.df['Month'], 
                                         format='%Y-%B', errors='coerce')
        
        sorted_df = self.df.sort_values('date')
        
        for date in sorted_df['date'].dropna().unique():
            month_df = sorted_df[sorted_df['date'] == date]
            monthly_participation.append({
                'date': date.strftime('%B %Y'),
                'participants': list(month_df['select_member'].unique()),
                'num_albums': len(month_df)
            })
        
        return monthly_participation

def format_stats_for_display(stats):
    """Format statistics for readable output"""
    output = []
    
    output.append("=== ALBUM CLUB WRAPPED 2024-2025 ===\n")
    
    # Member highlights
    output.append("🎵 MEMBER HIGHLIGHTS")
    member_stats = stats['member_stats']
    for member, count in member_stats['selection_counts'].items():
        output.append(f"  {member}: {count} albums selected")
        if member in member_stats['genre_preferences']:
            top_genre = member_stats['genre_preferences'][member]['top_genre']
            output.append(f"    Favorite genre: {top_genre[0]} ({top_genre[1]} picks)")
        if member in member_stats['era_preferences']:
            avg_year = member_stats['era_preferences'][member]['avg_release_year']
            output.append(f"    Average release year: {avg_year:.0f}")
    
    output.append("\n🎸 GENRE INSIGHTS")
    output.append(f"  Total unique genres explored: {stats['genre_stats']['total_unique_genres']}")
    output.append("  Top 5 genres:")
    for genre, count in stats['genre_stats']['top_genres'][:5]:
        output.append(f"    - {genre}: {count}")
    
    output.append("\n📅 DECADE BREAKDOWN")
    for decade, count in stats['decade_stats'].items():
        output.append(f"  {decade}: {count} albums")
    
    output.append("\n🏆 SUPERLATIVES")
    sup = stats['superlatives']
    if 'most_eclectic' in sup:
        output.append(f"  Most Eclectic Taste: {sup['most_eclectic'][0]} ({sup['most_eclectic'][1]} different genres)")
    if 'time_traveler' in sup:
        output.append(f"  Time Traveler: {sup['time_traveler'][0]} ({sup['time_traveler'][1]:.0f} year span)")
    if 'vintage_collector' in sup:
        output.append(f"  Vintage Collector: {sup['vintage_collector'][0]} (avg year: {sup['vintage_collector'][1]:.0f})")
    if 'trendsetter' in sup:
        output.append(f"  Trendsetter: {sup['trendsetter'][0]} (avg year: {sup['trendsetter'][1]:.0f})")
    
    output.append("\n🎤 ARTIST LOVE")
    output.append(f"  Total unique artists: {stats['artist_stats']['total_unique_artists']}")
    if stats['artist_stats']['repeat_artists']:
        output.append("  Artists we couldn't get enough of:")
        for artist, count in stats['artist_stats']['repeat_artists'].items():
            output.append(f"    - {artist}: {count} albums")
    
    return "\n".join(output)

# Run analysis
if __name__ == "__main__":
    wrapped = AlbumClubWrapped("album_club_enhanced_template.csv")
    stats = wrapped.generate_wrapped_stats()
    
    # Save raw stats as JSON
    with open('wrapped_stats.json', 'w') as f:
        # Convert non-serializable objects
        json_safe_stats = {}
        for key, value in stats.items():
            if key == 'member_stats':
                json_safe_stats[key] = {
                    'selection_counts': value['selection_counts'],
                    'genre_preferences': value['genre_preferences'],
                    'era_preferences': {k: {sk: float(sv) if isinstance(sv, np.number) else sv 
                                           for sk, sv in v.items()} 
                                       for k, v in value['era_preferences'].items()}
                }
            elif key == 'album_age_stats':
                if value:
                    json_safe_stats[key] = {
                        'avg_album_age': float(value['avg_album_age']),
                        'median_album_age': float(value['median_album_age']),
                        'oldest_album': {
                            'name': value['oldest_album']['album_name'],
                            'artist': value['oldest_album']['album_artist'],
                            'year': int(value['oldest_album']['album_release_date'])
                        },
                        'newest_album': {
                            'name': value['newest_album']['album_name'],
                            'artist': value['newest_album']['album_artist'],
                            'year': int(value['newest_album']['album_release_date'])
                        }
                    }
            elif key == 'superlatives':
                json_safe_stats[key] = {k: (v[0], float(v[1]) if isinstance(v[1], np.number) else v[1]) 
                                      for k, v in value.items()}
            else:
                json_safe_stats[key] = value
        
        json.dump(json_safe_stats, f, indent=2)
    
    # Save formatted output
    formatted = format_stats_for_display(stats)
    with open('wrapped_summary.txt', 'w') as f:
        f.write(formatted)
    
    print("Analysis complete! Check wrapped_summary.txt and wrapped_stats.json")