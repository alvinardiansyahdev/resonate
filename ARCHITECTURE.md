# PsychoAcoustic Engine — Arsitektur & Research

## 1. Core Insight: Kenapa "Healing Music" Gagal

### Masalah:
- Musik klasik / AI-generated / "curated therapy music" → **kurang dopamin**
- Orang dengan ADHD/Bipolar butuh **familiar sonic pattern** untuk trigger reward system
- Mereka sudah punya "playlist mental" — lagu-lagu yang TAHU mereka akan works

### Solusi:
**Jangan推荐 musik asing. Analisa fingerprint lagu favorit mereka, lalu temukan jutaan lagu lain yang SAMA SECARA AKUSTIK.**

```
User's Favorite Song
        ↓
[Fingerprint Extraction]
  - Timbre (MFCCs)
  - Tempo (BPM)
  - Harmony (Key, Mode, Chord)
  - Energy, Valence, Danceability
  - Instrumentation
  - Vocal Characteristics
  - Rhythm Pattern
        ↓
[Similarity Search across millions of songs]
        ↓
Top-K matches with same acoustic profile
        ↓
User gets DOPAMINE (familiar) + VARIETY (new but similar)
```

## 2. Neuroscience Validation

| Mekanisme | Penjelasan | Kenapa Relevant untuk ADHD/Bipolar |
|---|---|---|
| **Predictive Coding** | Otak constantly predicts what comes next in music. Familiar patterns → correct prediction → dopamine reward | ADHD brain understimulated; familiar music provides reliable prediction-reward loop |
| **Dopamine Release** | Nucleus accumbens teraktivasi saat dengar musik familiar | Bipolar mood episodes butuh emotional regulation via reliable reward |
| **Default Mode Network** | Musik familiar mengaktifkan DMN — self-reflection, emotional processing | ADHD大脑 constantly task-switching; familiar music anchors attention |
| **Entrainment** | Brainwaves synchronize to familiar rhythmic patterns | ADHD: beta entrainment untuk focus. Bipolar: alpha/theta untuk stabilization |

**Key Paper**: Salimpoor et al. (2011) "Anatomically distinct dopamine release during anticipation and experience of peak emotion to music" — *Nature Neuroscience*

## 3. Arsitektur Sistem

```
┌──────────────────────────────────────────────────────────────────┐
│                         INPUT LAYER                               │
│  User selects 1-N favorite songs (Spotify link / file upload)    │
└──────────────────────────┬───────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────────┐
│                    FEATURE EXTRACTION PIPELINE                    │
│                                                                   │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │
│  │ librosa         │  │ essentia         │  │ CLAP / MERT     │ │
│  │ (spectral,      │  │ (high-level      │  │ (deep audio     │ │
│  │  rhythmic)      │  │  descriptors)    │  │  embeddings)    │ │
│  └────────┬────────┘  └────────┬─────────┘  └────────┬────────┘ │
│           ↓                    ↓                      ↓          │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              Feature Vector (512-1024 dims)                  │ │
│  │  MFCCs, Tempo, Key, Mode, Energy, Valence,                  │ │
│  │  Danceability, Spectral, Chroma, Tonnetz, Embedding         │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────┬───────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────────┐
│                    SIMILARITY ENGINE                              │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  FAISS (Facebook AI Similarity Search)                       │ │
│  │  - IVF + HNSW indexing for billion-scale search              │ │
│  │  - Cosine similarity / L2 distance                           │ │
│  │  - GPU-accelerated                                           │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Music Database (100K - 10M+ songs)                          │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │ │
│  │  │ MTG-     │ │ FMA      │ │ Spotify  │ │ YouTube  │      │ │
│  │  │ Jamendo  │ │ (Free    │ │ API      │ │ Audio    │      │ │
│  │  │ (55K)    │ │ Music)   │ │ (metadata│ │ Dataset  │      │ │
│  │  │          │ │ (100K)   │ │ + audio) │ │          │      │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────┬───────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────────┐
│                    CURATION ENGINE                                │
│                                                                   │
│  1. Weighted similarity scoring:                                  │
│     - 60% Audio fingerprint match                                 │
│     - 20% Emotion profile match (valence/arousal)                 │
│     - 10% Genre/Cultural affinity                                 │
│     - 10% Novelty factor (not TOO similar)                        │
│                                                                   │
│  2. Emotion tagging (Music2Emo model)                             │
│  3. Diversity filtering                                           │
│  4. Personalization learning (feedback loop)                      │
└──────────────────────────┬───────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────────┐
│                    OUTPUT                                         │
│  Ranked playlist of songs that:                                   │
│  ✓ Sound like your favorites (acoustic fingerprint)              │
│  ✓ Hit the same emotional profile                                 │
│  ✓ Give dopamine (familiar patterns)                              │
│  ✓ But are NEW discoveries                                        │
└──────────────────────────────────────────────────────────────────┘
```

## 4. Tech Stack

| Layer | Technology | Kenapa |
|---|---|---|
| Audio Feature Extraction | **librosa** + **essentia** | Mature, well-documented, extensive feature set |
| Deep Audio Embeddings | **CLAP** (LAION) or **MERT** (Music2Emo) | State-of-the-art audio representations |
| Similarity Search | **FAISS** (Facebook AI) | Billion-scale, GPU-accelerated, open source |
| Emotion Model | **Music2Emo** (AMAAI Lab) | Best open-source MER model (2025) |
| Database | **PostgreSQL** + **FAISS index** | Structured metadata + vector search |
| Backend | **FastAPI** (Python) | Async, high-performance |
| Frontend | **React** or **Electron** | Cross-platform desktop |
| Dataset | **MTG-Jamendo** (55K) + **FMA** (100K) + **Spotify API** | Largest free music datasets |

