
def parse_ramfunc_table(file_path):
    """
    Parses a file containing space-separated hexadecimal bytes representing
    little-endian 16-bit addresses.

    Args:
        file_path (str): The path to the file.

    Returns:
        list: A list of integers, where each integer is a parsed address.
    """
    addresses = []
    try:
        with open(file_path, 'r') as f:
            hex_string = f.read()

        # Split the string into a list of hex byte strings
        byte_strings = hex_string.strip().split()

        # The addresses are in little-endian format, so we read two bytes at a time.
        # For example, "7c c2" becomes 0xc27c.
        # We can iterate through the list, taking 2 elements at a time.
        for i in range(0, len(byte_strings), 2):
            # Ensure we don't go out of bounds if there's an odd number of bytes
            if i + 1 < len(byte_strings):
                low_byte_str = byte_strings[i]
                high_byte_str = byte_strings[i+1]

                # Combine them in big-endian order for integer conversion
                address_hex = high_byte_str + low_byte_str

                # Convert hex string to integer and add to our list
                addresses.append(int(address_hex, 16))

    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return addresses

# Path to your file
file_path = 'ramfunc_table_bytes.txt'

# Get the list of addresses
ramfunc_addresses = parse_ramfunc_table(file_path)

# --- Address Conversion ---

# Constants for address conversion
RAM_BASE = 0xc27c
ROM_BASE = 0x6f4a

# Calculate and print the converted addresses
print("Converted ROM addresses:")
for i, ram_addr in enumerate(ramfunc_addresses):
    # Calculate the offset from the base RAM address
    offset = ram_addr - RAM_BASE
    
    # Calculate the new ROM address
    rom_addr = ROM_BASE + offset
    
    # Print in the desired format: f"{6xxx or 7xxx} romfun{0A}_{cxxx or dxxx}"
    print(f"{rom_addr:04x} ramfun{i:02X}_{ram_addr:04x}")

print(f"\nConverted {len(ramfunc_addresses)} function addresses.")
