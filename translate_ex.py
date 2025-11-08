import json
import argparse
import logging
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast

# Import the character map and phrase dictionary from your existing files
from dictionary_katakana import character_map
from phrases import phrases

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def decode_gameboy_text(rom_data: list[int]) -> str:
    """
    Decodes a list of byte values from a game scene into a Japanese string.
    This function is adapted from your translate_rom_text script but works on a list of bytes
    instead of reading directly from a ROM file.

    Args:
        rom_data (list[int]): A list of byte values representing a scene.

    Returns:
        str: The decoded Japanese text.
    """
    japanese_text = []
    i = 0
    while i < len(rom_data):
        byte = rom_data[i]

        if byte == 0x00:
            # The extractor script already splits scenes by the 0x00 terminator
            pass
        elif byte == 0x80:  # Newline character
            japanese_text.append("\n")
        elif byte == 0xFF:  # Phrase dictionary compression
            i += 1  # Move to the next byte for the phrase index
            if i < len(rom_data):
                phrase_index = rom_data[i]
                if phrase_index < len(phrases):
                    phrase_bytes = phrases[phrase_index]
                    for phrase_byte in phrase_bytes:
                        char = character_map.get(phrase_byte, f"[?{phrase_byte:02X}]")
                        japanese_text.append(char)
                else:
                    japanese_text.append(f"[?PHRASE_{phrase_index:02X}]")
        else:
            # Look up the character in the map
            char = character_map.get(byte, f"[?{byte:02X}]")
            japanese_text.append(char)

        i += 1

    return "".join(japanese_text)


def translate_text_to_english(text_list: list[str], model, tokenizer) -> list[str]:
    """
    Translates a batch of Japanese strings to English using the mBART model.
    This logic is adapted from your translate_test.py script.

    Args:
        text_list (list[str]): A list of Japanese strings to translate.
        model: The pre-loaded mBART model.
        tokenizer: The pre-loaded mBART tokenizer.

    Returns:
        list[str]: The list of translated English strings.
    """
    if not text_list:
        return []
    
    # The tokenizer needs to know the source language. For Japanese, it's "ja_XX".
    tokenizer.src_lang = "ja_XX"

    # Encode the Japanese text to get input tensors for the model.
    encoded_ja = tokenizer(
        text_list,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=model.config.max_position_embeddings
    )

    # Generate the translation, forcing the output to start with the English token.
    generated_tokens = model.generate(
        **encoded_ja,
        forced_bos_token_id=tokenizer.lang_code_to_id["en_XX"]
    )

    # Decode the generated tokens to get the translated text.
    return tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)


def main():
    parser = argparse.ArgumentParser(description="Batch translate scenes from a JSON file.")
    parser.add_argument("input_json", help="Path to the input JSON file from extract_scene_rom.py.")
    parser.add_argument("output_json", help="Path to save the translated output JSON file.")
    parser.add_argument("--limit_scenes", help="number of scenes to limit", type=int, default=1)
    args = parser.parse_args()

    logging.info(f"Loading input JSON file: {args.input_json}")
    with open(args.input_json, 'r', encoding='utf-8') as f:
        data = json.loads(f.read())

    logging.info("Loading translation model (mBART)... This may take a moment.")
    model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")
    tokenizer = MBart50TokenizerFast.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")

    # 1. Decode all scenes and phrases to Japanese
    logging.info("Decoding game scenes and phrases into Japanese...")
    decoded_scenes_ja = [decode_gameboy_text(scene) for scene in data['scenes']]

    logging.info(decoded_scenes_ja)
    limit_scenes = decoded_scenes_ja[:args.limit_scenes]

    # 2. Batch translate all Japanese text to English
    logging.info(f"Translating {len(limit_scenes)} scenes to English...")
    translated_scenes_en = translate_text_to_english(limit_scenes, model, tokenizer)

    # 3. Prepare the final output data
    output_data = {
        "header": data["header"],
        "translated_scenes": {
            str(i): {'japanese': ja, 'english': en}
            for i, (ja, en) in enumerate(zip(limit_scenes, translated_scenes_en))
        }
    }

    # 4. Save the output to a new JSON file
    logging.info(f"Saving translated data to {args.output_json}...")
    with open(args.output_json, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    logging.info("Batch translation complete!")

if __name__ == "__main__":
    main()