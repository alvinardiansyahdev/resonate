# Resonate

**Music that meets you where you are — and gently takes you where you want to be.**

Resonate is a content-based music curation engine that maps your emotional state to a gradual sonic trajectory. Instead of generic "healing music" that lacks dopamine, it analyzes the acoustic fingerprint of songs you already love and finds music that fits both your taste *and* your emotional journey.

## The Problem

People (especially with ADHD, bipolar, anxiety, or depression) instinctively reach for familiar music for emotional regulation — songs they *know* will work. Generic recommendations (classical, AI-generated, "therapy playlists") fail because they trigger neither the dopamine reward system nor the predictive coding patterns the brain has already built.

## The Solution

```
                ┌─ "I feel sad"
                ▼
┌──────────────────────────────┐
│  MOOD TRAJECTORY ENGINE      │
│                              │
│  sad → sadder → warm →       │
│  neutral → light → happy     │
│         (9 sigmoid steps)    │
└──────────┬───────────────────┘
           ▼
┌──────────────────────────────┐
│  AUDIO FINGERPRINT MATCHER   │
│                              │
│  Your favorite song ──→      │
│  93-dim feature vector       │
│         +                    │
│  512-dim CLAP embedding      │
│         =                    │
│  FAISS similarity search     │
│  across 100K+ songs          │
└──────────┬───────────────────┘
           ▼
┌──────────────────────────────┐
│  DUAL-SCORE RE-RANKING       │
│                              │
│  Score = 0.6×acoustic_match  │
│        + 0.4×emotion_match   │
│                              │
│  → Songs that sound LIKE     │
│    your favorites AND match  │
│    the target emotional step │
└──────────────────────────────┘
```

## Architecture

```
resonate/
├── src/
│   ├── feature_extractor.py    # librosa-based audio analysis (93-dim)
│   ├── emotion_analyzer.py     # Valence/Arousal prediction (rule-based + Music2Emo)
│   ├── embedding_engine.py     # CLAP deep audio embeddings (512-dim)
│   ├── similarity.py           # FAISS billion-scale nearest neighbor search
│   ├── curator.py              # Orchestrator: re-rank by similarity + emotion
│   ├── mood_trajectory.py      # Sigmoid path generator, step-based curation
│   ├── mood_router.py          # Interactive mood → trajectory selection
│   ├── dataset_manager.py      # Load MTG-Jamendo, FMA, Spotify datasets
│   └── run.py                  # CLI interface
├── ARCHITECTURE.md             # Full research & architecture document
└── requirements.txt
```

## Pre-built Trajectories

| Trajectory | Path | For |
|---|---|---|
| `sad_to_happy` | (0.2V,0.2A) → (0.75V,0.6A) | Gentle lift from sadness |
| `angry_to_happy` | (0.2V,0.8A) → (0.75V,0.6A) | Release anger, find calm, then happy |
| `anxious_to_calm` | (0.3V,0.7A) → (0.6V,0.25A) | Slow down and find peace |
| `tired_to_focused` | (0.35V,0.15A) → (0.5V,0.6A) | Wake up gently |
| `neutral_to_happy` | (0.5V,0.5A) → (0.75V,0.6A) | Simple lift |

## Quick Start

```bash
# Setup
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Analyze a single song
python -m src.run analyze --audio path/to/song.mp3

# Interactive mood router
python -c "from src.mood_router import run_interactive; run_interactive()"
```

## How It Works

1. **You tell it how you feel** — sad, angry, anxious, tired, neutral
2. **You optionally pick a favorite song** — it extracts the acoustic fingerprint (MFCCs, tempo, chroma, tonnetz, spectral contrast, deep CLAP embeddings)
3. **It generates a trajectory** — a smooth sigmoid curve through valence/arousal space, with organic wobble
4. **For each step** — it searches a FAISS index for songs that match both the emotional target and your acoustic profile
5. **You get a sequenced playlist** — each song gently nudges your emotional state toward the target, without feeling forced

## Technical Stack

- **Audio Analysis**: librosa, essentia, CLAP (LAION)
- **Emotion Model**: Music2Emo (AMAAI Lab, 2025) / rule-based
- **Similarity Search**: FAISS (Facebook AI)
- **Datasets**: MTG-Jamendo (55K), FMA (100K), Spotify API
- **Backend**: Python, FastAPI

## Research

Resonate is grounded in neuroscience research on:
- **Salimpoor et al. (2011)** — Dopamine release during music-evoked pleasure (*Nature Neuroscience*)
- **Koelsch (2014)** — Brain correlates of music-evoked emotions (*Nature Reviews Neuroscience*)
- **Wu et al. (2022)** — Contrastive Language-Audio Pretraining (CLAP)
- **Kang & Herremans (2025)** — Music2Emo: unified music emotion recognition
- **Nature Sci Rep (2025)** — Neural entrainment and subjective emotion

## License

MIT
