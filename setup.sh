#!/bin/bash
# PsychoAcoustic Engine — Setup

echo "🔧 Installing PsychoAcoustic Engine..."

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install core dependencies
pip install --upgrade pip
pip install librosa soundfile numpy scipy faiss-cpu \
            torch transformers pandas tqdm joblib \
            matplotlib seaborn

# Optional: Spotify API
pip install spotipy

# Optional: audio I/O
pip install pyaudio sounddevice

# Create data directories
mkdir -p data/music
mkdir -p data/indices
mkdir -p data/datasets

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Place some .mp3 files in data/music/"
echo "  2. Activate: source .venv/bin/activate"
echo "  3. Run:     python -m src.run full-demo --audio data/music/your_song.mp3"
echo ""
echo "Quick test - analyze a song:"
echo "  python -m src.run analyze --audio data/music/your_song.mp3"
