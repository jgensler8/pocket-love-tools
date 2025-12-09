# --- English to Game Boy Byte Mapping ---
# This map needs to be carefully constructed based on the game's actual font tiles.
# For now, it's a best-effort attempt using existing known mappings and placeholders.
# You will need to verify and expand this map based on your ROM's font data.
# Placeholder values (e.g., 0x81, 0xA1) are arbitrary and will likely display
# incorrect characters if not mapped to actual font tiles in your ROM.
character_map = {
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
    character_map[chr(ord("A") + i)] = start_char_code + i
    # Lowercase a-z
    character_map[chr(ord("a") + i)] = start_char_code + 26 + i