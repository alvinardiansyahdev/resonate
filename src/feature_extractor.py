"""
Audio Feature Extractor — librosa-based pipeline.
Extracts ~80-dimensional feature vector from any audio file.
"""

import librosa
import numpy as np
from typing import Dict, Optional


class AudioFeatureExtractor:
    def __init__(self, sr: int = 22050, n_mfcc: int = 20, hop_length: int = 512):
        self.sr = sr
        self.n_mfcc = n_mfcc
        self.hop_length = hop_length

    def extract(self, file_path: str) -> Dict[str, np.ndarray]:
        y, sr = librosa.load(file_path, sr=self.sr, mono=True)
        return self._extract_from_waveform(y, sr)

    def extract_from_bytes(self, audio_bytes: bytes) -> Dict[str, np.ndarray]:
        import soundfile as sf
        import io
        y, sr = sf.read(io.BytesIO(audio_bytes))
        if len(y.shape) > 1:
            y = y.mean(axis=1)
        if sr != self.sr:
            y = librosa.resample(y, orig_sr=sr, target_sr=self.sr)
        return self._extract_from_waveform(y, self.sr)

    def _extract_from_waveform(self, y: np.ndarray, sr: int) -> Dict[str, np.ndarray]:
        features = {}

        # --- Spectral features ---
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=self.n_mfcc, hop_length=self.hop_length)
        features['mfcc_mean'] = mfcc.mean(axis=1)
        features['mfcc_std'] = mfcc.std(axis=1)

        # Spectral centroid (brightness)
        cent = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=self.hop_length)
        features['spectral_centroid'] = np.array([cent.mean(), cent.std()])

        # Spectral contrast (timbre texture)
        contrast = librosa.feature.spectral_contrast(y=y, sr=sr, hop_length=self.hop_length)
        features['spectral_contrast_mean'] = contrast.mean(axis=1)
        features['spectral_contrast_std'] = contrast.std(axis=1)

        # Spectral rolloff
        rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, hop_length=self.hop_length)
        features['spectral_rolloff'] = np.array([rolloff.mean(), rolloff.std()])

        # Spectral bandwidth
        bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr, hop_length=self.hop_length)
        features['spectral_bandwidth'] = np.array([bandwidth.mean(), bandwidth.std()])

        # Zero crossing rate (noisiness)
        zcr = librosa.feature.zero_crossing_rate(y, hop_length=self.hop_length)
        features['zero_crossing_rate'] = np.array([zcr.mean(), zcr.std()])

        # RMS energy
        rms = librosa.feature.rms(y=y, hop_length=self.hop_length)
        features['rms_mean'] = np.array([rms.mean(), rms.std()])

        # --- Harmonic features ---
        # Chroma
        chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=self.hop_length)
        features['chroma_mean'] = chroma.mean(axis=1)
        features['chroma_std'] = chroma.std(axis=1)

        # Tonnetz (tonal centroid)
        tonnetz = librosa.feature.tonnetz(y=y, sr=sr)
        features['tonnetz_mean'] = tonnetz.mean(axis=1)
        features['tonnetz_std'] = tonnetz.std(axis=1)

        # Harmonic-percussive separation
        y_harm, y_perc = librosa.effects.hpss(y)
        features['harmonic_ratio'] = np.array([np.sum(y_harm**2) / (np.sum(y**2) + 1e-8)])

        # --- Rhythmic features ---
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        features['tempo'] = np.array([tempo])

        if len(beats) > 1:
            beat_intervals = np.diff(beats) / sr * 1000  # ms between beats
            features['beat_interval_mean'] = np.array([beat_intervals.mean()])
            features['beat_interval_std'] = np.array([beat_intervals.std()])
        else:
            features['beat_interval_mean'] = np.array([0.0])
            features['beat_interval_std'] = np.array([0.0])

        # Tempogram (summarize - full tempogram is too high-dim)
        tempogram = librosa.feature.tempogram(y=y, sr=sr, hop_length=self.hop_length)
        features['tempogram_mean'] = np.array([tempogram.mean()])
        features['tempogram_std'] = np.array([tempogram.std()])
        features['tempogram_max'] = np.array([tempogram.max()])

        return features

    def to_vector(self, features: Dict[str, np.ndarray]) -> np.ndarray:
        vectors = []
        for key in sorted(features.keys()):
            vectors.append(features[key].flatten())
        return np.concatenate(vectors).astype(np.float32)

    def get_feature_names(self) -> list:
        return sorted([
            'mfcc_mean', 'mfcc_std', 'spectral_centroid',
            'spectral_contrast_mean', 'spectral_contrast_std',
            'spectral_rolloff', 'spectral_bandwidth',
            'zero_crossing_rate', 'rms_mean',
            'chroma_mean', 'chroma_std',
            'tonnetz_mean', 'tonnetz_std',
            'harmonic_ratio',
            'tempo', 'beat_interval_mean', 'beat_interval_std',
            'tempogram_mean', 'tempogram_std', 'tempogram_max'
        ])
