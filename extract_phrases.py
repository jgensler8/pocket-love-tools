import os
from dictionary_katakana import character_map
from typing import List

ROM_FILE = "Pocket Love (J) [S].gb"
BANK_SIZE = 0x4000  # 16KB for Game Boy ROMs


def scan_phrase_dictionary(rom_path, bank, start_address):
    """
    Scans a region of a ROM for null-terminated phrases and translates them.

    Args:
        rom_path (str): Path to the ROM file.
        bank (int): The ROM bank number.
        start_address (int): The starting address within the bank.

    Returns:
        list: A list of translated phrases.
    """
    if not os.path.exists(rom_path):
        print(f"Error: ROM file not found at {rom_path}")
        return []

    # Calculate the absolute start position in the file
    bank_start_offset = bank * BANK_SIZE
    address_in_bank = start_address % BANK_SIZE
    file_start_offset = bank_start_offset + address_in_bank

    phrases: List[List[bytes]] = []
    try:
        with open(rom_path, "rb") as f:
            f.seek(file_start_offset)
            data = f.read(BANK_SIZE - address_in_bank)  # Read until the end of the bank

        current_phrase_bytes = []
        for byte in data:
            if byte == 0x00:  # Null terminator
                if current_phrase_bytes:
                    phrases.append(current_phrase_bytes)
                    current_phrase_bytes = []
            else:
                current_phrase_bytes.append(byte)
        # print(f"last phrase: {len(current_phrase_bytes)}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return phrases


def translate_phrases(phrases: List[List[bytes]]):
    # Translate and add the completed phrase
    translate_phrases = []
    for phrase_bytes in phrases:
        translated_phrase = "".join(
            character_map.get(b, f"[?{b:02X}]") for b in phrase_bytes
        )
        translate_phrases.append(translated_phrase)
    return translate_phrases


if __name__ == "__main__":
    rom_bank = 2
    start_addr = 0x48F9
    phrases_to_find = 0xFF

    found_phrases = scan_phrase_dictionary(ROM_FILE, rom_bank, start_addr)
    print(f"Found {len(found_phrases)} phrases. expected {phrases_to_find}")
    found_phrases_limit = found_phrases[:256]
    for i, translation in enumerate(translate_phrases(found_phrases_limit)):
        print(f"Phrase {i}: {translation}")
    with open("phrases.py", "w") as f:
        f.write("phrases = [\n")
        for i, phrase in enumerate(found_phrases_limit[:256]):
            f.write(f"{str(phrase)}, # ff{i:02X} {"".join([f"{d:02X}" for d in phrase])}\n")
        f.write("]")
