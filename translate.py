import os

from gameboy_translator import decode_gameboy_text


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

    with open(rom_path, "rb") as f:
        f.seek(file_start_offset)
        rom_data = f.read(file_end_offset - file_start_offset)
    
    # The decode_gameboy_text function expects a list of hex strings,
    # so we convert the raw bytes.
    rom_data_hex = [hex(byte) for byte in rom_data]
    return decode_gameboy_text(rom_data_hex)


if __name__ == "__main__":
    ROM_FILE = "Pocket Love (J) [S].gb"

    # Example from your notes: text starting around rom8::76c6
    # Assuming bank 8, with a start address and a reasonable end address
    # rom_bank = 8
    # start_addr, end_addr = (0x76C2, 0x76F9)
    # start_addr, end_addr = (0x766a, 0x7689)
    # rom_bank = 2
    # start_addr, end_addr = (0x766a, 0x7689)
    rom_bank = 30
    # stats
    # start_addr, end_addr = (0x5c10, 0x5c17)
    # start_addr, end_addr = (0x5c18, 0x5c21)
    # start_addr, end_addr = (0x5c22, 0x5c2b)
    # start_addr, end_addr = (0x5c2c, 0x5c35)
    # start_addr, end_addr = (0x5c36, 0x5c3f)
    # start_addr, end_addr = (0x5c40, 0x5c48)
    # task select
    start_addr, end_addr = (0x4018, 0x401f)
    # unknown tasks
    # start_addr, end_addr = (0x4ddc, 0x4de1)
    # start_addr, end_addr = (0x4de2, 0x4de7)


    result = translate_rom_text(ROM_FILE, rom_bank, start_addr, end_addr)
    print(
        f"--- Translation from Bank {rom_bank}, Addr 0x{start_addr:X} - 0x{end_addr:X} ---"
    )
    print(result)
    print("-----------------------------------------------------------------")
