import json
import argparse
import logging
from gameboy_translator import decode_gameboy_text

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

def replace_scene_text(bank: int, scene_num: int, scene_text: str, pointer_hex: str) -> str:
    waits = 0
    wait_text = ""
    for i, c in enumerate(scene_text):
        if c not in ["0x80", "0x82", "0x81"]:
            pass
        elif c == "0x80":
            wait_text += "\n"
            if i < len(scene_text):
                wait_text += "..."
        elif c == "0x82":
            wait_text += "@"
            waits += 1
        elif c == "0x81":
            wait_text += "#"
    # return f" B{bank} S{scene_num}\nA{pointer_hex} w={waits}{wait_text}"
    return f" B{bank} S{scene_num} w={waits}{wait_text}"
    

def main():
    parser = argparse.ArgumentParser(
        description="Generate a template translation JSON for scene patching."
    )
    parser.add_argument(
        "input_json", help="Path to the input JSON file from extract_scene_rom.py."
    )
    parser.add_argument(
        "output_json", help="Path to save the template output JSON file."
    )
    parser.add_argument(
        "--bank",
        type=int,
        required=True,
        help="The ROM bank number for which the template is generated."
    )
    args = parser.parse_args()

    logging.info(f"Loading input JSON file: {args.input_json}")
    with open(args.input_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    header_pointers = data.get("header", [])
    scenes = data.get("scenes", [])

    # 1. Generate template scenes
    logging.info("Generating template scenes...")
    template_scenes = []
    for i, pointer_hex in enumerate(header_pointers):
        scene_text = scenes[i]
        template_text = replace_scene_text(args.bank, i, scene_text, pointer_hex)
        template_scenes.append({"japanese": decode_gameboy_text(scene_text), "english": template_text})

    output_data = {"translated_scenes": template_scenes}

    # 2. Save the output to a new JSON file
    logging.info(f"Saving template data to {args.output_json}...")
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    logging.info("Template generation complete!")

if __name__ == "__main__":
    main()