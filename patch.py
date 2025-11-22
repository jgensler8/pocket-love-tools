import json
import argparse
import logging
from typing import List, Tuple
import png

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

BANK_SIZE = 0x4000  # 16KB for Game Boy ROMs

# --- English to Game Boy Byte Mapping ---
# This map needs to be carefully constructed based on the game's actual font tiles.
# For now, it's a best-effort attempt using existing known mappings and placeholders.
# You will need to verify and expand this map based on your ROM's font data.
# Placeholder values (e.g., 0x81, 0xA1) are arbitrary and will likely display
# incorrect characters if not mapped to actual font tiles in your ROM.
ENGLISH_TO_GAMEBOY_MAP = {
    " ": 0x7F,  # Space (from dictionary_katakana.py 0x7E, 0x7F, 0x80 are spaces)
    "0": 0x6F,
    "1": 0x70,
    "2": 0x71,
    "3": 0x72,
    "4": 0x73,
    "5": 0x74,
    "6": 0x75,
    "7": 0x76,
    "8": 0x77,
    "9": 0x78,
    "\n": 0x80,  # Newline control code (from gameboy_translator.py)
    # TODO: these are placeholders for theoretical control chars
    "@": 0x82,
    "#": 0x81,
    "!": 0x6A,
    "?": 0x6B,
    "<3": 0x69,  # Heart symbol
    "day": 0x79,  # Special word
    "~": 0x7A,
    "-": 0x7B,
    ".": 0x7C,
    "/": 0x7D,
    "=": 0x6E,
    "(": 0x65,
    ")": 0x66,
    ",": 0x37,  # Using Japanese comma for now
    ":": 0x01,  # Placeholder
    ";": 0x02,  # Placeholder
    "'": 0x03,  # Placeholder
    '"': 0x04,  # Placeholder
}

# Programmatically add A-Z and a-z
start_char_code = 0x09
for i in range(26):
    # Uppercase A-Z
    ENGLISH_TO_GAMEBOY_MAP[chr(ord("A") + i)] = start_char_code + i
    # Lowercase a-z
    ENGLISH_TO_GAMEBOY_MAP[chr(ord("a") + i)] = start_char_code + 26 + i


def encode_english_text(text: str) -> bytes:
    """
    Encodes an English string into Game Boy compatible bytes using a predefined map.
    Handles multi-character symbols like '<3' and replaces unknown characters with space.
    """
    encoded_bytes = bytearray()
    i = 0
    while i < len(text):
        found_multi = False
        # Check for multi-character symbols first (e.g., '<3', 'day')
        # Iterate over items to check for longest matches first
        for symbol in sorted(ENGLISH_TO_GAMEBOY_MAP.keys(), key=len, reverse=True):
            if len(symbol) > 1 and text.startswith(symbol, i):
                encoded_bytes.append(ENGLISH_TO_GAMEBOY_MAP[symbol])
                i += len(symbol)
                found_multi = True
                break
        if found_multi:
            continue

        char = text[i]
        byte_code = ENGLISH_TO_GAMEBOY_MAP.get(char)
        if byte_code is not None:
            encoded_bytes.append(byte_code)
        else:
            logging.warning(
                f"Unknown English character '{char}' (ord={ord(char)}) encountered. Replacing with space."
            )
            encoded_bytes.append(
                ENGLISH_TO_GAMEBOY_MAP[" "]
            )  # Replace unknown with space
        i += 1
    return bytes(encoded_bytes)


