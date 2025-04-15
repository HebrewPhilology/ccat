# This script converts the files in the ccat parallel folder to json and unicode.
# Frédérique Michèle Rey 2025
# v. 1.0

import os
import re
import pprint
import json
from pathlib import Path
from betacode_parser import *

INPUT_FOLDER = os.path.abspath("../ccat/parallel")
OUTPUT_FOLDER = os.path.abspath("../ccat/parallel_unicode")
EXTENSION = "*.par"

IGNORE = [
    "{#}",  # Asterized passage (in Job).
    "{g}",  # Reference to difference between the text of Rahlfs and that of the relevant G�ttingen edition.
    "..a",  # Word included in one of the Aramaic sections.
    "*",  # Ketib.
    "**",  # Qere.
    "*z",  # Qere wela ketib, ketib wela qere.
    "[ ]",  # Reference of number of verse in LXX, different from MT.
    "[[ ]]",  # Reference number of verse in MT, different from the LXX.
    "--- {x}",  # Apparent minus or
    "--+ {x}",  # apparent plus created by lack of equivalence between long stretches of text in the LXX and MT.
    "{...}",  # Equivalent reflected elsewhere in the text, disregarded by indexing program.
    "~",  # Difference in sequence between MT and LXX, denoted after the first Hebrew word and before the second one,
    # as well as between two Greek words.
    "~~~",  # Equivalent of the Hebrew or Greek word(s) occurring elsewhere in the verse or context (transposition).
    "{..~}",  # Stylistic or grammatical transposition.
    "---",  # In the Greek column:  Hebrew counterpart lacking in the LXX (minus in the LXX).
    "--+",  # In col a. of the Hebrew:  element �added� in the Greek (plus in the LXX).
    "''",  # Long minus or plus (at least four lines).
    "{d}",  # Reference to doublet (occurring between the two elements of the doublet.
    "{..d}",  # Distributive rendering, occurring once in the translation but referring to more than one Hebrew word.
    "{..r}",  # Notation in Hebrew column of elements repeated in the translation.
    "?",  # Questionable notation, equivalent, etc.
    "{p}",  # Greek preverb representing Hebrew preposition.
    "{..p}",  # Preposition added in the LXX in accordance with the rules of the Greek language or translational habits.
    "{!}",  # Infinitive absolute.
    "{s}",  # Hebrew M/, MN (comparative, superlative) reflected by Greek comparative or superlative.
    "{t}",  # Transliterated Hebrew word.
    "#",  # Long line continuing in next one, placed both at the end of the line running over and at the beginning of the following line in the opposite column.
    "=",  # Introducing col. b of the Hebrew (a selection of retroverted readings, presumably found in the parent text of the LXX).
    "{v}",  # The reading of the main text of the LXX seems to reflect a secondary text, while the �original� reading is reflected in a variant.
    "=%"  # Introducing categories of translation technique recorded in col. b.
    "=%vap"  # Change from active to passive form in verbs.
    "=%vpa"  # Change from passive to active form in verbs.
    "=%p"  # Difference in preposition or particle.
    "=%p+"  # Addition of preposition or particle.
    "=p%-"  # Omission of preposition or particle.
    "=;"  # Retroversion in col. b based on equivalence occurring in immediate or remote context.
    "G"  # Hebrew variant, but at this stage no plausible retroversion is suggested.
    "=+"  # Difference in numbers between MT and the LXX.
    "=@"  # Etymological exegesis.
    "=@...a"  # Etymological exegesis according to Aramaic.
    "=:"  # Introducing reconstructed proper noun.
    "=v"  # Difference in vocalization (reading).
    "=r"  # Incomplete retroversion.
    "{*}"  # Agreement of LXX with ketib.
    "{**}"  # Agreement of LXX with qere.
    "."  # Interchange of consonants between MT and the presumed Hebrew parent text of the LXX.
    ".rd"  # As above, interchange of R/D, etc.
    ".m"  # As above, metathesis.
    ".z"  # Possible abbreviation.
    ".s"  # One word of MT separated into two or more words in the parent text of the LXX.
    ".j"  # Two words of MT joined into one word in the parent text of the LXX.
    ".w",  # Different word-division reflected in the parent text of the LXX.
]


def hb_betacode(hb: str) -> str:
    """
    Convert Hebrew text to betacode while ignoring the IGNORE list.

    Args:
        hb (str): The Hebrew text in betacode
    Return:
        str: The converted text in Unicode ignoring the IGNORE list.
    """

    # Create a regex with the IGNORE list
    ignore = "|".join(re.escape(i) for i in IGNORE)
    result = ""
    position = 0

    # Search each instance of ignore
    for match in re.finditer(ignore, hb):
        start, end = match.start(), match.end()
        # Convert the text before the ignore instance
        before_ignore = hb[position:start]
        converted = beta_to_hebrew(before_ignore, True)
        # Concatenate the converted hebrew and the ignore instance
        result += converted + hb[start:end]
        # Update position
        position = end

    # Finish the work...
    remaining = hb[position:]
    result += beta_to_hebrew(remaining, True)

    return result
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
        book = ""
        chap_num = ""
        verse_num = ""

        content = {}
        with open(self.file) as file:
            word = 1
            for line in file:
                line = line.strip()
                if re.search(r"[1-9A-Z].+\d+:\d+", line):
                    book, chap_num, verse_num = re.split(r"[\s:]", line)
                    content.setdefault(book, {}).setdefault(chap_num, {}).setdefault(
                        verse_num, {}
                    )
                    word = 1
                elif line:
                    # print(f"{chap_num}:{verse_num}:{word}:'{line}'")
                    hb, gr = re.split(r"\t", line)
                    hb = hb_betacode(hb)
                    hb = hb.replace("/", "")
                    gr = beta_to_greek(gr)
                    content[book][chap_num][verse_num][word] = {"hb": hb, "gr": gr}
                    word += 1
        return content

    def dump(self, file: Path) -> None:
        """
        Convert the Betacode and dump it to a JSON file.
        Args:
            filename (Path): Path of the file that is converted
        """

        # Add JSON extension to file
        file = file.with_suffix(".json")

        # Create the output folder
        os.makedirs(os.path.dirname(file), exist_ok=True)

        # Execute the conversion and write the file
        with open(file, "w") as f:
            json.dump(self.convert(), f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    for file in Path(INPUT_FOLDER).glob(EXTENSION):
        print(f"Converting file : {file.name}")
        BetacodeTranformer(file).dump(Path(OUTPUT_FOLDER) / file.name)
print("Done... 🥳")
