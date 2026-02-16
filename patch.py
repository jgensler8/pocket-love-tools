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


# Pre-compute multi-character keys for performance
MULTI_CHAR_KEYS = {}
for k in character_map.keys():
    if len(k) > 1:
        first = k[0]
        if first not in MULTI_CHAR_KEYS:
            MULTI_CHAR_KEYS[first] = []
        MULTI_CHAR_KEYS[first].append(k)

# Sort each list by length descending to ensure longest match first
for k in MULTI_CHAR_KEYS:
    MULTI_CHAR_KEYS[k].sort(key=len, reverse=True)


def encode_english_text(text: str) -> bytes:
    """
    Encodes an English string into Game Boy compatible bytes using a predefined map.
    Handles multi-character symbols like '<3' and replaces unknown characters with space.
    """
    encoded_bytes = bytearray()
    i = 0
    n = len(text)
    while i < n:
        found_multi = False
        char = text[i]

        # Check for multi-character symbols first (e.g., '<3', 'day')
        if char in MULTI_CHAR_KEYS:
            for symbol in MULTI_CHAR_KEYS[char]:
                if text.startswith(symbol, i):
                    encoded_bytes.append(character_map[symbol])
                    i += len(symbol)
                    found_multi = True
                    break

        if found_multi:
            continue

        byte_code = character_map.get(char)
        if byte_code is not None:
            encoded_bytes.append(byte_code)
        else:
            logging.warning(
                f"Unknown English character '{char}' (ord={ord(char)}) encountered. Replacing with space. (text={text})"
            )
            encoded_bytes.append(character_map[" "])  # Replace unknown with space
        i += 1
    return bytes(encoded_bytes)


def write_header_file(
    outfile: str,
    bank: int,
    scene_json: List[object],
):
    # calculate relative pointers (without the 0x4000, which is how they are stored natively)
    header_size = 2 * len(scene_json)
    relative_offset = header_size
    max_addr = 0x7FFF - 0x4000
    for scene_data in scene_json:
        scene_data["header_address"] = relative_offset
        relative_offset += len(scene_data["encoded_bytes"])

    if relative_offset > max_addr:
        logging.warning(
            f"ROM TRANSLATION EXTENDS PAST ROM BANK {bank} by {relative_offset - max_addr}"
        )

    # build header data
    # even if a scene would end up over the end of the bank, still keep its pointer to preserve structure
    all_data = bytearray()
    for scene_data in scene_json:
        header_address = scene_data["header_address"]
        low_byte = header_address & 0xFF
        high_byte_stored = header_address >> 8
        # print(f"{hex(new_cpu_address)} {hex(low_byte)} {hex(high_byte_stored)}")
        all_data.append(low_byte)
        all_data.append(high_byte_stored)

    # build scene data
    for scene_data in scene_json:
        if scene_data["header_address"] + len(scene_data["encoded_bytes"]) > max_addr:
            break
        all_data.extend(scene_data["encoded_bytes"])

    # --- Write to ROM ---
    bank_absolute_start = bank * BANK_SIZE
    with open(outfile, "r+b") as rom_file:
        # Write new header
        rom_file.seek(bank_absolute_start)
        rom_file.write(all_data)
        bytes_used = rom_file.tell() - bank_absolute_start
        bytes_left = (0x7FFF - 0x4000) - bytes_used
        logging.info(
            f"scenes: start={hex(bank_absolute_start)} end={hex(rom_file.tell())} used={bytes_used} left={bytes_left}"
        )


