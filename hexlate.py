import argparse
from typing import List
from dictionary_en import character_map
from patch import encode_english_text


def hexlate(text: str) -> List[int]:
    return [character_map.get(char, 0x7F) for char in text]


if __name__ == "__main__":
    main_parser = argparse.ArgumentParser(description="encode text to index list")
    main_parser.add_argument(
        "--simple", default=False, type=bool, help="ignore multi-characters"
    )
    main_parser.add_argument("text", help="text to hexlate")

    args = main_parser.parse_args()

    if args.simple:
        print(hexlate(args.text))
    else:
        print([b for b in encode_english_text(args.text)])
