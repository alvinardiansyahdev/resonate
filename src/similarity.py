"""
FAISS-based Similarity Engine — billion-scale nearest neighbor search.
"""

import numpy as np
import faiss
from typing import Optional, List, Tuple


class SimilarityEngine:
    def __init__(self, dim: int = 128, index_type: str = 'flat'):
        self._dim = dim
        self.index_type = index_type
        self.index = None
        self.song_ids: List[str] = []
        self.metadata: List[dict] = []

        if index_type == 'flat':
            self.index = faiss.IndexFlatIP(dim)  # Inner product = cosine for normalized vectors
        elif index_type == 'ivf':
            quantizer = faiss.IndexFlatIP(dim)
            nlist = 100  # number of clusters
            self.index = faiss.IndexIVFFlat(quantizer, dim, nlist, faiss.METRIC_INNER_PRODUCT)
        elif index_type == 'hnsw':
            self.index = faiss.IndexHNSWFlat(dim, 32)  # 32 neighbors per node
            self.index.hnsw.efConstruction = 200
        else:
            raise ValueError(f"Unknown index type: {index_type}")

    def normalize(self, vectors: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        return vectors / (norms + 1e-10)

    def add_songs(self, vectors: np.ndarray, song_ids: List[str], metadata: Optional[List[dict]] = None):
        vectors = self.normalize(vectors).astype(np.float32)

        if self.index_type == 'ivf' and not self.index.is_trained:
            self.index.train(vectors)

        self.index.add(vectors)
        self.song_ids.extend(song_ids)
        if metadata:
            self.metadata.extend(metadata)

    def search(self, query_vector: np.ndarray, k: int = 20) -> List[Tuple[str, float, dict]]:
        query_vector = self.normalize(query_vector.reshape(1, -1)).astype(np.float32)

        scores, indices = self.index.search(query_vector, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.song_ids) and score > 0:
                results.append((
                    self.song_ids[idx],
                    float(score),
                    self.metadata[idx] if idx < len(self.metadata) else {}
                ))

        return results

    def save(self, path: str):
        faiss.write_index(self.index, f"{path}.index")
        import pickle
        with open(f"{path}.meta.pkl", 'wb') as f:
            pickle.dump({
                'song_ids': self.song_ids,
                'metadata': self.metadata,
            }, f)

    def load(self, path: str):
        self.index = faiss.read_index(f"{path}.index")
        import pickle
        with open(f"{path}.meta.pkl", 'rb') as f:
            data = pickle.load(f)
            self.song_ids = data['song_ids']
            self.metadata = data['metadata']

    @property
    def size(self) -> int:
        return self.index.ntotal if self.index else 0

    @property
    def dim(self) -> int:
        return self._dim
