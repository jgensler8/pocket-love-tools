from dictionary_katakana import character_map
from phrases import phrases


def decode_gameboy_text(rom_data: list[str]) -> str:
    """
    Decodes a list of byte values from a game scene into a Japanese string.
    This function is adapted from your translate_rom_text script but works on a list of bytes
    instead of reading directly from a ROM file.

    Args:
        rom_data (list[str]): A list of hex string values representing a scene.
    Returns:
        str: The decoded Japanese text.
    """
    japanese_text = []
    i = 0
    while i < len(rom_data):
        byte_hex = rom_data[i]
        # Convert the hex string from JSON (e.g., "0xff") into an integer
        byte = int(byte_hex, 16)
        if byte == 0x00:
            # The extractor script already splits scenes by the 0x00 terminator
            pass
        elif byte == 0x80:  # Newline character
            japanese_text.append("\n")
        elif byte == 0xFE:  # wait / continuation
            pass
        elif byte == 0xFF:  # Phrase dictionary compression
            i += 1  # Move to the next byte for the phrase index
            if i < len(rom_data):
                # Also convert the phrase index from a hex string
                phrase_index = int(rom_data[i], 16)
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