def rebuild_rom_headers(
    output_rom_path,
    extracted_json_path,
    translated_json_path,
    character_limit,
    bank_num,
):
    """
    Rebuilds ROM headers and replaces scene text based on translated JSON data.
    Enforces a character limit per scene, truncating and warning when exceeded.
    Relocates translated text to a new area and updates header pointers.

    Args:
        output_rom_path (str): Path to the output ROM file.
        extracted_json_path (str): Path to the JSON file containing original ROM structure info.
        translated_json_path (str): Path to the JSON file containing translated scenes.
        character_limit (int): Maximum number of characters allowed per scene.
        bank_num (int): The ROM bank number where the text and header reside.
                                      E.g., "0x7000". This must be a safe, unused area in the ROM.
    """
    logging.info(
        f"patching bank {bank_num}, ex:{extracted_json_path} tr:{translated_json_path}"
    )
    try:
        with open(translated_json_path, "r", encoding="utf-8") as f:
            translated_data = json.load(f)

        with open(extracted_json_path, "r", encoding="utf-8") as f:
            extracted_data = json.load(f)

        translated_scenes = translated_data["translated_scenes"]

        # rom addressesing works the same across all banks
        bank_start_addr = 0x4000
        # Calculate file offset for the header
        header_file_offset = bank_num * BANK_SIZE
        header_bytes_len = len(extracted_data["header"]) * 2
        scene_file_offset = header_file_offset + header_bytes_len

        # --- Process translated scenes and generate new text block ---
        new_text_rom_bytes = bytearray()
        new_scene_cpu_addresses = []

        relative_scene_start_address = bank_start_addr + header_bytes_len
        current_new_text_cpu_address = relative_scene_start_address

        for i, scene_data in enumerate(translated_scenes):
            japanese_text = scene_data["japanese"]
            english_text = scene_data["english"]

            # TODO either factor in the control codes // warn about the translation
            # if len(english_text) > len(japanese_text):
            #     english_text = english_text[: len(japanese_text)]

            if len(english_text) > character_limit:
                logging.warning(
                    f"Scene {i} exceeds character limit ({character_limit}). need {len(english_text)}. Truncating."
                )
                english_text = english_text[:character_limit]
                # Update the scene data in memory, though it won't be saved back to JSON
                translated_scenes[i]["english"] = english_text

            encoded_scene_bytes = encode_english_text(english_text)
            encoded_scene_bytes += b"\x00"  # Add null terminator

            # logging.info(f"{i}: {hex(current_new_text_cpu_address)}")
            new_text_rom_bytes.extend(encoded_scene_bytes)
            new_scene_cpu_addresses.append(current_new_text_cpu_address)
            current_new_text_cpu_address += len(encoded_scene_bytes)

        if current_new_text_cpu_address > 0x7999:
            logging.warning(
                f"ROM TRANSLATION EXTENDS PAST ROM BANK: {current_new_text_cpu_address} by {current_new_text_cpu_address - 0x7999}"
            )

        logging.info(
            f"calculated header scenes:{len(translated_scenes)} ending:{current_new_text_cpu_address}"
        )

        # --- Rebuild Header ---
        new_header_bytes = bytearray()
        for new_cpu_address in new_scene_cpu_addresses:
            low_byte = new_cpu_address & 0xFF
            # Assuming the 0x40 offset for high byte as seen in extract_scene_rom.py
            high_byte_stored = (new_cpu_address >> 8) - 0x40
            # print(f"{hex(new_cpu_address)} {hex(low_byte)} {hex(high_byte_stored)}")
            new_header_bytes.append(low_byte)
            new_header_bytes.append(high_byte_stored)

        # logging.info("rebuilt header")

        # --- Write to ROM ---
        with open(output_rom_path, "r+b") as rom_file:
            # Write new header
            rom_file.seek(header_file_offset)
            rom_file.write(new_header_bytes)
            logging.info(f"header: {hex(header_file_offset)}")

            # Write new translated text block
            rom_file.seek(scene_file_offset)
            rom_file.write(new_text_rom_bytes)
            logging.info(
                f"scenes: {hex(scene_file_offset)} end: {hex(scene_file_offset + len(new_text_rom_bytes))}"
            )

        # logging.info("done")

    except FileNotFoundError as e:
        logging.error(f"File not found: {e}.")
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON format in one of the input files: {e}.")
    except KeyError as e:
        logging.error(
            f"Missing expected key in JSON data: {e}. Please ensure extracted_json contains 'bank_num', 'header_start_address', and 'header'."
        )
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


