# Egyptian Arabic TTS Dataset Pipeline

A pipeline for generating a high-quality Egyptian Arabic speech dataset automatically — from prompt generation using an LLM, to text-to-speech synthesis, audio processing, and final export.

---

##  Overview

This project automates the full process of building a TTS (Text-to-Speech) dataset in Egyptian Arabic dialect. It uses Groq's LLM to generate realistic Egyptian Arabic sentences, converts them to audio using ElevenLabs, processes and validates the audio, then exports a clean dataset ready for training.

---

## 🗂️ Project Structure

```
project/
│
├── main.py                  # Entry point — runs the full pipeline
├── .env                     # API keys and config (not committed to git)
├── requirements.txt         # Python dependencies
│
├── src/
│   ├── prompts/
│   │   └── prompts_generation.py    # Generates Egyptian Arabic sentences via Groq LLM
│   │
│   ├── tts/
│   │   └── tts_service.py           # Converts text to speech using ElevenLabs
│   │
│   └── processing/
│       ├── audio_processing.py      # Converts, trims, and normalizes audio
│       ├── qualitychecker.py        # Validates text and audio quality
│       ├── datasetexporter.py       # Exports final dataset to JSONL
│       └── text_normalization.py    # Cleans and normalizes Arabic text
│
├── data/
│   └── audio/
│       ├── raw/             # Raw MP3 files from ElevenLabs
│       └── processed/       # Processed WAV files (16kHz, mono, normalized)
│
└── outputs/
    └── final_dataset.jsonl  # Final exported dataset
```

---

## Pipeline Steps

```
1. Generate Prompts     →    Groq LLM (llama-3.3-70b) generates Egyptian Arabic sentences
        ↓
2. Validate Text        →    Check text is valid and not empty
        ↓
3. Normalize Text       →    Remove diacritics, emojis, duplicate punctuation
        ↓
4. Text-to-Speech       →    ElevenLabs converts text to MP3
        ↓
5. Audio Processing     →    Convert to WAV (16kHz mono), trim silence, normalize amplitude
        ↓
6. Quality Check        →    Validate duration (1–20 seconds), detect issues
        ↓
7. Export Dataset       →    Save valid samples to JSONL
```

---

## Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up environment variables

Copy `.env` and fill in your API keys:

```
GROQ_API_KEY=your_groq_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
NUM_SAMPLES=50
```

### 3. Run the pipeline

```bash
python main.py
```

---

## Output Format

Each record in `outputs/final_dataset.jsonl` looks like this:

```json
{
  "id": "eg_0",
  "text": "عامل ايه النهارده",
  "audio_path": "data/audio/processed/sample_0.wav",
  "duration": 1.84,
  "quality_score": 1.0,
  "issues": []
}
```

| Field | Description |
|---|---|
| `id` | Unique sample ID |
| `text` | Original Egyptian Arabic sentence |
| `audio_path` | Path to the processed WAV file |
| `duration` | Audio duration in seconds |
| `quality_score` | Score from 0.0 to 1.0 (1.0 = no issues) |
| `issues` | List of detected issues (empty if valid) |

---

## 🔧 Configuration

| Variable | Default | Description |
|---|---|---|
| `NUM_SAMPLES` | `10` | Number of sentences to generate |
| `MIN_DURATION` | `1.0s` | Minimum accepted audio duration |
| `MAX_DURATION` | `20.0s` | Maximum accepted audio duration |
| `SAMPLE_RATE` | `16000 Hz` | Output WAV sample rate |
| `voice_id` | `EXAVITQu4vr4xnSDxMaL` | ElevenLabs voice ID |
| `model_id` | `eleven_multilingual_v2` | ElevenLabs model |

---

## Requirements

- Python 3.8+
- [Groq API key](https://console.groq.com/)
- [ElevenLabs API key](https://elevenlabs.io/)

```
groq
elevenlabs
librosa
soundfile
numpy
python-dotenv
```

---

## Notes

- The pipeline skips any sample that fails text validation, audio quality checks, or TTS generation.
- Audio is automatically converted to **16kHz mono WAV** — the standard format for most speech/ASR model training.
- Text normalization removes diacritics (tashkeel), emojis, and non-Arabic characters before synthesis.
- The `.env` file and `data/` folder are excluded from git via `.gitignore`.
