"""
Dataset Manager — handles scraping, indexing, and managing music datasets.
Supports MTG-Jamendo, FMA, and Spotify API integration.
"""

import json
import os
import numpy as np
from typing import Dict, List, Optional, Generator
from pathlib import Path


class DatasetManager:
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.songs: List[Dict] = []

    def load_mtg_jamendo(self, path: str) -> List[Dict]:
        """Load MTG-Jamendo dataset metadata."""
        import pandas as pd
        df = pd.read_csv(path, sep='\t')
        songs = []
        for _, row in df.iterrows():
            songs.append({
                'id': row.get('track_id', ''),
                'title': row.get('title', ''),
                'artist': row.get('artist_name', ''),
                'tags': row.get('tags', '').split(','),
                'genre': row.get('genre', ''),
                'mood': row.get('mood', ''),
                'instrument': row.get('instrument', ''),
                'source': 'mtg_jamendo',
            })
        self.songs.extend(songs)
        return songs

    def load_fma(self, path: str, sample_rate: int = 5) -> List[Dict]:
        """Load Free Music Archive dataset (small subset)."""
        import pandas as pd
        tracks_path = os.path.join(path, 'fma_metadata', 'tracks.csv')
        if not os.path.exists(tracks_path):
            print(f"FMA metadata not found at {tracks_path}")
            return []

        tracks = pd.read_csv(tracks_path, index_col=0, header=[0, 1])
        songs = []
        for track_id, row in tracks.iterrows():
            if sample_rate and np.random.random() > 1.0 / sample_rate:
                continue
            songs.append({
                'id': str(track_id),
                'title': row.get(('track', 'title'), ''),
                'artist': row.get(('artist', 'name'), ''),
                'genre': row.get(('track', 'genre_top'), ''),
                'tags': [],
                'source': 'fma',
            })
        self.songs.extend(songs)
        return songs

    def load_from_spotify(self, playlist_ids: List[str]) -> List[Dict]:
        """Load songs from Spotify playlists via API."""
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials

        client_id = os.environ.get('SPOTIFY_CLIENT_ID', '')
        client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET', '')

        if not client_id or not client_secret:
            print("Spotify credentials not found in environment")
            return []

        sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=client_id, client_secret=client_secret
            )
        )
        songs = []
        for playlist_id in playlist_ids:
            results = sp.playlist_tracks(playlist_id)
            for item in results['items']:
                track = item['track']
                if not track:
                    continue
                features = sp.audio_features(track['id'])
                songs.append({
                    'id': track['id'],
                    'title': track['name'],
                    'artist': track['artists'][0]['name'] if track['artists'] else '',
                    'album': track['album']['name'] if track['album'] else '',
                    'preview_url': track.get('preview_url', ''),
                    'features': features[0] if features else {},
                    'popularity': track.get('popularity', 0),
                    'source': 'spotify',
                })
        self.songs.extend(songs)
        return songs

    def save_index(self, vectors: np.ndarray, path: str):
        np.save(os.path.join(self.data_dir, f"{path}_vectors.npy"), vectors)
        with open(os.path.join(self.data_dir, f"{path}_songs.json"), 'w') as f:
            json.dump(self.songs, f)

    def load_index(self, path: str) -> Optional[np.ndarray]:
        vec_path = os.path.join(self.data_dir, f"{path}_vectors.npy")
        meta_path = os.path.join(self.data_dir, f"{path}_songs.json")
        if os.path.exists(vec_path) and os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                self.songs = json.load(f)
            return np.load(vec_path)
        return None

    def iter_audio_files(self, directory: str) -> Generator[Dict, None, None]:
        """Iterate over audio files in a directory tree."""
        audio_exts = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac'}
        for root, _, files in os.walk(directory):
            for fname in files:
                ext = os.path.splitext(fname)[1].lower()
                if ext in audio_exts:
                    path = os.path.join(root, fname)
                    yield {
                        'path': path,
                        'filename': fname,
                        'title': os.path.splitext(fname)[0],
                    }
