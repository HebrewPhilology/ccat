import os
import re
import pprint
import json
from pathlib import Path
from betacode_parser import *

INPUT_FOLDER = os.path.abspath("../ccat/parallel")
OUTPUT_FOLDER = os.path.abspath("../ccat/parallel_unicode")
EXTENSION = "par"
EXTENSION = "*." + EXTENSION


class BetacodeTranformer:
    """
    Class to convert text file in betacode to unicode
    """

    def __init__(self, file: str) -> None:
        """
        Constructor of the class
        Args:
            file_path (str): le chemin du fichier à transformer
        """
        self.file = file

    def convert(self) -> dict:
        """
        Convert the content of the betacode file and return a dictionnary


        Returns:
            dict: The content of the converted file
        """
        book = ''
        chap_num = ''
        verse_num = ''

        content = {}
        with open(self.file) as file:
            word = 1
            for line in file:
                line = line.strip()
                if re.search(
                    r"[1-9A-Z].+\d+:\d+", line
                ):  
                    book, chap_num, verse_num = re.split(r"[\s:]", line)
                    content.setdefault(book, {}).setdefault(chap_num, {}).setdefault(
                        verse_num, {}
                    )
                    word = 1
                elif line:
                    #print(f"{chap_num}:{verse_num}:{word}:'{line}'")
                    hb, gr = re.split(r"\t", line)
                    hb = beta_to_hebrew(hb, True)
                    hb = hb.replace("/", "")
                    gr = beta_to_greek(gr)
                    content[book][chap_num][verse_num][word] = {"hb": hb, "gr": gr}
                    word+=1
        return content

    def dump(self, filename: Path):
        """Convert the Betacode and dump it to a JSON file."""
        # Add JSON extension to file
        filename = filename.with_suffix(".json")

        # Create the output folder
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        # Execute the conversion and write the file
        with open(filename, "w") as f:
            json.dump(self.convert(), f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    for file in Path(INPUT_FOLDER).glob(EXTENSION):
        print(f'Converting file : {file.name}')
        BetacodeTranformer(file).dump(Path(OUTPUT_FOLDER) / file.name)
print("Done... 🥳")