def rebuild_rom_headers(
    output_rom_path,
    extracted_json_path,
    translated_json_path,
    bytes_limit,
    bank_num,
    overflow_bank,
    prefix,
):
    """
    Rebuilds ROM headers and replaces scene text based on translated JSON data.
    Enforces a character limit per scene, truncating and warning when exceeded.
    Relocates translated text to a new area and updates header pointers.

    Args:
        output_rom_path (str): Path to the output ROM file.
        extracted_json_path (str): Path to the JSON file containing original ROM structure info.
        translated_json_path (str): Path to the JSON file containing translated scenes.
        bytes_limit (int): Maximum number of characters allowed per scene.
        bank_num (int): The ROM bank number where the text and header reside.
                                      E.g., "0x7000". This must be a safe, unused area in the ROM.
        overflow_bank (int): if scene data overflows the original bank, write overflow data into this scene bank and reference from the original bank (via scene extension)
        prefix: scene text prefix for all phrases in the bank
    """
    logging.info(
        f"patching bank {bank_num}, ex:{extracted_json_path} tr:{translated_json_path}"
    )
    try:
        newline_byte = encode_english_text("\n")
        at_byte = encode_english_text("@")
        hash_byte = encode_english_text("#")

        with open(translated_json_path, "r", encoding="utf-8") as f:
            translated_data = json.load(f)

        # with open(extracted_json_path, "r", encoding="utf-8") as f:
        #     extracted_data = json.load(f)

        translated_scenes = translated_data["translated_scenes"]

        # encode all scenes, checking for printing/line issues
        for i, scene_data in enumerate(translated_scenes):
            english_text = scene_data["english"]
            if prefix:
                english_text = prefix + english_text
            encoded_scene_bytes = encode_english_text(english_text)
            # encoded_scene_bytes = ""
            encoded_scene_bytes += b"\x00"  # Add null terminator
            scene_data["encoded_bytes"] = encoded_scene_bytes

            # warn for individual line length
            line_limit = 18
            lines = encoded_scene_bytes.split(newline_byte)
            for l_i, line in enumerate(lines):
                line_printable = line
                line_printable = line_printable.replace(at_byte, b"")
                line_printable = line_printable.replace(hash_byte, b"")
                line_printable = line_printable.replace(b"\x00", b"")
                if len(line_printable) > line_limit:
                    logging.warning(
                        f"bank {bank_num} scene {i} line {l_i} ({len(line_printable)}) greater than limit {line_limit}"
                    )
                # warn on the 4th line 18 char (where the flashing cursor is)
                # technically, we don't know which lines are character dialog
                # vs narrator (unless we parse metadata) so we'll just do out best
                # if l_i == 3 and len(line_printable) > line_limit - 1:
                #     logging.warning(f"bank {bank_num} scene {i} line {l_i} ({len(line_printable)}) possible truncation")

            if len(encoded_scene_bytes) > bytes_limit:
                logging.error(
                    f"bank {bank_num} scene {i} exceeds byte limit ({bytes_limit}). have {len(encoded_scene_bytes)}. Truncating with scene terminator"
                )
                encoded_scene_bytes = encoded_scene_bytes[: bytes_limit - 3]
                encoded_scene_bytes += b"\x82\x81\x00"  # Add scene end
                scene_data["encoded_bytes"] = encoded_scene_bytes

        if overflow_bank:
            overflow_scenes = []
            translation_len = 2 * len(translated_scenes) + sum(
                [len(scene["encoded_bytes"]) for scene in translated_scenes]
            )
            # continually swap out scenes until the first bank fits
            # note that the overflow bank can also overflow, shrug
            overflow_scene_index = 0
            for scene in translated_scenes:
                if translation_len < 0x7FFF - 0x4000:
                    break
                # never move short, empty scenes, or scene headers
                is_short_or_empty = len(scene["encoded_bytes"]) <= 3
                is_header_or_short_question = "(" in scene["english"]
                if is_short_or_empty or is_header_or_short_question:
                    continue
                # if overflow_scene_index >= 126:
                #     logging.error("would not be able to shift left")
                #     break
                translation_len -= len(scene["encoded_bytes"])
                # copy the scene to preserve the original text for the overflow bank
                overflow_scene = scene.copy()
                overflow_scenes.append(overflow_scene)
                # reencode the scene swap
                scene["encoded_bytes"] = encode_english_text(
                    f"__fd__{overflow_bank:02x}__{overflow_scene_index:02x}__00"
                )
                translation_len += len(scene["encoded_bytes"])
                overflow_scene_index += 1

            write_header_file(output_rom_path, bank_num, translated_scenes)
            if len(overflow_scenes) > 0:
                write_header_file(output_rom_path, overflow_bank, overflow_scenes)
            else:
                logging.info(f"overflow flag provided ({overflow_bank}) for bank {bank_num} but not used")
        else:
            write_header_file(output_rom_path, bank_num, translated_scenes)
        # logging.info("done")

    except FileNotFoundError as e:
        logging.error(f"File not found: {e}.")
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON format in one of the input files: {e}.")
    except KeyError as e:
        logging.error(
            f"Missing expected key in JSON data: {e}. Please ensure extracted_json contains 'bank_num', 'header_start_address', and 'header'."
        )


