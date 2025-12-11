import os
from typing import List, Tuple
import json

import logging
import argparse

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

ROM_FILE = "Pocket Love (J) [S].gb"
BANK_SIZE = 0x4000  # 16KB for Game Boy ROMs

META_INSTRUCTION_ARGS = {
    0: None,
}


def read_scene_pointers(rom_data: bytes, header_start: int) -> List[int]:
    """
    Reads the scene header and returns a list of scene start addresses.

    Args:
        rom_data (bytes): The content of the ROM bank.
        header_start (int): The starting offset of the header in the bank.

    Returns:
        List[int]: A list of scene start addresses in order parsed in file
    """
    pointers = []
    # The header contains 2-byte little-endian pointers.
    # We scan until we hit an invalid pointer, assuming the table is contiguous.
    for i in range(header_start, len(rom_data), 2):
        low_byte = rom_data[i]
        high_byte = rom_data[i + 1]

        # Combine to form a 16-bit address as seen by the CPU (e.g., 0x412A)
        # The user's formula: (high_byte + 0x40) << 8 | low_byte
        address = ((high_byte + 0x40) << 8) | low_byte
        if address < 0x4000 or address >= 0x8000: # Pointers should be within the bank's address space
            logging.warning(f"Address 0x{address:04X} at offset 0x{i:04X} is outside the 0x4000-0x7FFF range. Stopping header scan.")
            break

        pointers.append(address)

    return pointers


def get_scenes_from_pointers(rom_data: bytes, pointers: List[int]) -> List[bytes]:
    """
    Extracts scene data from the ROM bank based on a list of pointers.

    Args:
        rom_data (bytes): The content of the ROM bank.
        pointers (List[int]): A list of scene start addresses.

    Returns:
        List[bytes]: A list of byte sequences, in the same order of the pointers
    """
    scenes = []
    for start_ptr in pointers:
        # Convert CPU address to an offset inside the bank data
        start_offset = start_ptr - 0x4000

        # Find the end of the scene by looking for the null terminator (0x00)
        end_offset = -1
        search_start = start_offset
        try:
            # do no split on phrase and name control codes
            while end_offset == -1 or rom_data[end_offset - 1] in [0xff, 0xfe]:
                # if end_offset > 0:
                #     logging.info("name ctrl code")
                end_offset = rom_data.index(0x00, search_start)
                search_start = end_offset + 1
        except ValueError:
            # If no null terminator is found, we can't define the scene.
            logging.warning(f"No null terminator found for scene starting at 0x{start_ptr:04X}")
            continue

        scenes.append(rom_data[start_offset:end_offset])
    return scenes


def extract_scenes_from_bank(rom_path: str, bank_num: int, header_start: int) -> Tuple[List[int], List[bytes]]:
    """
    Reads a ROM bank, parses the scene header, and extracts all scenes.

    Args:
        rom_path (str): Path to the ROM file.
        bank_num (int): The ROM bank number to process.
        header_start (int): The starting address of the scene header.

    Returns:
        A tuple containing the list of pointers and the list of scene data.
    """
    if not os.path.exists(rom_path):
        logging.error(f"ROM file not found at {rom_path}")
        return [], []

    file_start_offset = bank_num * BANK_SIZE

    with open(rom_path, "rb") as f:
        f.seek(file_start_offset)
        bank_data = f.read(BANK_SIZE)

    header_start_offset = header_start % BANK_SIZE

    scene_pointers = read_scene_pointers(bank_data, header_start_offset)
    # scenes = get_scenes_from_pointers(bank_data, scene_pointers)
    return scene_pointers, []

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract scene data from a Game Boy ROM bank.")
    parser.add_argument(
        "--bank",
        type=int,
        default=5,
        help="The ROM bank number to process (default: 8)."
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        default="out",
        help="output directory prefix"
    )
    args = parser.parse_args()

    pointers, scenes_data = extract_scenes_from_bank(ROM_FILE, bank_num=args.bank, header_start=0x4000)

    logging.info(f"max: {hex(max(pointers))}")

    # Format pointers and scene data as hexadecimal strings for better readability
    output_data = {
        "header": [hex(p) for p in pointers],
        # "scene_meta": [[hex(byte) for byte in scene] for scene in scenes_data],
    }

    outfile = os.path.join(args.out_dir, f"bank_{args.bank}_ex.json")
    with open(outfile, "w") as f:
        json.dump(output_data, f, indent=2)
