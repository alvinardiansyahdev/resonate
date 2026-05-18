"""
Music Emotion Analyzer — predicts valence/arousal from audio.
Uses classical ML as fallback (Music2Emo when available).
"""

import numpy as np
from typing import Dict, Tuple, Optional


class EmotionAnalyzer:
    def __init__(self, use_music2emo: bool = False):
        self.model = None
        if use_music2emo:
            try:
                from music2emo import Music2emo
                self.model = Music2emo()
                self.model_type = 'music2emo'
            except ImportError:
                print("Music2Emo not installed. Using rule-based fallback.")
                self.model_type = 'rule'
        else:
            self.model_type = 'rule'

    def predict(self, audio_path: str) -> Dict[str, float]:
        if self.model_type == 'music2emo':
            return self._predict_music2emo(audio_path)
        else:
            return self._predict_rule_based(audio_path)

    def _predict_music2emo(self, audio_path: str) -> Dict[str, float]:
        result = self.model.predict(audio_path)
        return {
            'valence': result['valence'],
            'arousal': result['arousal'],
            'moods': result.get('predicted_moods', []),
        }

    def _predict_rule_based(self, audio_path: str) -> Dict[str, float]:
        """
        Rule-based emotion prediction from audio features.
        Based on established music psychology correlations:
        - Tempo ↑ → Arousal ↑
        - Spectral centroid ↑ (bright) → Valence ↑
        - Mode major → Valence ↑
        - RMS energy ↑ → Arousal ↑
        """
        import librosa

        y, sr = librosa.load(audio_path, sr=22050)

        # Tempo → Arousal
        tempo_arr, _ = librosa.beat.beat_track(y=y, sr=sr)
        tempo = float(tempo_arr.item() if hasattr(tempo_arr, 'item') else tempo_arr)

        # Spectral centroid → Valence (bright = positive)
        cent = librosa.feature.spectral_centroid(y=y, sr=sr)
        cent_mean = float(cent.mean())

        # RMS → Arousal
        rms = librosa.feature.rms(y=y)
        rms_mean = float(rms.mean())

        # Zero crossing rate → Energy/agitation
        zcr = librosa.feature.zero_crossing_rate(y)
        zcr_mean = float(zcr.mean())

        # Harmonic ratio → Valence (more harmonic = more pleasant)
        y_harm, y_perc = librosa.effects.hpss(y)
        harm_ratio = float(np.sum(y_harm ** 2) / (np.sum(y ** 2) + 1e-8))

        # Key/mode detection
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        chroma_mean = chroma.mean(axis=1)
        major_likelihood = chroma_mean[0]  # C major proxy
        minor_likelihood = chroma_mean[3]  # C minor proxy
        is_major = major_likelihood > minor_likelihood

        # Normalize to 0-1 scale
        norm_tempo = float(np.clip(tempo / 200.0, 0.0, 1.0))
        norm_cent = float(np.clip(cent_mean / 5000.0, 0.0, 1.0))
        norm_rms = float(np.clip(rms_mean * 10, 0.0, 1.0))
        norm_zcr = float(np.clip(zcr_mean * 10, 0.0, 1.0))

        # Valence: bright + major + harmonic + not too noisy
        valence = float(np.clip(
            0.3 * norm_cent +
            0.25 * (1.0 if is_major else 0.3) +
            0.25 * harm_ratio +
            0.2 * (1.0 - norm_zcr),
        0.0, 1.0))

        # Arousal: fast + loud + noisy
        arousal = float(np.clip(
            0.4 * norm_tempo +
            0.3 * norm_rms +
            0.3 * norm_zcr,
        0.0, 1.0))

        # Mood tags based on VA quadrant
        moods = self._va_to_moods(valence, arousal)

        return {
            'valence': round(float(valence), 3),
            'arousal': round(float(arousal), 3),
            'moods': moods,
        }

    def _va_to_moods(self, valence: float, arousal: float) -> list:
        """Map valence/arousal to mood tags (Russell's circumplex)."""
        if valence > 0.6 and arousal > 0.6:
            return ['happy', 'excited', 'energetic']
        elif valence > 0.6 and arousal <= 0.6:
            return ['relaxed', 'peaceful', 'calm']
        elif valence <= 0.6 and arousal > 0.6:
            return ['angry', 'tense', 'frustrated']
        else:
            return ['sad', 'melancholic', 'gloomy']

    def analyze_dataset(
        self, feature_vectors: np.ndarray, audio_paths: list
    ) -> np.ndarray:
        """Batch predict emotions for a dataset."""
        # Simple linear mapping from features to VA
        # Assumes feature_vectors include energy, tempo, etc. at known indices
        results = []
        for path in audio_paths:
            try:
                result = self.predict(path)
                results.append([result['valence'], result['arousal']])
            except Exception:
                results.append([0.5, 0.5])  # neutral fallback
        return np.array(results)