## 5. Audio Features — Yang Harus Di-Ekstrak

### Low-level (librosa)
```python
mfcc          = librosa.feature.mfcc()           # Timbre (paling penting!)
chroma        = librosa.feature.chroma_stft()     # Harmonic content
spectral_contrast = librosa.feature.spectral_contrast()  # Texture
tonnetz       = librosa.feature.tonnetz()         # Tonal centroid
tempo, beats  = librosa.beat.beat_track()         # Rhythm
spectral_centroid = ...                           # Brightness
spectral_rolloff  = ...                           # Frequency spread
zero_crossing_rate = ...                          # Noisiness
rms           = librosa.feature.rms()             # Energy
```

### High-level (Spotify-style)
```
danceability    : 0.0 - 1.0
energy          : 0.0 - 1.0
valence         : 0.0 - 1.0  (positiveness)
acousticness    : 0.0 - 1.0
instrumentalness: 0.0 - 1.0
liveness        : 0.0 - 1.0
speechiness     : 0.0 - 1.0
mode            : major/minor
key             : C, C#, D, ...
tempo           : BPM
loudness        : dB
```

### Deep Embeddings (CLAP)
```
audio_embedding : 512-dim vector
text_embedding  : 512-dim vector
```
CLAP memproyeksikan audio dan text ke shared embedding space. Dua lagu yang mirip secara akustik → cosine similarity tinggi.

## 6. Pipeline End-to-End

### Training (one-time, build index)
```
1. Scrape 100K+ songs (MTG-Jamendo + FMA + Spotify)
2. Extract features per song (librosa + CLAP)
3. Store: {song_id, metadata, feature_vector, embedding}
4. Build FAISS index from all feature vectors
5. Store index to disk
```

### Inference (real-time per user)
```
1. User submits favorite song (link or file)
2. Extract feature vector from that song
3. FAISS search: find top-50 nearest neighbors
4. Re-rank by: similarity + emotion match + diversity
5. Return curated playlist
6. Optional: user feedback → fine-tune weights
```

## 7. Kenapa Ini Berbeda dari Spotify/Pandora

| Feature | Spotify | Pandora | PsychoAcoustic Engine |
|---|---|---|---|
| Basis Rekomendasi | Collaborative filtering (what others listen to) | Music Genome Project (human annotation) | **Audio fingerprint similarity** |
| Cold-start problem | Yes (new songs need listens) | No | **No** (works purely on audio) |
| Personalization | What you + similar users listen to | Genre/tags | **What YOUR ears like acoustically** |
| Emotion-aware | Valence tag only | Limited | **Full VA + mood recognition** |
| ADHD/Bipolar use case | Not designed | Not designed | **Designed for emotional regulation** |
| Dopamine optimization | No | No | **Yes — familiar pattern matching** |

## 8. Research Papers — Priority Reading

| Paper | Key Takeaway |
|---|---|
| Salimpoor et al. 2011 *Nature Neuro* | Dopamine release during music peak emotion |
| Koelsch 2014 *Nat Rev Neurosci* | Brain correlates of music-evoked emotions |
| Bogdanov et al. 2019 *ISMIR* | MTG-Jamendo dataset |
| Wu et al. 2022 *CLAP* | Contrastive Language-Audio Pretraining |
| Kang & Herremans 2025 *Music2Emo* | Unified music emotion recognition |
| Nature Sci Rep 2025 *Entrainment* | Neural entrainment → emotion linkage |
| RecSys 2021 *Siamese NN* | Content-based music recommendation |

## 9. Development Roadmap

### Phase 1 — Core Engine (2-3 weeks)
- [x] Feature extraction pipeline (librosa)
- [ ] FAISS similarity index
- [ ] CLAP embedding integration
- [ ] Basic recommendation from file input

### Phase 2 — Emotion Layer (1-2 weeks)
- [ ] Music2Emo integration
- [ ] Emotion profile matching
- [ ] Valence/arousal filtering

### Phase 3 — Dataset (2-3 weeks)
- [ ] Scrape MTG-Jamendo (55K songs)
- [ ] Scrape FMA (100K songs)
- [ ] Index all with FAISS
- [ ] Spotify API integration for metadata

### Phase 4 — App (2-3 weeks)
- [ ] FastAPI backend
- [ ] React/Electron frontend
- [ ] User authentication
- [ ] Feedback loop
- [ ] EEG integration (optional)

## 10. Your Personal Study (ADHD + Bipolar)

Kita bisa gunakan dirimu sebagai **N=1 case study**:

1. Kumpulkan 20-50 lagu favoritmu yang "work" untuk mood stabilization
2. Ekstrak fingerprint → cari pola umum
3. Temukan lagu baru dengan fingerprint yang sama
4. Test: apakah lagu baru itu memberikan efek emosional yang sama?
5. Iterasi: refine feature weights based on your feedback

Ini bisa menjadi prototype untuk jutaan orang dengan kondisi serupa.