def patch_scene_meta(output_rom: str, extracted_json: str, new_scenes_json: str):
    # TODO
    pass


def patch_file(output_rom: str, bank: int, file: str):
    patches = {}

    with open(file, "r") as f:
        for line in f.read().split("\n"):
            if line.startswith("#"):
                continue
            addr, text = line.split(sep=" ", maxsplit=1)
            patches[addr] = text.strip('"')

    with open(output_rom, "r+b") as f:
        for addr, text in patches.items():
            text_bytes = encode_english_text(text)

            # it will be easier to record the bank addrs as 0x4??? so subtract another BANK_SIZE
            absolute_offset = bank * BANK_SIZE + (int(addr, 16) - BANK_SIZE)
            # logging.info(f"{absolute_offset} {text_bytes}")
            f.seek(absolute_offset)
            f.write(text_bytes)


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

    logging.info("patched alphabet")


def patch_font_ex_tiles(output_rom: str, font_ex_png: str):
    font_ex_addr = 0xA742 + (26 * 2 * 8 * 2)  # two alphabets * 16 bytes per tile
    font_ex_tiles = 40
    all_bytes = tile_png_to_bytes(font_ex_png, font_ex_tiles)

    with open(output_rom, "r+b") as f:
        f.seek(font_ex_addr)
        f.write(all_bytes)

    logging.info("patched font_ex")


def import_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def patch_phrases(output_rom: str, phrases_file: str):
    rom_bank = 2
    index_addr = 0x06F9
    data_addr = 0x08F9
    max_end = 0x0E72

    module = import_from_path("phrases", phrases_file)

    absolute_phrase_indices = []
    with open(output_rom, "r+b") as f:
        absolute_data_addr = 0x4000 * rom_bank + data_addr
        f.seek(absolute_data_addr)
        for phrase in module.phrases:
            absolute_phrase_indices.append(f.tell())
            for char in phrase:
                f.write(bytes([char]))
            f.write(bytes([0x00]))

        logging.info(
            f"phrase data: wrote {(f.tell() - absolute_data_addr)} of {(max_end - data_addr)}"
        )
        if (f.tell() - absolute_data_addr) > (max_end - data_addr):
            logging.warning(f"wrote more phrase data than original rom")

        absolute_index_addr = 0x4000 * rom_bank + index_addr
        f.seek(absolute_index_addr)
        for absolute_phrase_ptr in absolute_phrase_indices:
            # for some reason, the base phrase ptr is 0x0200
            # next is 0x0205, 0x0209, etc
            relative_phrase_ptr = absolute_phrase_ptr - absolute_data_addr + 0x0200
            # logging.info([hex(absolute_phrase_ptr), hex(relative_phrase_ptr)])
            high_byte = relative_phrase_ptr >> 8
            low_byte = relative_phrase_ptr & 0xFF
            f.write(bytes([low_byte, high_byte]))

    logging.info("patched phrases and phrase indices")


