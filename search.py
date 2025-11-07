import re

def search_bytes_in_file(filepath, hex_string):
    """
    Searches for a sequence of bytes in a file.

    Args:
        filepath (str): The path to the file to search.
        hex_string (str): A string of hexadecimal digits representing the byte sequence (e.g., "00B0FF").

    Returns:
        list: A list of integer offsets where the byte sequence was found.
    """
    try:
        # Convert hex string to bytes
        search_bytes = bytes.fromhex(hex_string)

        with open(filepath, 'rb') as f:
            file_content = f.read()

        # Find all occurrences
        offsets = []
        start = 0
        while True:
            index = file_content.find(search_bytes, start)
            if index == -1:
                break
            offsets.append(index)
            start = index + 1 # Continue searching after the found occurrence

        return offsets

    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return []
    except ValueError:
        print(f"Error: Invalid hexadecimal string '{hex_string}'. Please provide an even number of hex digits.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

if __name__ == "__main__":
    file_to_search = "Pocket Love (J) [S].gb"

    print(search_bytes_in_file(file_to_search, "000038384444"))

    tile_index = [274, 289, 325, 379, 297, 290]
    # guess that 255/256 would be potential offsets

    for diff in range(-1025, 1025):
        new_sequence = [t - diff for t in tile_index]
        new_hex_sequence = "".join([f"{t & 0xFF:02X}" for t in new_sequence])
        # print(new_hex_sequence)
        found_offsets = search_bytes_in_file(file_to_search, new_hex_sequence)
        if found_offsets:
            print(f"Byte sequence '{new_hex_sequence}' found at offsets: {found_offsets}")
    for diff in range(-513, 513):
        new_sequence = [t - diff for t in tile_index[::-1]] # Search in reverse order
        new_hex_sequence = "".join([f"{t & 0xFF:02X}" for t in new_sequence])
        # print(new_hex_sequence)
        found_offsets = search_bytes_in_file(file_to_search, new_hex_sequence)
        if found_offsets:
            print(f"Byte sequence (reversed) '{new_hex_sequence}' found at offsets: {found_offsets}")
