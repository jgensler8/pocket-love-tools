import json
import argparse
import logging
from typing import List, Tuple
import png
import importlib
import sys
from dictionary_en import character_map

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

BANK_SIZE = 0x4000  # 16KB for Game Boy ROMs


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
        for symbol in sorted(character_map.keys(), key=len, reverse=True):
            if len(symbol) > 1 and text.startswith(symbol, i):
                encoded_bytes.append(character_map[symbol])
                i += len(symbol)
                found_multi = True
                break
        if found_multi:
            continue

        char = text[i]
        byte_code = character_map.get(char)
        if byte_code is not None:
            encoded_bytes.append(byte_code)
        else:
            logging.warning(
                f"Unknown English character '{char}' (ord={ord(char)}) encountered. Replacing with space."
            )
            encoded_bytes.append(character_map[" "])  # Replace unknown with space
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


def tile_png_to_bytes(file_png: str, file_tiles: int) -> bytearray:
    # png2asset
    reader = png.Reader(filename=file_png)
    width, height, pixels, metadata = reader.read()
    tiles = [[] for _ in range(file_tiles)]

    # create tiles
    for y, row in enumerate(pixels):
        for x, pixel in enumerate(row):
            # row_i = i % width
            tile = int(x / 8) % file_tiles
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
    return all_bytes


def patch_alphabet_tiles(output_rom: str, alphabet_png: str):
    alphabet_addr = 0xA742
    alphabet_tiles = 26

    all_bytes = tile_png_to_bytes(alphabet_png, alphabet_tiles)

    with open(output_rom, "r+b") as f:
        f.seek(alphabet_addr)
        # upper case
        f.write(all_bytes)
        # TODO lower case
        f.write(all_bytes)

    logging.info("replaced alphabet")


def patch_font_ex_tiles(output_rom: str, font_ex_png: str):
    font_ex_addr = 0xA742 + (26 * 2 * 8*2) # two alphabets * 16 bytes per tile
    font_ex_tiles = 39
    all_bytes = tile_png_to_bytes(font_ex_png, font_ex_tiles)

    with open(output_rom, "r+b") as f:
        f.seek(font_ex_addr)
        f.write(all_bytes)

    logging.info("replaced font_ex")


def import_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def patch_phrases(output_rom: str, phrases_file: str):
    rom_bank = 2
    index_addr = 0x06f9
    data_addr = 0x08F9
    max_end = 0x0e72

    module = import_from_path("phrases", phrases_file)

    absolute_phrase_indices = []
    with open(output_rom, "r+b") as f:
        absolute_data_addr = (0x4000 * rom_bank + data_addr)
        f.seek(absolute_data_addr)
        for phrase in module.phrases:
            absolute_phrase_indices.append(f.tell())
            for char in phrase:
                f.write(bytes([char]))
            f.write(bytes([0x00]))

        logging.info(f"phrase data: wrote {(f.tell() - absolute_data_addr)} of {(max_end - data_addr)}")
        if (f.tell() - absolute_data_addr) > (max_end - data_addr):
            logging.warning(f"wrote more phrase data than original rom")

        absolute_index_addr = (0x4000 * rom_bank + index_addr)
        f.seek(absolute_index_addr)
        for absolute_phrase_ptr in absolute_phrase_indices:
            # for some reason, the base phrase ptr is 0x0200
            # next is 0x0205, 0x0209, etc
            relative_phrase_ptr = absolute_phrase_ptr - absolute_data_addr + 0x0200
            # logging.info([hex(absolute_phrase_ptr), hex(relative_phrase_ptr)])
            high_byte = relative_phrase_ptr >> 8
            low_byte = relative_phrase_ptr & 0xFF
            f.write(bytes([low_byte, high_byte]))

    logging.info("replaced phrases and phrase indices")


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

    # Subcommand: alphabet
    alphabet_parser = subparsers.add_parser(
        "alphabet", help="Patch alphabet tiles in ROM"
    )
    alphabet_parser.add_argument(
        "--png", type=str, required=True, help="Path to alphabet data file."
    )

    # Subcommand: font_ex
    font_ex_parser = subparsers.add_parser(
        "font_ex", help="Patch extended font tiles in ROM"
    )
    font_ex_parser.add_argument(
        "--png", type=str, required=True, help="Path to extended font data file."
    )

    # Subcommand: phrases
    phrases_parser = subparsers.add_parser(
        "phrases", help="Patch alphabet tiles in ROM"
    )
    phrases_parser.add_argument(
        "--phrases_file",
        type=str,
        required=True,
        help="Path to translated phrases.py file.",
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
        patch_alphabet_tiles(args.output_rom, args.png)
    elif args.command == "font_ex":
        patch_font_ex_tiles(args.output_rom, args.png)
    elif args.command == "phrases":
        patch_phrases(args.output_rom, args.phrases_file)
    elif args.command == "inplace":
        patch_inplace(
            args.output_rom,
            args.bank,
            args.hex_addr,
            args.hex_value,
        )


if __name__ == "__main__":
    main()
