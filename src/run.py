"""
Resonate — Main runner.
Modes: analyze, resolve, route, build-index, curate
"""

import os
import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.feature_extractor import AudioFeatureExtractor
from src.emotion_analyzer import EmotionAnalyzer
from src.similarity import SimilarityEngine
from src.curator import PsychoAcousticCurator, CuratorConfig
from src.dataset_manager import DatasetManager
from src.song_resolver import SongResolver
from src.mood_router import run_interactive


def demo_analyze_song(audio_path: str):
    print(f"\n{'='*60}")
    print(f"  R E S O N A T E — Analyze")
    print(f"{'='*60}")
    print(f"  File: {audio_path}\n")

    extractor = AudioFeatureExtractor(n_mfcc=13)
    features = extractor.extract(audio_path)
    vector = extractor.to_vector(features)
    t = float(features['tempo'].item()) if hasattr(features['tempo'], 'item') else float(features['tempo'])

    print(f"📊 Acoustic Fingerprint")
    print(f"   Tempo:              {t:.0f} BPM")
    print(f"   Spectral Centroid:  {features['spectral_centroid'][0]:.0f} Hz (brightness)")
    print(f"   Zero Crossing Rate: {features['zero_crossing_rate'][0]:.4f} (noisiness)")
    print(f"   Harmonic Ratio:     {features['harmonic_ratio'][0]:.3f}")
    print(f"   Feature vector:     {len(vector)} dimensions")

    analyzer = EmotionAnalyzer()
    emotion = analyzer.predict(audio_path)
    print(f"\n❤️  Emotion Profile")
    print(f"   Valence: {emotion['valence']:.3f}  {'─'*int(emotion['valence']*20)}●{'─'*int((1-emotion['valence'])*20)}")
    print(f"   Arousal: {emotion['arousal']:.3f}  {'─'*int(emotion['arousal']*10)}●{'─'*int((1-emotion['arousal'])*10)}")
    print(f"   Moods:   {', '.join(emotion['moods'])}")

    return vector, emotion, features


def cmd_resolve(query: str):
    resolver = SongResolver()
    print(f"\n🔍 Resolving: {query}")
    path, source = resolver.resolve(query)
    if path:
        print(f"   ✅ {source}")
        demo_analyze_song(path)
        resolver.cleanup()
    else:
        print(f"   ⚠ {source}")


def cmd_build_index(dataset_path: str, n_mfcc: int = 13):
    print(f"\n📚 Building similarity index from: {dataset_path}")

    extractor = AudioFeatureExtractor(n_mfcc=n_mfcc)
    similarity = SimilarityEngine(dim=93, index_type='flat')
    dataset = DatasetManager()

    song_data = list(dataset.iter_audio_files(dataset_path))
    print(f"   Found {len(song_data)} audio files")

    if not song_data:
        print("   No audio files found.")
        return similarity

    vectors, song_ids, metadata = [], [], []
    total = min(len(song_data), 500)

    for i, song in enumerate(song_data[:total]):
        try:
            features = extractor.extract(song['path'])
            vector = extractor.to_vector(features)
            vectors.append(vector)
            song_ids.append(song['path'])
            emotion = EmotionAnalyzer().predict(song['path'])
            metadata.append({'title': song['title'], 'path': song['path'], 'emotion': emotion})
            if (i+1) % 10 == 0 or i == total-1:
                print(f"   [{i+1}/{total}]", end='\r')
        except Exception as e:
            pass

    print(f"\n   Indexing {len(vectors)} songs...")
    if vectors:
        similarity.add_songs(np.array(vectors), song_ids, metadata)
        print(f"   ✅ Index built: {similarity.size} songs")

    return similarity


def cmd_curate(query: str, dataset_path: str):
    resolver = SongResolver()
    path, source = resolver.resolve(query)

    if not path:
        print(f"   ⚠ {source}")
        return

    print(f"   ✅ {source}")
    sim = cmd_build_index(dataset_path)

    if sim.size == 0:
        print("   ⚠ No songs in index to search against")
        return

    extractor = AudioFeatureExtractor(n_mfcc=13)
    analyzer = EmotionAnalyzer()
    curator = PsychoAcousticCurator()
    curator.initialize(extractor, analyzer, sim)

    result = curator.curate(path, top_k=20)
    print(f"\n🔍 Query: V={result.query_emotion['valence']:.2f}, A={result.query_emotion['arousal']:.2f}")
    print(f"\n🎧 Recommendations:")
    for i, rec in enumerate(result.recommendations[:10]):
        t = rec['metadata'].get('title', rec['song_id'])[:35]
        print(f"   {i+1}. {t}  (sim: {rec['similarity']:.2f})")

    resolver.cleanup()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Resonate — emotional music curation")
    parser.add_argument("mode", choices=["analyze", "resolve", "route", "build-index", "curate"],
                       help="Operation mode")
    parser.add_argument("query", nargs="?", default="",
                       help="Song title, YouTube link, or file path")
    parser.add_argument("--dataset", default="./data/music",
                       help="Path to music dataset (for curate mode)")

    args = parser.parse_args()

    if args.mode == "route":
        run_interactive()

    elif args.mode == "resolve":
        if not args.query:
            print("Usage: python -m src.run resolve \"song title\"")
            sys.exit(1)
        cmd_resolve(args.query)

    elif args.mode == "analyze":
        if not args.query:
            print("Usage: python -m src.run analyze \"song or file\"")
            sys.exit(1)
        resolver = SongResolver()
        path, source = resolver.resolve(args.query)
        if path:
            print(f"   ✅ {source}")
            demo_analyze_song(path)
            resolver.cleanup()
        else:
            print(f"   ⚠ {source}")

    elif args.mode == "build-index":
        cmd_build_index(args.dataset)

    elif args.mode == "curate":
        if not args.query:
            print("Usage: python -m src.run curate \"song\" --dataset ./data/music")
            sys.exit(1)
        cmd_curate(args.query, args.dataset)
