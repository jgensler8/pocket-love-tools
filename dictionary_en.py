# --- English to Game Boy Byte Mapping ---
character_map = {
    "__day": 0x3D,
    "__month": 0x3E,
    "$": 0x3F,  # font_ex
    ",": 0x40,
    "'": 0x41,
    '"': 0x42,
    ":": 0x43,
    ";": 0x44,
    ">": 0x45,
    "<": 0x46,
    "*": 0x47,
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
    " ": 0x7F,  # Space (from dictionary_katakana.py 0x7E, 0x7F, 0x80 are spaces)
    "\n": 0x80,
    # TODO: these are placeholders for theoretical control chars
    "@": 0x82,
    "#": 0x81,
    "__heart": 0x69,
    "^": 0x69, # TODO placeholder under lenght is double checked, also to suppress patch warnings
    "!": 0x6A,
    "?": 0x6B,
    "~": 0x7A,
    "-": 0x7B,
    ".": 0x7C,
    "/": 0x7D,
    "=": 0x6E,
    "(": 0x65,
    ")": 0x66,
    "__ff": 0xff,
    "__fd": 0xfd,
}

# Programmatically add A-Z and a-z
start_char_code = 0x09
for i in range(26):
    # Uppercase A-Z
    character_map[chr(ord("A") + i)] = start_char_code + i
    # Lowercase a-z
    character_map[chr(ord("a") + i)] = start_char_code + 26 + i

# __01 (for large segments that are cumbersome for inplace)
for i in range(0x00, 0x3e):
    character_map[f"__{i:02x}"] = i