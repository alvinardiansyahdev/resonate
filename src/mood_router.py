"""
Interactive Mood Router — user-friendly interface for mood trajectory selection.
Console-based UI that guides users through mood selection → trajectory generation.
"""

import os
import sys
from typing import Optional
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mood_trajectory import Mood, MoodTrajectoryEngine, DEFAULT_TRAJECTORIES
from src.feature_extractor import AudioFeatureExtractor
from src.emotion_analyzer import EmotionAnalyzer
from src.similarity import SimilarityEngine
from src.song_resolver import SongResolver


class MoodRouter:
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        self.trajectory_engine = MoodTrajectoryEngine()
        self.current_mood = None
        self.trajectory_name = None

    def show_welcome(self):
        print("\n" + "="*60)
        print("  🧠  R E S O N A T E")
        print("  Music that meets you where you are.")
        print("="*60)
        print("\nHow are you feeling right now?")
        print("This helps me plan the right musical journey for you.")

    def select_mood(self) -> str:
        moods = [
            ("sad", "😢 Sad — heavy, melancholic, low energy"),
            ("depressed", "😔 Depressed — hopeless, drained, empty"),
            ("angry", "😠 Angry — frustrated, irritated, tense"),
            ("anxious", "😰 Anxious — worried, restless, stressed"),
            ("tired", "😴 Tired — exhausted, low energy, sluggish"),
            ("tense", "😬 Tense — on edge, alert but uncomfortable"),
            ("neutral", "😐 Neutral — not great, not terrible"),
            ("calm", "😌 Calm — peaceful, centered, relaxed"),
            ("happy", "😊 Happy — good, light, positive"),
            ("excited", "🤩 Excited — energetic, pumped, enthusiastic"),
        ]

        for i, (name, desc) in enumerate(moods, 1):
            print(f"  {i}. {desc}")

        while True:
            try:
                choice = input(f"\nYour choice (1-{len(moods)}): ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(moods):
                    self.current_mood = moods[idx][0]
                    return self.current_mood
            except ValueError:
                pass
            print(f"Please enter a number between 1 and {len(moods)}.")

    def suggest_trajectories(self) -> str:
        mood = self.current_mood

        suggestions = {
            'sad':          [('sad_to_happy', "Guide you gently toward happiness"),
                             ('neutral_to_happy', "Lift you up slowly")],
            'depressed':    [('sad_to_happy', "Gentle rise toward lightness"),
                             ('anxious_to_calm', "Find peace first")],
            'angry':        [('angry_to_happy', "Release anger, find calm, then happy"),
                             ('anxious_to_calm', "Calm down first")],
            'anxious':      [('anxious_to_calm', "Slow down and find peace"),
                             ('tired_to_focused', "Channel energy into focus")],
            'tired':        [('tired_to_focused', "Wake up gently and find focus"),
                             ('sad_to_happy', "Gentle energy lift")],
            'tense':        [('anxious_to_calm', "Release tension, find calm"),
                             ('angry_to_happy', "Process and release")],
            'neutral':      [('neutral_to_happy', "Simple lift toward happiness"),
                             ('sad_to_happy', "Gentle upward journey")],
            'calm':         [('neutral_to_happy', "Maintain peace, add brightness")],
            'happy':        [('neutral_to_happy', "Stay in a good place")],
            'excited':      [('neutral_to_happy', "Channel that energy")],
        }

        available = suggestions.get(mood, [('neutral_to_happy', "Simple lift")])

        print(f"\n🎯 I see you're feeling **{mood.upper()}**.")
        print("Here's what I can do for you:\n")

        valid = []
        for key, desc in available:
            if key in DEFAULT_TRAJECTORIES:
                valid.append((key, desc))

        if len(valid) == 1:
            print(f"Recommended: {valid[0][1]}")
            self.trajectory_name = valid[0][0]
            return self.trajectory_name

        for i, (key, desc) in enumerate(valid, 1):
            traj_name = DEFAULT_TRAJECTORIES[key]['start'].label
            traj_end = DEFAULT_TRAJECTORIES[key]['end'].label
            print(f"  {i}. {traj_name} → {traj_end}")
            print(f"     {desc}")

        while True:
            try:
                choice = input(f"\nWhich journey sounds right? (1-{len(valid)}): ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(valid):
                    self.trajectory_name = valid[idx][0]
                    return self.trajectory_name
            except ValueError:
                pass
            print(f"Please enter a number between 1 and {len(valid)}.")

    def ask_favorite_song(self) -> Optional[str]:
        print(f"\n🎵 To make this personal:")
        print("  Type a song title, artist name, YouTube link, or file path.")
        print("  I'll find it and analyze what makes it special to you.")
        print("  (Press Enter to skip)")

        query = input("  Song / link > ").strip().strip('"\'')

        if not query:
            return None

        resolver = SongResolver()
        file_path, source = resolver.resolve(query)

        if file_path and os.path.exists(file_path):
            print(f"  ✅ Found: {source}")
            return file_path

        print(f"  ⚠ Could not find: {query}")
        print(f"  ({source})")
        print("  You can still continue without personalization.")
        return None

    def run(self):
        self.show_welcome()
        mood = self.select_mood()
        traj = self.suggest_trajectories()
        fav_song = self.ask_favorite_song()

        print(f"\n✅ Route planned:")
        print(f"   Current mood: {mood}")
        print(f"   Trajectory: {traj}")
        print(f"   Base song: {os.path.basename(fav_song) if fav_song else 'general (no personalization)'}")

        return {
            'mood': mood,
            'trajectory': traj,
            'favorite_song': fav_song,
        }


def run_interactive():
    """Run the full interactive mood routing + trajectory experience."""
    router = MoodRouter()
    config = router.run()

    extractor = AudioFeatureExtractor(n_mfcc=13)
    similarity = SimilarityEngine(dim=93, index_type='flat')
    analyzer = EmotionAnalyzer()

    engine = MoodTrajectoryEngine(
        similarity_engine=similarity,
        emotion_analyzer=analyzer,
    )

    # Analyze favorite song if provided
    query_vector = None
    if config['favorite_song']:
        try:
            print(f"\n🔬 Analyzing your song...")
            features = extractor.extract(config['favorite_song'])
            query_vector = extractor.to_vector(features)
            query_emotion = analyzer.predict(config['favorite_song'])

            t = float(features['tempo'].item()) if hasattr(features['tempo'], 'item') else float(features['tempo'])
            print(f"\n📊 Your song's emotional profile:")
            print(f"   Valence: {query_emotion['valence']:.2f}  (sad {'─'*10} happy)")
            print(f"   Arousal: {query_emotion['arousal']:.2f}  (calm {'─'*10} excited)")
            print(f"   Mood:    {query_emotion['moods'][0]}")
            print(f"   Tempo:   {t:.0f} BPM")

            # Find similar songs in index (if exists)
            if similarity.size > 0:
                similar = similarity.search(query_vector, k=5)
                if similar:
                    print(f"\n🎧 Found {len(similar)} similar songs in your library")

        except Exception as e:
            print(f"  ⚠ Could not analyze song: {e}")
    else:
        print("\n📊 No personalization — showing general trajectory blueprint")

    # Build trajectory
    result = engine.build_trajectory(
        trajectory_name=config['trajectory'],
        query_vector=query_vector,
        n_songs_per_step=2,
    )

    print(engine.trajectory_to_timeline(result))

    # Next steps
    if similarity.size == 0:
        print("\n💡 To get real song recommendations:")
        print("   • Build an index:   python -m src.run build-index")
        print("   • Or add a favorite song so I can curate around it")
    else:
        print("\n💡 Resonate ready with", similarity.size, "songs indexed")

    return result


if __name__ == "__main__":
    run_interactive()
