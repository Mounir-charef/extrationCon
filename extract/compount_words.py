import requests
from tqdm import tqdm
import re
from .cached_store import CachedStore

CACHE_FILE = "compound_words_cache.pkl"


class CompoundWordsStore(CachedStore):
    URL = "https://www.jeuxdemots.org/JDM-LEXICALNET-FR/20240924-LEXICALNET-JEUXDEMOTS-ENTRIES-MWE.txt"
    WORD_PATTERN = re.compile(r"(\d+);\"(.+)\";")

    def __init__(self):
        super().__init__(cache_file=CACHE_FILE)

    def _get_process_data(self) -> list[str]:
        try:
            response = requests.get(self.URL, stream=True)
            response.raise_for_status()
        except requests.RequestException as e:
            print(e)
            raise Exception("Failed to fetch compound words")

        compound_words = []
        for line in tqdm(
            response.iter_lines(), desc="Getting compound words from jdm..."
        ):
            line = line.decode("latin-1").strip()
            match = self.WORD_PATTERN.match(line)
            if match:
                compound_words.append(match.group(2).lower())

        return compound_words

    @property
    def compound_words(self) -> list[str]:
        return self.get_data()
