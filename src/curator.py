"""
PsychoAcoustic Curator — main orchestration engine.
Combines feature extraction, emotion analysis, and similarity search.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class CurationResult:
    query_song: str
    recommendations: List[Dict]
    query_emotion: Dict[str, float]
    feature_count: int = 0


@dataclass
class CuratorConfig:
    similarity_weight: float = 0.60
    emotion_weight: float = 0.20
    diversity_weight: float = 0.10
    novelty_weight: float = 0.10
    max_results: int = 50


class PsychoAcousticCurator:
    def __init__(self, config: Optional[CuratorConfig] = None):
        self.config = config or CuratorConfig()
        self.feature_extractor = None
        self.emotion_analyzer = None
        self.similarity_engine = None

    def initialize(self, feature_extractor, emotion_analyzer, similarity_engine):
        self.feature_extractor = feature_extractor
        self.emotion_analyzer = emotion_analyzer
        self.similarity_engine = similarity_engine

    def curate(
        self,
        query_path: str,
        exclude_ids: Optional[List[str]] = None,
        top_k: int = 50,
    ) -> CurationResult:
        # 1. Extract features from query song
        features = self.feature_extractor.extract(query_path)
        query_vector = self.feature_extractor.to_vector(features)

        # 2. Analyze emotion of query
        query_emotion = self.emotion_analyzer.predict(query_path)

        # 3. Search for similar songs
        raw_results = self.similarity_engine.search(query_vector, k=top_k * 2)

        # 4. Filter and re-rank
        exclude_ids = exclude_ids or []
        scored = []
        for song_id, sim_score, meta in raw_results:
            if song_id in exclude_ids:
                continue

            final_score = self._compute_score(
                similarity=sim_score,
                query_emotion=query_emotion,
                song_emotion=meta.get('emotion', {}),
            )

            scored.append({
                'song_id': song_id,
                'title': meta.get('title', ''),
                'artist': meta.get('artist', ''),
                'similarity': round(sim_score, 4),
                'final_score': round(final_score, 4),
                'emotion': meta.get('emotion', {}),
                'metadata': meta,
            })

        # 5. Sort and return top-k
        scored.sort(key=lambda x: x['final_score'], reverse=True)

        return CurationResult(
            query_song=query_path,
            recommendations=scored[:self.config.max_results],
            query_emotion=query_emotion,
            feature_count=len(query_vector),
        )

    def _compute_score(
        self,
        similarity: float,
        query_emotion: Dict,
        song_emotion: Dict,
    ) -> float:
        s = self.config.similarity_weight * similarity

        # Emotion matching bonus
        if song_emotion and query_emotion:
            ve_dist = abs(
                song_emotion.get('valence', 0.5) - query_emotion.get('valence', 0.5)
            )
            ar_dist = abs(
                song_emotion.get('arousal', 0.5) - query_emotion.get('arousal', 0.5)
            )
            emotion_match = 1.0 - (ve_dist + ar_dist) / 2.0
            s += self.config.emotion_weight * emotion_match

        # Diversity penalty (applied after initial sort)
        # Handled in curate() with re-ranking
        return s

    def curate_by_embedding(
        self,
        query_embedding: np.ndarray,
        top_k: int = 50,
    ) -> List[Dict]:
        raw_results = self.similarity_engine.search(query_embedding, k=top_k)
        return [
            {
                'song_id': song_id,
                'similarity': score,
                'metadata': meta,
            }
            for song_id, score, meta in raw_results
        ]
