import json
import argparse
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


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
        template_text = f" B{args.bank}\n S{i}\n A{pointer_hex}\n"
        scene_text = scenes[i]
        # logging.info(scene_text)
        if len(scene_text) >= 2 and scene_text[-2] == '0x82' and scene_text[-1] == '0x81':
            template_text += "@#"
        template_scenes.append({"japanese": "", "english": template_text})

    output_data = {"translated_scenes": template_scenes}

    # 2. Save the output to a new JSON file
    logging.info(f"Saving template data to {args.output_json}...")
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    logging.info("Template generation complete!")

if __name__ == "__main__":
    main()