def patch_alphabet_tiles(output_rom: str, alphabet_png: str):
    alphabet_addr = 0xA742
    font_glyphs = 26

    # png2asset
    reader = png.Reader(filename=alphabet_png)
    width, height, pixels, metadata = reader.read()
    tiles = [[] for _ in range(font_glyphs)]

    # create tiles
    for y, row in enumerate(pixels):
        for x, pixel in enumerate(row):
            # row_i = i % width
            tile = int(x / 8) % font_glyphs
            tiles[tile].append(pixel)

    # encode bytes
    # for example see: https://gbdev.io/pandocs/Tile_Data.html
    all_bytes = bytearray()
    for i, tile in enumerate(tiles):
        logging.debug("----")
        for y in range(8):
            row = tile[y * 8 : y * 8 + 8]
            logging.debug(f"{i}: {row}")
            byte_low = [p & 0x1 and 1 for p in row[0:8]]
            # logging.info(f"{byte_low}")
            b0 = sum(
                [p and pow(2, place) for place, p in enumerate(reversed(byte_low[0:4]))]
            )
            b1 = sum(
                [p and pow(2, place) for place, p in enumerate(reversed(byte_low[4:8]))]
            )
            byte_high = [p & 0x2 and 1 for p in row[0:8]]
            # logging.info(f"{byte_high}")
            b2 = sum(
                [
                    p and pow(2, place)
                    for place, p in enumerate(reversed(byte_high[0:4]))
                ]
            )
            b3 = sum(
                [
                    p and pow(2, place)
                    for place, p in enumerate(reversed(byte_high[4:8]))
                ]
            )
            # logging.info(f"{[b0, b1, b2, b3]}")
            all_bytes.append(b0 << 4 | b1)
            all_bytes.append(b2 << 4 | b3)

    with open(output_rom, "r+b") as f:
        f.seek(alphabet_addr)
        # upper case
        f.write(all_bytes)
        # TODO lower case
        f.write(all_bytes)

    logging.info("replaced alphabet")


def patch_inplace(output_rom: str, bank: int, hex_addr: str, hex_value: str):
    with open(output_rom, "r+b") as f:
        absolute_offset = bank * BANK_SIZE + (int(hex_addr, 16) - BANK_SIZE)
        logging.info(f"patching absolute offset: {hex(absolute_offset)}")
        f.seek(absolute_offset)
        f.write(bytes.fromhex(hex_value))


def main():
    main_parser = argparse.ArgumentParser(
        description="Rebuild ROM headers from JSON, enforce character limits, and replace text."
    )
    main_parser.add_argument("output_rom", help="Path to the output ROM file.")
    subparsers = main_parser.add_subparsers(dest="command", help="Sub-command help")

    # Subcommand: dialog
    dialog_parser = subparsers.add_parser("dialog", help="Patch dialog text in ROM")
    # dialog_parser.add_argument("output_rom", help="Path to the output ROM file.")
    dialog_parser.add_argument(
        "extracted_json",
        help="Path to the extracted JSON file (from extract_scene_rom.py).",
    )
    dialog_parser.add_argument(
        "translated_json",
        help="Path to the translated input JSON file (from translate_ex.py).",
    )
    dialog_parser.add_argument(
        "--character_limit",
        type=int,
        # maybe as high as 18, maybe as many rows as 5
        default=17 * 4,
        help="Maximum characters per scene (default: 17*4=68).",
    )
    dialog_parser.add_argument(
        "--bank",
        type=int,
        required=True,
        help="The ROM bank number where the text and header reside.",
    )

    # Subcommand: alphabet (example - you'll need to implement this)
    alphabet_parser = subparsers.add_parser(
        "alphabet", help="Patch alphabet tiles in ROM"
    )
    alphabet_parser.add_argument(
        "--alphabet_png", type=str, required=True, help="Path to alphabet data file."
    )

    # Subcommand: inplace
    inplace_parser = subparsers.add_parser("inplace", help="patch a single byte")
    inplace_parser.add_argument(
        "--bank",
        type=int,
        required=True,
        help="The ROM bank number to address",
    )
    inplace_parser.add_argument(
        "--hex_addr",
        type=str,
        required=True,
        help="realtive memory address if bank was switched too. 0x4??? will be translated into absoluate rom addr.",
    )
    inplace_parser.add_argument(
        "--hex_value",
        type=str,
        required=True,
        help="hex",
    )

    args = main_parser.parse_args()

    if args.command == "dialog":
        rebuild_rom_headers(
            args.output_rom,
            args.extracted_json,
            args.translated_json,
            args.character_limit,
            args.bank,
        )
    elif args.command == "alphabet":
        patch_alphabet_tiles(args.output_rom, args.alphabet_png)
    elif args.command == "inplace":
        patch_inplace(
            args.output_rom,
            args.bank,
            args.hex_addr,
            args.hex_value,
        )


if __name__ == "__main__":
    main()
