import os
from dotenv import load_dotenv

from src.prompts.prompts_generation import PromptGeneratorService
from src.tts.tts_service import TTSService
from src.processing.audio_processing import AudioProcessor
from src.processing.qualitychecker import QualityChecker
from src.processing.datasetexporter import DatasetExporter

def main():

    load_dotenv()

    num_samples = int(os.getenv("NUM_SAMPLES", 10))

    print("🚀 Starting pipeline...")

    # init services
    prompt_service = PromptGeneratorService(
        api_key=os.getenv("GROQ_API_KEY")
    )

    tts_service = TTSService()

    audio_processor = AudioProcessor()

    quality_checker = QualityChecker()

    exporter = DatasetExporter()

    dataset = []

    os.makedirs("data/audio", exist_ok=True)

    # 1) Generate prompts
    print("\n📝 Generating prompts...")
    prompts = prompt_service.generate_prompts(num_samples)

    print(f"Generated {len(prompts)} prompts")

    # 2) Process each sample
    for i, text in enumerate(prompts):

        print(f"\n🎧 Processing sample {i}")

        # validate text
        if not quality_checker.validate_text(text):
            print("❌ Invalid text, skipped")
            continue

        # TTS
        mp3_path = tts_service.text_to_speech(
            text,
            f"sample_{i}.mp3"
        )

        # Audio processing
        wav_path = audio_processor.process_audio(
            mp3_path,
            f"data/audio/sample_{i}.wav"
        )

        # Quality check
        result = quality_checker.validate_audio(wav_path)

        if not result["valid"]:
            print("❌ Bad audio, skipped")
            continue

        # save record
        dataset.append({
            "id": f"eg_{i}",
            "text": text,
            "audio_path": wav_path,
            "duration": result["duration"],
            "quality_score": result["quality_score"],
            "issues": result["issues"]
        })

        print("✅ Added to dataset")

    # 3) Export dataset
    print("\n📦 Exporting dataset...")

    exporter.export_jsonl(dataset)

    print(f"🎉 Done! Saved {len(dataset)} samples")


if __name__ == "__main__":
    main()