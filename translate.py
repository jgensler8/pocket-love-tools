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
    # start_addr, end_addr = (0x4018, 0x401f)
    # unknown tasks
    # start_addr, end_addr = (0x4ddc, 0x4de1)
    # start_addr, end_addr = (0x4de2, 0x4de7)
    # travel window
    # start_addr, end_addr = (0x442e, 0x4441)
    # start_addr, end_addr = (0x4456, 0x4469)
    # start_addr, end_addr = (0x446a, 0x447d)
    # start_addr, end_addr = (0x447e, 0x4491)
    # start_addr, end_addr = (0x4492, 0x44a5)
    # club soccer start
    # start_addr, end_addr = (0x4531, 0x4541)
    # club task select submenu
    # start_addr, end_addr = (0x4660, 0x4667)
    # start_addr, end_addr = (0x450b, 0x4511)
    # start_addr, end_addr = (0x4512, 0x4515)
    # club weekend task select option
    # start_addr, end_addr = (0x43f8, 0x43fd)
    # start_addr, end_addr = (0x43fe, 0x4403)
    # club task > ill try > lines (failed to schedule task, seems to be for all clubs)
    # start_addr, end_addr = (0x4d82, 0x4d88)
    # start_addr, end_addr = (0x4d89, 0x4d8f)
    # club task > ill try > lines (scheduled)
    # club task > this club > lines
    # start_addr, end_addr = (0x4c1e, 0x4c21)
    # start_addr, end_addr = (0x4c25, 0x4c2b)
    # second week holiday
    # start_addr, end_addr = (0x4004, 0x400b)
    # start_addr, end_addr = (0x400c, 0x4013)
    # weekend travel
    # start_addr, end_addr = (0x55b6, 0x55c6)
    # start_addr, end_addr = (0x55c7, 0x55d7)
    # start_addr, end_addr = (0x55d8, 0x55e8)
    # start_addr, end_addr = (0x55e9, 0x55f9)
    # start_addr, end_addr = (0x55fa, 0x560a)
    # start_addr, end_addr = (0x560b, 0x561b)
    # start_addr, end_addr = (0x561c, 0x562c)
    # start_addr, end_addr = (0x562d, 0x563d)
    # start_addr, end_addr = (0x563e, 0x564e)
    # start_addr, end_addr = (0x564f, 0x565f)
    # start_addr, end_addr = (0x5660, 0x5670)
    # start_addr, end_addr = (0x5671, 0x5681)
    # start_addr, end_addr = (0x5682, 0x5692)
    # start_addr, end_addr = (0x5693, 0x56a3)
    # start_addr, end_addr = (0x56a4, 0x56b4)
    # start_addr, end_addr = (0x56b5, 0x56c5)
    # start_addr, end_addr = (0x56c6, 0x56d6)
    # start_addr, end_addr = (0x56d7, 0x56e7)
    # start_addr, end_addr = (0x56e8, 0x56f8)
    # start_addr, end_addr = (0x56f9, 0x5709)
    # start_addr, end_addr = (0x570a, 0x571a)
    # start_addr, end_addr = (0x571b, 0x572b)
    # start_addr, end_addr = (0x572c, 0x573b)
    # start_addr, end_addr = (0x573d, 0x574d)
    # start_addr, end_addr = (0x574e, 0x575e)
    # start_addr, end_addr = (0x575f, 0x576f)
    # start_addr, end_addr = (0x5770, 0x5780)
    # start_addr, end_addr = (0x5781, 0x5791)
    # start_addr, end_addr = (0x5792, 0x57a3)
    # info window
    # start_addr, end_addr = (0x40c6, 0x40d7)
    # start_addr, end_addr = (0x40da, 0x40eb)
    # start_addr, end_addr = (0x4102, 0x4113)
    # start_addr, end_addr = (0x4116, 0x4127)
    # start_addr, end_addr = (0x412a, 0x413b)
    # start_addr, end_addr = (0x4c09, 0x4c19)
    # start_addr, end_addr = (0x41ba, 0x41c4)
    # start_addr, end_addr = (0x41c9, 0x41d4)
    # info > girls
    # start_addr, end_addr = (0x45c2, 0x45c9)
    # start_addr, end_addr = (0x45ca, 0x45d1)
    # start_addr, end_addr = (0x45d2, 0x45d9)
    # start_addr, end_addr = (0x45da, 0x45e1)
    # start_addr, end_addr = (0x45e2, 0x45e9)
    # start_addr, end_addr = (0x45ea, 0x45f1)
    start_addr, end_addr = (0x45f2, 0x45f9)


    result = translate_rom_text(ROM_FILE, rom_bank, start_addr, end_addr)
    print(
        f"--- Translation from Bank {rom_bank}, Addr 0x{start_addr:X} - 0x{end_addr:X} ---"
    )
    print(result)
    print("-----------------------------------------------------------------")
