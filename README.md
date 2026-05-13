# Egyptian Arabic TTS Dataset Pipeline

An automated pipeline for generating a spoken Egyptian Arabic dialect dataset — from LLM-based prompt generation, through TTS synthesis and audio processing, to a clean exportable dataset.

---

##  Overview

Egyptian Arabic (Masri) is a low-resource dialect with very limited publicly available speech data. This pipeline addresses that by synthetically generating text–audio pairs at scale using a two-model approach: a large language model to produce realistic colloquial sentences, and a multilingual TTS system to synthesize them into speech.

The output is a JSONL dataset of validated audio samples paired with their transcriptions, intended for use in ASR model fine-tuning, TTS model training, or speech research.

---

## Project Structure

```
project/
│
├── main.py                          # Entry point — orchestrates the full pipeline
├── .env                             # API keys and config (not committed to git)
├── requirements.txt                 # Python dependencies
│
├── src/
│   ├── prompts/
│   │   └── prompts_generation.py    # Generates Egyptian Arabic sentences via Groq LLM
│   ├── tts/
│   │   └── tts_service.py           # Text-to-speech via ElevenLabs
│   └── processing/
│       ├── audio_processing.py      # Loads, trims, and normalizes audio
│       ├── qualitychecker.py        # Validates text and audio quality
│       ├── datasetexporter.py       # Exports final dataset to JSONL
│       └── text_normalization.py    # Arabic text cleaning and normalization
│
├── data/
│   └── audio/
│       ├── raw/                     # Raw MP3 files from ElevenLabs
│       └── processed/               # Processed WAV files (16kHz mono)
│
└── outputs/
    └── final_dataset.jsonl          # Final exported dataset
```

---

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          main.py                                │
│                                                                 │
│  ┌──────────────────┐                                           │
│  │PromptGenerator   │  Groq API → llama-3.3-70b-versatile       │
│  │                  │  Generates N Egyptian Arabic sentences     │
│  └────────┬─────────┘                                           │
│           │  raw sentences                                      │
│           ▼                                                     │
│  ┌──────────────────┐                                           │
│  │ QualityChecker   │  validate_text() — length, type checks    │
│  │ TextNormalizer   │  strip diacritics, emojis, fix punctuation│
│  └────────┬─────────┘                                           │
│           │  clean text                                         │
│           ▼                                                     │
│  ┌──────────────────┐                                           │
│  │  TTSService      │  ElevenLabs → eleven_multilingual_v2      │
│  │                  │  Outputs MP3 to data/audio/raw/           │
│  └────────┬─────────┘                                           │
│           │  mp3 path                                           │
│           ▼                                                     │
│  ┌──────────────────┐                                           │
│  │ AudioProcessor   │  librosa: resample → 16kHz mono           │
│  │                  │  trim silence, normalize amplitude        │
│  │                  │  Outputs WAV to data/audio/processed/     │
│  └────────┬─────────┘                                           │
│           │  wav path                                           │
│           ▼                                                     │
│  ┌──────────────────┐                                           │
│  │ QualityChecker   │  validate_audio() — duration 1s–20s       │
│  │                  │  assigns quality_score                    │
│  └────────┬─────────┘                                           │
│           │  valid sample                                       │
│           ▼                                                     │
│  ┌──────────────────┐                                           │
│  │ DatasetExporter  │  Appends record to final_dataset.jsonl    │
│  └──────────────────┘                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

##  Model & Prompt-Source Choices

### LLM — `llama-3.3-70b-versatile` via Groq

**Why Llama 3.3 70B?**
A 70B model is necessary here because generating authentic Egyptian dialect — as opposed to MSA (Modern Standard Arabic) — requires strong Arabic language understanding and the ability to follow nuanced stylistic constraints simultaneously. Smaller models tend to drift into MSA or produce formal phrasing.

**Why Groq?**
Groq's inference speed allows generating hundreds of prompts in seconds. For iterative dataset building this matters more than marginal quality differences between hosting providers.

**Prompt design choices:**
The system prompt explicitly:
- Forbids MSA (Modern Standard Arabic) expressions
- Forbids Franco Arabic (Latin-script Arabic)
- Forbids English loanwords written in Latin script
- Provides positive examples of genuine Egyptian street speech
- Provides negative examples of formal Arabic to contrast against

Temperature is set to `0.4` — low enough for consistent dialect adherence, high enough to produce lexical variety across samples.

### TTS — `eleven_multilingual_v2` via ElevenLabs

**Why ElevenLabs?**
It is currently one of the few commercial TTS systems that produces natural-sounding Arabic speech, including dialectal Arabic, without heavy MSA pronunciation artifacts.

