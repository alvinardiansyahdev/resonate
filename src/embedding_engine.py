"""
Deep Audio Embedding Engine — CLAP-based audio representation.
Projects audio into a shared embedding space for similarity search.
"""

import numpy as np
from typing import Optional


class AudioEmbeddingEngine:
    def __init__(self, model_name: str = 'laion/clap-htsat-unfused', device: str = 'cpu'):
        self.model_name = model_name
        self.device = device
        self.model = None
        self.processor = None
        self._load_model()

    def _load_model(self):
        try:
            import torch
            import torch.nn.functional as F
            from transformers import ClapModel, ClapProcessor

            self.model = ClapModel.from_pretrained(self.model_name).to(self.device)
            self.processor = ClapProcessor.from_pretrained(self.model_name)
            self.model.eval()
            print(f"CLAP model loaded: {self.model_name}")
        except Exception as e:
            print(f"Warning: Could not load CLAP model ({e}). Using librosa features only.")

    def get_audio_embedding(self, audio_path: str) -> Optional[np.ndarray]:
        if self.model is None:
            return None

        import torch
        import librosa

        try:
            y, sr = librosa.load(audio_path, sr=48000, mono=True, duration=30.0)

            inputs = self.processor(
                audios=y,
                sampling_rate=48000,
                return_tensors="pt",
                padding=True,
            ).to(self.device)

            with torch.no_grad():
                embeddings = self.model.get_audio_features(**inputs)

            return embeddings.cpu().numpy().flatten()

        except Exception as e:
            print(f"Embedding error for {audio_path}: {e}")
            return None

    def get_text_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get embedding for text description (for cross-modal search)."""
        if self.model is None:
            return None

        import torch

        try:
            inputs = self.processor(
                text=[text],
                return_tensors="pt",
                padding=True,
            ).to(self.device)

            with torch.no_grad():
                embeddings = self.model.get_text_features(**inputs)

            return embeddings.cpu().numpy().flatten()

        except Exception as e:
            print(f"Text embedding error: {e}")
            return None

    def compute_similarity(self, embed1: np.ndarray, embed2: np.ndarray) -> float:
        """Cosine similarity between two embeddings."""
        norm1 = embed1 / (np.linalg.norm(embed1) + 1e-10)
        norm2 = embed2 / (np.linalg.norm(embed2) + 1e-10)
        return float(np.dot(norm1, norm2))

    def extract_all_embeddings(self, audio_paths: list, batch_size: int = 8) -> np.ndarray:
        """Batch extract embeddings for multiple audio files."""
        if self.model is None:
            return None

        import torch
        import librosa
        from tqdm import tqdm

        all_embeddings = []

        for i in tqdm(range(0, len(audio_paths), batch_size), desc="Extracting embeddings"):
            batch = audio_paths[i:i + batch_size]
            batch_audios = []
            valid_indices = []

            for j, path in enumerate(batch):
                try:
                    y, sr = librosa.load(path, sr=48000, mono=True, duration=30.0)
                    batch_audios.append(y)
                    valid_indices.append(j)
                except Exception:
                    continue

            if not batch_audios:
                continue

            inputs = self.processor(
                audios=batch_audios,
                sampling_rate=48000,
                return_tensors="pt",
                padding=True,
            ).to(self.device)

            with torch.no_grad():
                embeddings = self.model.get_audio_features(**inputs)
                all_embeddings.append(embeddings.cpu().numpy())

        if all_embeddings:
            return np.concatenate(all_embeddings, axis=0)
        return np.array([])
