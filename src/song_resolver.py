"""
Song Resolver — finds and downloads music from various sources.
Supports: YouTube links, song title search, local file paths.
"""

import os
import re
import tempfile
from pathlib import Path
from typing import Optional, Tuple


class SongResolver:
    """
    Resolves a user's query into a local audio file.

    Input can be:
    - YouTube URL → download audio
    - Song title / artist name → search YouTube → download first result
    - Local file path → use directly
    """

    def __init__(self, download_dir: str = None):
        self.download_dir = download_dir or os.path.join(tempfile.gettempdir(), "resonate")
        os.makedirs(self.download_dir, exist_ok=True)
        self._temp_files = []

    def resolve(self, query: str) -> Tuple[Optional[str], str]:
        """
        Try to resolve a user query into a local audio file.

        Returns: (file_path, source_description) or (None, error_message)
        """
        query = query.strip().strip('"\'')

        if not query:
            return None, "Empty query"

        # Case 1: Local file path
        if os.path.exists(query):
            return query, f"local file: {os.path.basename(query)}"

        # Case 2: Looks like a file path but doesn't exist (probably a typo)
        if '/' in query or '\\' in query or query.endswith(('.mp3', '.wav', '.flac', '.ogg', '.m4a')):
            return None, f"File not found: {query}"

        # Case 3: YouTube URL
        if self._is_youtube_url(query):
            return self._download_from_youtube(query)

        # Case 4: Search query (song title / artist)
        print(f"  🔍 Searching YouTube for: {query}")
        return self._search_and_download(query)

    def _is_youtube_url(self, text: str) -> bool:
        patterns = [
            r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/',
            r'(https?://)?(www\.)?(m\.youtube\.com)/',
            r'(https?://)?(www\.)?(music\.youtube\.com)/',
        ]
        return any(re.match(p, text) for p in patterns)

    def _find_downloaded_file(self) -> Optional[str]:
        """Find the most recently added audio file in download_dir."""
        audio_exts = {'.mp3', '.m4a', '.webm', '.wav', '.ogg'}
        candidates = []
        for f in os.listdir(self.download_dir):
            ext = os.path.splitext(f)[1].lower()
            if ext in audio_exts:
                path = os.path.join(self.download_dir, f)
                candidates.append((os.path.getmtime(path), path))
        if candidates:
            candidates.sort(reverse=True)
            return candidates[0][1]
        return None

    def _download_from_youtube(self, url: str) -> Tuple[Optional[str], str]:
        """Download audio from a YouTube URL."""
        try:
            import yt_dlp

            output_template = os.path.join(self.download_dir, '%(title)s.%(ext)s')

            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': output_template,
                'quiet': True,
                'no_warnings': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Unknown')

                path = self._find_downloaded_file()
                if path:
                    self._temp_files.append(path)
                    return path, f"YouTube: {title}"

            return None, "Download failed: file not found after download"

        except ImportError:
            return None, "yt-dlp not installed. Run: pip install yt-dlp"
        except Exception as e:
            return None, f"YouTube download error: {e}"

    def _search_and_download(self, query: str) -> Tuple[Optional[str], str]:
        """Search YouTube for a song and download the first result."""
        try:
            import yt_dlp

            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'default_search': 'ytsearch1',
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch1:{query}", download=True)

                if not info or 'entries' not in info or not info['entries']:
                    return None, f"No results found for: {query}"

                entry = info['entries'][0]
                title = entry.get('title', 'Unknown')

                path = self._find_downloaded_file()
                if path:
                    self._temp_files.append(path)
                    return path, f"YouTube: {title}"

                return None, f"Downloaded but file not found for: {title}"

        except ImportError:
            return None, "yt-dlp not installed. Run: pip install yt-dlp"
        except Exception as e:
            return None, f"Search error: {e}"

    def cleanup(self):
        """Remove temporary downloaded files."""
        for f in self._temp_files:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except Exception:
                pass
        self._temp_files = []

    def __del__(self):
        self.cleanup()
