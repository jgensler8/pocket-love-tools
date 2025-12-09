import argparse
from typing import List
from dictionary_en import character_map


def hexlate(text: str) -> List[int]:
    return [character_map.get(char, 0x7F) for char in text]

if __name__ == "__main__":
    main_parser = argparse.ArgumentParser(
        description="encode text to index list"
    )
    main_parser.add_argument("text", help="text to hexlate")

    args = main_parser.parse_args()

    print(hexlate(args.text))