import json
import argparse
import logging
import os
import sys

# Add current directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from patch import encode_english_text
except ImportError:
    logging.error("Could not import encode_english_text from patch.py.")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(message)s")

# ROM Bank boundaries
# Available space is from 0x4000 up to 0x7999 (inclusive)
BANK_START = 0x4000
BANK_LIMIT_ADDR = 0x7999
AVAILABLE_SIZE = BANK_LIMIT_ADDR - BANK_START

def main():
    parser = argparse.ArgumentParser(description="Analyze scene lengths and ROM space usage.")
    parser.add_argument("input_json", help="Path to the translated JSON file.")
    args = parser.parse_args()

    if not os.path.exists(args.input_json):
        logging.error(f"File not found: {args.input_json}")
        return

    try:
        with open(args.input_json, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON: {e}")
        return

    scenes = data.get("translated_scenes", [])
    if not scenes:
        logging.warning("No scenes found in JSON.")
        return

    # Header is 2 bytes per scene
    header_size = len(scenes) * 2
    
    scene_infos = []
    total_text_size = 0

    for i, scene in enumerate(scenes):
        english_text = scene.get("english", "")
        # Calculate encoded length + null terminator
        encoded_bytes = encode_english_text(english_text)
        length = len(encoded_bytes) + 1
        
        snippet = english_text.replace("\n", "\\n")
        if len(snippet) > 40:
            snippet = snippet[:37] + "..."

        scene_infos.append({
            "index": i,
            "length": length,
            "text_snippet": snippet
        })
        total_text_size += length

    total_required = header_size + total_text_size
    remaining_space = AVAILABLE_SIZE - total_required

    print(f"--- Summary ---")
    print(f"Total Scenes:    {len(scenes)}")
    print(f"Header Size:     {header_size} bytes")
    print(f"Total Text Size: {total_text_size} bytes")
    print(f"Total Required:  {total_required} bytes")
    print(f"Available Space: {AVAILABLE_SIZE} bytes (0x4000 - 0x7999)")
    print(f"Space Remaining: {remaining_space} bytes")
    
    if remaining_space < 0:
        print(f"STATUS: OVERFLOW by {abs(remaining_space)} bytes")
    else:
        print(f"STATUS: FITS with {remaining_space} bytes to spare")

    # print("\n--- Scenes Sorted by Length (Longest First) ---")
    sorted_scenes = sorted(scene_infos, key=lambda x: x["length"], reverse=True)
    
    # print(f"{'Idx':<5} | {'Len':<5} | {'Text'}")
    # print("-" * 60)
    # for info in sorted_scenes:
    #     print(f"{info['index']:<5} | {info['length']:<5} | {info['text_snippet']}")

    print("\n--- Sequential Fit Analysis (Original Order) ---")
    current_size = header_size
    fit_count = 0
    overflow_index = -1
    
    for info in scene_infos:
        if current_size + info["length"] > AVAILABLE_SIZE:
            overflow_index = info["index"]
            break
        current_size += info["length"]
        fit_count += 1
    
    print(f"Scenes that fit: {fit_count} / {len(scenes)}")
    if fit_count < len(scenes):
        print(f"First scene to overflow: Index {overflow_index}")
        print(f"Scenes needing to move: {len(scenes) - fit_count}")
    else:
        print("All scenes fit.")

    if remaining_space < 0:
        print("\n--- Optimization Suggestion ---")
        bytes_needed = abs(remaining_space)
        saved = 0
        candidates = []
        for info in sorted_scenes:
            saved += info["length"]
            candidates.append(info["index"])
            if saved >= bytes_needed:
                break
        
        print(f"To resolve overflow, consider moving the top {len(candidates)} longest scenes:")
        print(f"Indices: {sorted(candidates)}")
        print(f"Bytes saved: {saved} (Need: {bytes_needed})")

if __name__ == "__main__":
    main()