def patch_inplace(output_rom: str, bank: int, hex_addr: str, hex_value: str):
    with open(output_rom, "r+b") as f:
        absolute_offset = bank * BANK_SIZE + (int(hex_addr, 16) - BANK_SIZE)
        logging.info(f"patching absolute offset: {hex(absolute_offset)}")
        f.seek(absolute_offset)
        f.write(bytes.fromhex(hex_value))


def patch_code_raw(output_rom: str, file: str, hex_addr: str):
    file_bytes = bytearray()
    with open(file, "r") as f:
        file_str = f.read()
        for i, line in enumerate(file_str.split("\n")):
            if line.startswith(";"):
                continue
            # extract plain text byte code
            line_code = line.split(";", 1)[0]
            line_code = line_code.replace(" ", "")
            if len(line_code) % 2 != 0:
                logging.error(
                    f"file {file} line {i}: invalid number of plaintext characters"
                )
            file_bytes.extend(bytes.fromhex(line_code))

    with open(output_rom, "r+b") as f:
        f.seek(int(hex_addr, 16))
        f.write(file_bytes)

    logging.info(f"patched {file} at {hex_addr} ({len(file_bytes)} bytes)")


def patch_mbc(output_rom: str):
    # update the mbc
    with open(output_rom, "r+b") as f:
        f.seek(0x0147)
        # patch 03 MBC1+RAM+BATTERY -> 1b MBC5+RAM+BATTERY
        f.write(b'\x1b')
        # also, lengthen the file to be mbc-5 bytes long
        f.seek(256 * 0x4000 - 1)
        f.write(b"\x00")


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
        "--bytes_limit",
        type=int,
        default=90,
        help="Maximum bytes per scene (inclusive area between C0EA and C143)",
    )
    dialog_parser.add_argument(
        "--bank",
        type=int,
        required=True,
        help="The ROM bank number where the text and header reside.",
    )
    dialog_parser.add_argument(
        "--overflow_bank",
        type=int,
        required=False,
        help="If header + meta exceeds the original rom bank, use scene extension in the original bank and place scene data in this overflow bank",
    )
    dialog_parser.add_argument(
        "--prefix",
        type=str,
        default=None,
        help="phrase prefix for all phrases"
    )

    # Subcommand: scene_meta
    scene_meta_parser = subparsers.add_parser(
        "scene_meta", help="Patch new text into a scene"
    )
    scene_meta_parser.add_argument(
        "extracted_json",
        help="Path to the extracted JSON file (from extract_scene_meta.py).",
    )
    scene_meta_parser.add_argument(
        "new_scenes_json",
        help="Path to the new scene insertions JSON file",
    )

    # Subcommand: file
    patch_file_parser = subparsers.add_parser(
        "file", help="Patch translation into direct location"
    )
    patch_file_parser.add_argument(
        "--bank",
        type=int,
        required=True,
        help="bank to patch into",
    )
    patch_file_parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="Path to the patch file",
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

    # Subcommand: code
    code_raw_parser = subparsers.add_parser("code_raw", help="patch a bytecode file")
    code_raw_parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="plaintext bytecode file",
    )
    code_raw_parser.add_argument(
        "--hex_addr",
        type=str,
        required=True,
        help="offset into entire rom",
    )

    # Subcommand: mbc
    mbc_parser = subparsers.add_parser("mbc", help="patch mbc")

    args = main_parser.parse_args()

    if args.command == "dialog":
        rebuild_rom_headers(
            args.output_rom,
            args.extracted_json,
            args.translated_json,
            args.bytes_limit,
            args.bank,
            args.overflow_bank,
            args.prefix,
        )
    elif args.command == "scene_meta":
        patch_scene_meta(args.output_rom, args.extracted_json, args.new_scenes_json)
    elif args.command == "file":
        patch_file(args.output_rom, args.bank, args.file)
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
    elif args.command == "code_raw":
        patch_code_raw(args.output_rom, args.file, args.hex_addr)
    elif args.command == "mbc":
        patch_mbc(args.output_rom)


if __name__ == "__main__":
    main()
