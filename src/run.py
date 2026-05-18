"""
PsychoAcoustic Engine — Main runner.
Demo mode: analyze a song, find similar songs, predict emotion.
"""

import os
import sys
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.feature_extractor import AudioFeatureExtractor
from src.emotion_analyzer import EmotionAnalyzer
from src.similarity import SimilarityEngine
from src.curator import PsychoAcousticCurator, CuratorConfig
from src.dataset_manager import DatasetManager


def demo_analyze_song(audio_path: str):
    print(f"\n{'='*60}")
    print(f"🎵 PSYCHOACOUSTIC ENGINE — DEMO")
    print(f"{'='*60}")
    print(f"Analyzing: {audio_path}\n")

    # 1. Extract features
    extractor = AudioFeatureExtractor()
    features = extractor.extract(audio_path)
    vector = extractor.to_vector(features)
    print(f"📊 Feature vector dim: {len(vector)}")
    print(f"   Tempo: {features['tempo'][0]:.1f} BPM")

    # 2. Analyze emotion
    analyzer = EmotionAnalyzer()
    emotion = analyzer.predict(audio_path)
    print(f"\n❤️  Emotion Profile:")
    print(f"   Valence: {emotion['valence']:.3f} (0=sad, 1=happy)")
    print(f"   Arousal: {emotion['arousal']:.3f} (0=calm, 1=excited)")
    print(f"   Moods:   {', '.join(emotion['moods'])}")

    # 3. Russell's circumplex visualization
    print(f"\n📈 Russell's Circumplex:")
    print(f"                    Aroused")
    print(f"                      ↑")
    if emotion['arousal'] > 0.6:
        if emotion['valence'] > 0.6:
            print(f"      Unpleasant ← ● → Happy   ← YOU ARE HERE (excited-happy)")
        else:
            print(f"      ● ← Angry/Tense           ← YOU ARE HERE (tense-angry)")
    else:
        if emotion['valence'] > 0.6:
            print(f"      Relaxed/Calm ● → Happy   ← YOU ARE HERE (relaxed)")
        else:
            print(f"      Sad/Depressed ●           ← YOU ARE HERE (sad)")
    print(f"                      ↓")
    print(f"                    Calm")

    # 4. Feature breakdown
    print(f"\n🔬 Acoustic Fingerprint:")
    print(f"   Spectral Centroid: {features['spectral_centroid'][0]:.0f} Hz (brightness)")
    print(f"   Zero Crossing Rate: {features['zero_crossing_rate'][0]:.4f} (noisiness)")
    print(f"   Harmonic Ratio: {features['harmonic_ratio'][0]:.3f}")
    print(f"   MFCC (first 5): {features['mfcc_mean'][:5]}")
    print(f"   Chroma (pitch class): {features['chroma_mean']}")

    return vector, emotion, features


def demo_build_index(dataset_path: str):
    print(f"\n{'='*60}")
    print(f"📚 BUILDING SIMILARITY INDEX")
    print(f"{'='*60}")

    extractor = AudioFeatureExtractor()
    similarity = SimilarityEngine(dim=79)  # match feature vector size
    dataset = DatasetManager()

    # Find all audio files
    song_data = list(dataset.iter_audio_files(dataset_path))
    print(f"Found {len(song_data)} audio files")

    if not song_data:
        print("No audio files found. Create a data/music/ directory with .mp3 files.")
        return similarity

    # Extract features for all songs
    vectors = []
    song_ids = []
    metadata = []

    for i, song in enumerate(song_data[:100]):  # limit for demo
        try:
            features = extractor.extract(song['path'])
            vector = extractor.to_vector(features)
            vectors.append(vector)

            song_id = song['path']
            song_ids.append(song_id)

            emotion = EmotionAnalyzer().predict(song['path'])
            metadata.append({
                'title': song['title'],
                'path': song['path'],
                'emotion': emotion,
            })
            print(f"  [{i+1}/{min(len(song_data), 100)}] {song['title']}")
        except Exception as e:
            print(f"  ✗ Skipped {song['filename']}: {e}")

    if vectors:
        similarity.add_songs(np.array(vectors), song_ids, metadata)
        print(f"\n✅ Index built with {similarity.size} songs")

    return similarity


def demo_curate(audio_path: str, similarity_engine):
    print(f"\n{'='*60}")
    print(f"🎧 CURATION RESULTS")
    print(f"{'='*60}")

    extractor = AudioFeatureExtractor()
    analyzer = EmotionAnalyzer(use_music2emo=False)

    curator = PsychoAcousticCurator()
    curator.initialize(extractor, analyzer, similarity_engine)

    result = curator.curate(audio_path, top_k=20)

    print(f"\n🔍 Query emotion: V={result.query_emotion['valence']:.3f}, "
          f"A={result.query_emotion['arousal']:.3f}")
    print(f"   Moods: {', '.join(result.query_emotion['moods'])}")
    print(f"\n📋 Top 10 Recommendations:")
    print(f"{'#':<3} {'Title':<30} {'Similarity':<12} {'V':<6} {'A':<6}")
    print(f"{'-'*60}")

    for i, rec in enumerate(result.recommendations[:10]):
        emo = rec.get('emotion', {})
        v = emo.get('valence', 0.5) if emo else 0.5
        a = emo.get('arousal', 0.5) if emo else 0.5
        title = rec['metadata'].get('title', rec['song_id'])[:28]
        print(f"{i+1:<3} {title:<30} {rec['similarity']:<12.4f} {v:<6.3f} {a:<6.3f}")

    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="PsychoAcoustic Engine")
    parser.add_argument("mode", choices=["analyze", "build-index", "curate", "full-demo"],
                       help="Operation mode")
    parser.add_argument("--audio", type=str, help="Path to audio file")
    parser.add_argument("--dataset", type=str, default="./data/music",
                       help="Path to music dataset directory")

    args = parser.parse_args()
    args.audio = args.audio or ""

    if args.mode == "analyze":
        if not args.audio or not os.path.exists(args.audio):
            print("Please provide a valid --audio path")
            sys.exit(1)
        demo_analyze_song(args.audio)

    elif args.mode == "build-index":
        demo_build_index(args.dataset)

    elif args.mode == "curate":
        if not os.path.exists(args.audio):
            print("Please provide a valid --audio path")
            sys.exit(1)
        sim = demo_build_index(args.dataset)
        if sim and sim.size > 0:
            demo_curate(args.audio, sim)

    elif args.mode == "full-demo":
        print("\n🚀 PSYCHOACOUSTIC ENGINE — FULL DEMO")
        print("=" * 60)

        # Step 1: Build index from dataset
        sim = demo_build_index(args.dataset)

        if sim and sim.size > 0 and args.audio and os.path.exists(args.audio):
            # Step 2: Analyze query song
            demo_analyze_song(args.audio)
            # Step 3: Curate recommendations
            demo_curate(args.audio, sim)
        else:
            print("\n💡 Tip: Place some .mp3 files in data/music/ and run with --audio to curate")