**Why `eleven_multilingual_v2`?**
The v2 multilingual model handles Arabic script better than the English-only models, and produces more natural prosody for Egyptian dialect sentences compared to v1.

**Voice choice:**
The default voice ID (`EXAVITQu4vr4xnSDxMaL`) is used as a starting point. This should be replaced with an Arabic-native voice for higher authenticity — ElevenLabs has dedicated Arabic voices that reduce accent artifacts.

---

##  Review Approach

Automated quality filtering is applied at two stages:

**Stage 1 — Text validation (before TTS):**
- Checks that the input is a non-empty string with at least 3 characters
- Runs `TextNormalizer` to strip diacritics (tashkeel), emojis, symbols, and duplicate punctuation before sending to TTS — this prevents the TTS model from mispronouncing or skipping marked-up text

**Stage 2 — Audio validation (after processing):**
- Checks audio duration is between `1.0s` and `20.0s`
- Samples outside this range are flagged and skipped
- A `quality_score` of `1.0` is assigned to samples with no issues; any sample with issues receives `0.0` and is excluded from the dataset

**What is NOT currently reviewed:**
- Dialect accuracy — there is no automated check that the generated sentence is genuinely Egyptian dialect vs. MSA drift
- Pronunciation accuracy — the TTS output is not verified against the input text via ASR
- Speaker consistency — all samples use a single voice, but prosody is not verified for consistency

---

## Output Format

Each record in `outputs/final_dataset.jsonl`:

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

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique sample identifier |
| `text` | string | Normalized Egyptian Arabic transcription |
| `audio_path` | string | Relative path to the 16kHz mono WAV file |
| `duration` | float | Audio duration in seconds |
| `quality_score` | float | `1.0` = no issues, `0.0` = failed validation |
| `issues` | list | Detected issues e.g. `["audio_too_short"]` |

Audio format: **16kHz, mono, 16-bit WAV** — compatible with Whisper, wav2vec2, and most ASR/TTS training frameworks.

---

## Observed Quality Issues

| Issue | Cause | Frequency |
|---|---|---|
| `audio_too_short` | Very short sentences (2–3 words) synthesized in under 1 second | Occasional |
| `corrupted_audio` | ElevenLabs API returns an incomplete audio stream | Rare |
| MSA drift in generated text | LLM generates formal Arabic despite prompt constraints | Occasional — more frequent at lower temperatures or with short prompts |
| Unnatural prosody | TTS model applies non-Egyptian pronunciation patterns on some words | Present — especially on loanwords |
| Tashkeel artifacts | If diacritics are not stripped, TTS reads them as separate sounds | Fixed by `TextNormalizer` before TTS |

---

## Trade-offs

**Synthetic vs. real speech:**
All audio is synthesized, not recorded. This means speaker diversity and natural background variation are absent. The dataset is suitable for bootstrapping or fine-tuning but should not replace real-speaker recordings for production-grade ASR systems.

**Single voice:**
Using one ElevenLabs voice keeps the dataset consistent but introduces speaker bias. A robust dataset should include multiple voices and genders.

**LLM-generated text:**
The LLM produces plausible Egyptian Arabic but occasionally drifts toward MSA, especially for longer or more complex sentences. There is no automated classifier to catch this — manual spot-checking is recommended.

**Speed vs. cost:**
Groq is fast and cheap for generation. ElevenLabs is the main cost driver — each API call synthesizes one sentence. At scale (1000+ samples), ElevenLabs costs become significant.

**Duration filter as quality proxy:**
The current quality check uses duration as the primary signal. This is a weak proxy — a 5-second audio file could still have poor pronunciation or TTS artifacts. A stronger approach would run ASR on the output and compare the transcript to the input text using WER (Word Error Rate).

---

## Limitations

- **No dialect verification** — the pipeline cannot confirm that generated text is genuinely Egyptian colloquial Arabic rather than MSA
- **No ASR feedback loop** — synthesized audio is not checked for pronunciation accuracy against the source text
- **Single speaker** — no speaker diversity; not suitable for speaker-independent model training without modification
- **No punctuation handling in TTS** — sentence-final punctuation like `؟` or `!` is passed to ElevenLabs but its effect on prosody is not validated
- **Sequential processing** — samples are processed one by one; no batching or parallelism, which limits throughput at scale
- **Platform dependency** — relies on two paid external APIs (Groq + ElevenLabs); any API change or rate limit directly impacts pipeline throughput

---

## Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

```env
GROQ_API_KEY=your_groq_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
NUM_SAMPLES=50
```

### 3. Run

```bash
python main.py
```

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
