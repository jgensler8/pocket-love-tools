import os
from dictionary import character_map

def translate_rom_text(rom_path, bank, start_address, end_address):
    """
    Reads and translates text from a specified address range in a ROM file,
    handling custom character encoding and phrase dictionary compression.

    Args:
        rom_path (str): Path to the ROM file.
        bank (int): The ROM bank number to read from.
        start_address (int): The starting address within the bank (e.g., 0x4000).
        end_address (int): The ending address within the bank.

    Returns:
        str: The translated text.
    """
    if not os.path.exists(rom_path):
        return f"Error: ROM file not found at {rom_path}"

    BANK_SIZE = 0x4000  # 16KB for Game Boy ROMs

    # Calculate the absolute start and end positions in the file
    # Bank 0 is at 0x0000, Bank 1+ is at 0x4000, 0x8000, etc.
    # The address within a bank (e.g., 0x4000-0x7FFF) maps to the start of that bank's data.
    file_start_offset = bank * BANK_SIZE + (start_address % BANK_SIZE)
    file_end_offset = bank * BANK_SIZE + (end_address % BANK_SIZE) + 1

    translated_text = []

    with open(rom_path, 'rb') as f:
        f.seek(file_start_offset)
        rom_data = f.read(file_end_offset - file_start_offset)

    i = 0
    while i < len(rom_data):
        byte = rom_data[i]

        if byte == 0x80:  # Newline character based on notes
            translated_text.append('\n')
        elif byte == 0xff:  # Phrase dictionary compression
            translated_text.append('()')
            i += 1  # Skip the next byte which is the dictionary index
        else:
            # Look up the character in the map, default to a placeholder
            char = character_map.get(byte, f'[?{byte:02X}]')
            if char is not None:
                translated_text.append(char)

        i += 1

    return " ".join(translated_text)

if __name__ == "__main__":
    ROM_FILE = "Pocket Love (J) [S].gb"

    # Example from your notes: text starting around rom8::76c6
    # Assuming bank 8, with a start address and a reasonable end address
    rom_bank = 8
    start_addr = 0x76c2
    end_addr = 0x76f9

    result = translate_rom_text(ROM_FILE, rom_bank, start_addr, end_addr)
    print(f"--- Translation from Bank {rom_bank}, Addr 0x{start_addr:X} - 0x{end_addr:X} ---")
    print(result)
    print("-----------------------------------------------------------------")