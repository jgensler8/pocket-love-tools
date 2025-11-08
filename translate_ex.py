import json
import argparse
import logging
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from gameboy_translator import decode_gameboy_text

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def translate_text_to_english(text_list: list[str], model, tokenizer) -> list[str]:
    """
    Translates a batch of Japanese strings to English using the Liquid AI model.
    This logic is adapted from your translate_test.py script.

    Args:
        text_list (list[str]): A list of Japanese strings to translate.
        model: The pre-loaded model.
        tokenizer: The pre-loaded tokenizer.

    Returns:
        list[str]: The list of translated English strings.
    """
    if not text_list:
        return []

    translated_texts = []
    for text in text_list:
        chat = [
            {"role": "system", "content": "Translate to English."},
            {"role": "user", "content": text}
        ]
        prompt = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(prompt, return_tensors="pt", padding=True).to(model.device)

        outputs = model.generate(**inputs, max_new_tokens=256, pad_token_id=tokenizer.eos_token_id)
        input_length = inputs.input_ids.shape[1]
        generated_tokens = outputs[0][input_length:]
        translated_text = tokenizer.decode(generated_tokens, skip_special_tokens=True)
        translated_texts.append(translated_text)

    return translated_texts


def main():
    parser = argparse.ArgumentParser(description="Batch translate scenes from a JSON file.")
    parser.add_argument("input_json", help="Path to the input JSON file from extract_scene_rom.py.")
    parser.add_argument("output_json", help="Path to save the translated output JSON file.")
    parser.add_argument("--start_scene", help="number of scenes to limit", type=int, default=0)
    parser.add_argument("--end_scene", help="number of scenes to limit", type=int, default=1)
    args = parser.parse_args()

    logging.info(f"Loading input JSON file: {args.input_json}")
    with open(args.input_json, 'r', encoding='utf-8') as f:
        data = json.loads(f.read())

    logging.info("Loading translation model (LiquidAI)... This may take a moment.")
    model_name = "LiquidAI/LFM2-350M-ENJP-MT"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.bfloat16, device_map="auto")

    # 1. Decode all scenes and phrases to Japanese
    logging.info("Decoding game scenes and phrases into Japanese...")
    decoded_scenes_ja = [decode_gameboy_text(scene) for scene in data['scenes']]

    logging.info(decoded_scenes_ja)
    limit_scenes = decoded_scenes_ja[args.start_scene:(args.end_scene + 1)]

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