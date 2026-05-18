"""
Mood Trajectory Engine — creates smooth emotional paths through VA space.
Transitions user from current mood to target mood via carefully sequenced songs.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum


class Mood(Enum):
    SAD = (0.2, 0.2, "sad", "melancholic, gloomy")
    DEPRESSED = (0.15, 0.1, "depressed", "heavy, hopeless")
    ANGRY = (0.2, 0.8, "angry", "tense, frustrated")
    ANXIOUS = (0.3, 0.75, "anxious", "worried, stressed")
    NEUTRAL = (0.5, 0.5, "neutral", "balanced")
    CALM = (0.6, 0.2, "calm", "peaceful, relaxed")
    HAPPY = (0.75, 0.6, "happy", "joyful, upbeat")
    EXCITED = (0.8, 0.8, "excited", "energetic, pumped")
    RELAXED = (0.7, 0.3, "relaxed", "serene, chill")
    FOCUSED = (0.5, 0.6, "focused", "alert, concentrated")
    TENSE = (0.3, 0.6, "tense", "stressed, on edge")
    TIRED = (0.35, 0.15, "tired", "drained, low energy")

    @classmethod
    def from_name(cls, name: str):
        for mood in cls:
            if mood.value[2] == name.lower():
                return mood
        return cls.NEUTRAL

    @property
    def valence(self) -> float:
        return self.value[0]

    @property
    def arousal(self) -> float:
        return self.value[1]

    @property
    def label(self) -> str:
        return self.value[2]

    @property
    def description(self) -> str:
        return self.value[3]


# Pre-defined mood transition paths (curated for emotional safety)
DEFAULT_TRAJECTORIES = {
    # Sad → Happy: slow, gentle rise
    'sad_to_happy': {
        'start': Mood.SAD,
        'end': Mood.HAPPY,
        'waypoints': [
            (0.25, 0.2, "gently sad"),
            (0.3, 0.25, "slightly lighter"),
            (0.4, 0.3, "warming up"),
            (0.5, 0.35, "neutral calm"),
            (0.55, 0.4, "quiet hope"),
            (0.6, 0.45, "lifting"),
            (0.65, 0.5, "brightening"),
            (0.75, 0.55, "content"),
            (0.75, 0.6, "happy"),
        ],
        'steps': 9,
    },
    # Angry → Calm → Happy: bring arousal down first, then valence up
    'angry_to_happy': {
        'start': Mood.ANGRY,
        'end': Mood.HAPPY,
        'waypoints': [
            (0.25, 0.75, "vent"),
            (0.3, 0.7, "releasing"),
            (0.35, 0.6, "settling"),
            (0.4, 0.5, "neutralizing"),
            (0.5, 0.4, "calming"),
            (0.55, 0.35, "peace"),
            (0.6, 0.4, "lifting"),
            (0.7, 0.5, "bright"),
            (0.75, 0.6, "happy"),
        ],
        'steps': 9,
    },
    # Anxious → Calm: drop arousal gradually
    'anxious_to_calm': {
        'start': Mood.ANXIOUS,
        'end': Mood.CALM,
        'waypoints': [
            (0.3, 0.7, "acknowledging"),
            (0.35, 0.65, "breathing"),
            (0.4, 0.55, "slowing down"),
            (0.45, 0.45, "settling"),
            (0.5, 0.35, "quieting"),
            (0.55, 0.3, "serene"),
            (0.6, 0.25, "peaceful"),
        ],
        'steps': 7,
    },
    # Tired → Focused: gently increase arousal
    'tired_to_focused': {
        'start': Mood.TIRED,
        'end': Mood.FOCUSED,
        'waypoints': [
            (0.35, 0.15, "resting"),
            (0.4, 0.2, "stirring"),
            (0.4, 0.3, "waking up"),
            (0.45, 0.4, "warming"),
            (0.45, 0.5, "engaging"),
            (0.5, 0.55, "focusing"),
            (0.5, 0.6, "focused"),
        ],
        'steps': 7,
    },
    # Neutral → Happy: simple lift
    'neutral_to_happy': {
        'start': Mood.NEUTRAL,
        'end': Mood.HAPPY,
        'waypoints': [
            (0.5, 0.5, "neutral"),
            (0.55, 0.5, "noticing"),
            (0.6, 0.5, "warming"),
            (0.65, 0.55, "lifting"),
            (0.7, 0.55, "bright"),
            (0.75, 0.6, "happy"),
        ],
        'steps': 6,
    },
}


@dataclass
class TrajectoryStep:
    valence: float
    arousal: float
    label: str
    songs: List[Dict] = field(default_factory=list)


@dataclass
class TrajectoryResult:
    trajectory_name: str
    start_mood: str
    end_mood: str
    steps: List[TrajectoryStep]
    total_songs: int = 0


class MoodTrajectoryEngine:
    def __init__(self, similarity_engine=None, emotion_analyzer=None):
        self.similarity = similarity_engine
        self.emotion_analyzer = emotion_analyzer

    def get_available_trajectories(self) -> Dict:
        """Return pre-defined trajectories with readable names."""
        return {
            'sad_to_happy': "😢 Sad → 😊 Happy (gentle rise)",
            'angry_to_happy': "😠 Angry → 😊 Happy (calm down first)",
            'anxious_to_calm': "😰 Anxious → 😌 Calm (slow down)",
            'tired_to_focused': "😴 Tired → 🎯 Focused (wake up gently)",
            'neutral_to_happy': "😐 Neutral → 😊 Happy (simple lift)",
        }

    def generate_sigmoid_path(
        self,
        start_va: Tuple[float, float],
        end_va: Tuple[float, float],
        n_steps: int = 8,
        curvature: float = 0.5,
    ) -> List[Tuple[float, float, str]]:
        """
        Generate smooth sigmoid path from start to end VA.

        curvature: 0 = linear, >0 = more S-curve (start/end slower, middle faster)
        """
        steps = []
        for i in range(n_steps):
            t = i / (n_steps - 1)  # 0..1

            # Sigmoid interpolation: smooth S-curve
            s = 1 / (1 + np.exp(-curvature * (t - 0.5) * 10))
            s = (s - 0.5) / (1 / (1 + np.exp(-curvature * (-0.5) * 10)) - 0.5)  # normalize

            v = start_va[0] + (end_va[0] - start_va[0]) * s
            a = start_va[1] + (end_va[1] - start_va[1]) * s

            # Add slight wobble to feel organic (not a perfectly smooth robot line)
            wobble = 0.02 * np.sin(i * 1.5)
            v = np.clip(v + wobble, 0.05, 0.95)
            a = np.clip(a + wobble * 0.5, 0.05, 0.95)

            steps.append((float(v), float(a), f"step_{i+1}"))

        return steps

    def find_songs_for_step(
        self,
        target_va: Tuple[float, float],
        query_vector: np.ndarray,
        user_genre_profile: Optional[np.ndarray] = None,
        exclude_ids: set = None,
        top_k: int = 20,
        emotion_weight: float = 0.3,
    ) -> List[Dict]:
        """
        Find songs that:
        1. Are near the target VA coordinate (emotion match)
        2. Are similar to user's acoustic fingerprint
        """
        if self.similarity is None:
            return []

        # Get content-based similarity results
        content_results = self.similarity.search(query_vector, k=top_k * 3)

        scored = []
        for song_id, sim_score, meta in content_results:
            if exclude_ids and song_id in exclude_ids:
                continue

            # Emotion matching
            song_emotion = meta.get('emotion', {})
            song_va = (
                song_emotion.get('valence', 0.5),
                song_emotion.get('arousal', 0.5),
            )

            # Euclidean distance in VA space
            va_dist = np.sqrt(
                (song_va[0] - target_va[0])**2 +
                (song_va[1] - target_va[1])**2
            )
            va_score = 1.0 - min(va_dist / 1.5, 1.0)  # normalized 0-1

            # Combined score
            final_score = (1 - emotion_weight) * sim_score + emotion_weight * va_score

            scored.append({
                'song_id': song_id,
                'similarity': sim_score,
                'va_score': va_score,
                'final_score': final_score,
                'valence': song_va[0],
                'arousal': song_va[1],
                'metadata': meta,
            })

        scored.sort(key=lambda x: x['final_score'], reverse=True)
        return scored[:top_k]

    def build_trajectory(
        self,
        trajectory_name: str,
        query_audio_path: Optional[str] = None,
        query_vector: Optional[np.ndarray] = None,
        custom_start: Optional[Tuple[float, float]] = None,
        custom_end: Optional[Tuple[float, float]] = None,
        n_songs_per_step: int = 3,
        smooth_transitions: bool = True,
    ) -> TrajectoryResult:
        """Build a full mood trajectory playlist."""
        # Get trajectory definition
        if trajectory_name in DEFAULT_TRAJECTORIES:
            traj = DEFAULT_TRAJECTORIES[trajectory_name]
            start_mood = traj['start']
            end_mood = traj['end']
            waypoints = traj['waypoints']
            n_steps = traj['steps']
        elif custom_start and custom_end:
            start_mood = Mood.NEUTRAL
            end_mood = Mood.NEUTRAL
            waypoints = self.generate_sigmoid_path(custom_start, custom_end, n_steps=8)
            n_steps = len(waypoints)
        else:
            raise ValueError(f"Unknown trajectory: {trajectory_name}")

        # Generate smooth path
        if trajectory_name in DEFAULT_TRAJECTORIES:
            path = [
                (wp[0], wp[1], wp[2])
                for wp in waypoints
            ]
        else:
            path = waypoints

        # If we have a query (user's favorite song), extract vector
        if query_vector is None and query_audio_path and self.similarity:
            from src.feature_extractor import AudioFeatureExtractor
            ext = AudioFeatureExtractor()
            feat = ext.extract(query_audio_path)
            query_vector = ext.to_vector(feat)

        # For each step, find songs
        trajectory_steps = []
        used_songs = set()
        prev_tempo = None

        for v, a, label in path:
            step_songs = self.find_songs_for_step(
                target_va=(v, a),
                query_vector=query_vector,
                exclude_ids=used_songs,
                top_k=n_songs_per_step * 3,
            )

            # Apply smooth transition filter
            if smooth_transitions and prev_tempo and step_songs:
                step_songs = self._smooth_filter(step_songs, prev_tempo)

            # Take top N
            selected = step_songs[:n_songs_per_step]

            # Update used songs and prev tempo
            for s in selected:
                used_songs.add(s['song_id'])

            step = TrajectoryStep(
                valence=v,
                arousal=a,
                label=label,
                songs=selected,
            )
            trajectory_steps.append(step)

            # Update prev_tempo from last selected song
            if selected:
                emo = selected[0].get('metadata', {}).get('emotion', {})
                prev_tempo = emo.get('arousal', a)  # rough proxy

        total = sum(len(s.songs) for s in trajectory_steps)
        return TrajectoryResult(
            trajectory_name=trajectory_name,
            start_mood=start_mood.label,
            end_mood=end_mood.label,
            steps=trajectory_steps,
            total_songs=total,
        )

    def _smooth_filter(self, songs: List[Dict], prev_tempo: float) -> List[Dict]:
        """Reorder songs so adjacent tempos don't jump too much."""
        # Simple: sort by closeness to prev_tempo
        songs_with_diff = [
            (s, abs(s.get('arousal', 0.5) - prev_tempo))
            for s in songs
        ]
        songs_with_diff.sort(key=lambda x: x[1])
        return [s for s, _ in songs_with_diff]

    def trajectory_to_timeline(self, result: TrajectoryResult) -> str:
        """Visualize the trajectory as a timeline."""
        lines = []
        lines.append(f"\n{'='*60}")
        lines.append(f"🧭 MOOD TRAJECTORY: {result.start_mood} → {result.end_mood}")
        lines.append(f"{'='*60}")

        for i, step in enumerate(result.steps):
            v, a = step.valence, step.arousal
            mood_label = self._va_to_label(v, a)
            bar_v = '█' * int(v * 20) + '░' * (20 - int(v * 20))
            bar_a = '█' * int(a * 10) + '░' * (10 - int(a * 10))

            lines.append(f"\nStep {i+1}: {step.label}")
            lines.append(f"  Valence {v:.2f} |{bar_v}| {mood_label}")
            lines.append(f"  Arousal {a:.2f} |{bar_a}|")

            if step.songs:
                for j, song in enumerate(step.songs):
                    meta = song.get('metadata', {})
                    title = meta.get('title', song['song_id'])[:30]
                    lines.append(f"    {j+1}. {title} (fit: {song['final_score']:.2f})")
            else:
                lines.append(f"    (no songs found for this stage)")

        lines.append(f"\n{'='*60}")
        lines.append(f"Total: {result.total_songs} songs across {len(result.steps)} stages")
        lines.append(f"{'='*60}")
        return '\n'.join(lines)

    def _va_to_label(self, v: float, a: float) -> str:
        if v > 0.6 and a > 0.6: return "excited"
        if v > 0.6 and a > 0.4: return "happy"
        if v > 0.6 and a <= 0.4: return "relaxed"
        if v > 0.5 and a > 0.5: return "warm"
        if v <= 0.5 and a > 0.6: return "tense"
        if v <= 0.5 and a <= 0.3: return "sad"
        if v <= 0.4 and a > 0.5: return "frustrated"
        return "neutral"
