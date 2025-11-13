import json
import argparse
import logging
from gameboy_translator import decode_gameboy_text, character_map
from liquid_translator import LiquidAITranslator
from google_cloud_translator import GoogleCloudTranslator

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    parser = argparse.ArgumentParser(
        description="Batch translate scenes from a JSON file."
    )
    parser.add_argument(
        "input_json", help="Path to the input JSON file from extract_scene_rom.py."
    )
    parser.add_argument(
        "output_json", help="Path to save the translated output JSON file."
    )
    parser.add_argument(
        "--start_scene", help="number of scenes to limit", type=int, default=0
    )
    parser.add_argument(
        "--end_scene", help="number of scenes to limit", type=int, default=1
    )
    args = parser.parse_args()

    logging.info(f"Loading input JSON file: {args.input_json}")
    with open(args.input_json, "r", encoding="utf-8") as f:
        data = json.loads(f.read())

    # translator = GoogleCloudTranslator(project_id="matching-game-fb")
    translator = LiquidAITranslator()

    # 1. Decode all scenes and phrases to Japanese
    logging.info("Decoding game scenes and phrases into Japanese...")
    decoded_scenes_ja = [decode_gameboy_text(scene) for scene in data["scenes"]]

    logging.info(decoded_scenes_ja)
    scenes_to_translate = decoded_scenes_ja[args.start_scene : (args.end_scene + 1)]

    # 2. Batch translate all Japanese text to English
    logging.info(f"Translating {len(scenes_to_translate)} scenes to English...")
    translated_scenes_en = translator.translate_batch(scenes_to_translate)

    # 3. Prepare the final output data
    output_data = {
        "translated_scenes": [
            {"japanese": ja, "english": en}
            for (ja, en) in zip(scenes_to_translate, translated_scenes_en)
        ],
    }

    # 4. Save the output to a new JSON file
    logging.info(f"Saving translated data to {args.output_json}...")
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    logging.info("Batch translation complete!")


if __name__ == "__main__":
    main()
