def modify_rom(original_rom_path, modified_rom_path, changes):
    """
    Modifies a ROM file by replacing bytes at specified addresses.

    Args:
        original_rom_path (str): Path to the original ROM file.
        modified_rom_path (str): Path where the modified ROM will be saved.
        changes (dict): A dictionary where keys are addresses (int)
                        and values are the new byte values (int).
    """
    try:
        with open(original_rom_path, 'rb') as f_orig:
            rom_data = bytearray(f_orig.read()) # Read into a mutable bytearray

        for address, new_byte in changes.items():
            if address < len(rom_data):
                rom_data[address] = new_byte
            else:
                print(f"Warning: Address 0x{address:X} out of bounds for ROM size {len(rom_data)}.")

        with open(modified_rom_path, 'wb') as f_mod:
            f_mod.write(rom_data)

        print(f"Successfully created modified ROM: {modified_rom_path}")

    except FileNotFoundError:
        print(f"Error: Original ROM not found at {original_rom_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    ORIGINAL_ROM = "Pocket Love (J) [S].gb" # Replace with your original ROM file name
    MODIFIED_ROM = "pkl.gb" # Name for the output modified ROM

    # Define your changes: {address: new_byte_value}
    # Example: Change byte at 0x1234 to 0xFF, and at 0x5678 to 0xAA
    modifications = {
        # 0xA7D2: 0x00,
        # 0xA7D3: 0x00,
        # 0xA7D4: 0x7e,
        # 0xA7D5: 0x7e,
    }
    # alphabet start:0xA742
    modifications.update({0xA7D2 + i: v for i,v in enumerate([
        0x00, 0x00,
        0x7e, 0x7e,
        0x42, 0x42,
        0x7e, 0x7e,
        0x42, 0x42,
        0x42, 0x42,
        0x42, 0x42,
        0x00, 0x00,
    ])})

    modify_rom(ORIGINAL_ROM, MODIFIED_ROM, modifications)