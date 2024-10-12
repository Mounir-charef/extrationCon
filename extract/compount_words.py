import pickle
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import List
from tqdm import tqdm
import re


class CompoundWordsCache:
    DATA_FOLDER = Path("data")
    CACHE_FILE = DATA_FOLDER / "compound_words_cache.pkl"
    CACHE_EXPIRY = timedelta(days=7)  # Cache expires after 7 days
    URL = "https://www.jeuxdemots.org/JDM-LEXICALNET-FR/20240924-LEXICALNET-JEUXDEMOTS-ENTRIES-MWE.txt"
    WORD_PATTERN = re.compile(r"(\d+);\"(.+)\";")

    def __init__(self):
        self.__compound_words = None
        self.last_updated = None
        self._ensure_data_folder()
        self._load_or_fetch()

    def _ensure_data_folder(self):
        if not self.DATA_FOLDER.exists():
            self.DATA_FOLDER.mkdir(parents=True)

    def _load_or_fetch(self):
        if not self._load_cache():
            self._fetch_and_cache()

    def get_compound_words(self) -> None:
        if self._is_cache_expired():
            self._fetch_and_cache()

    def _is_cache_expired(self) -> bool:
        if not self.last_updated:
            return True
        return (datetime.now() - self.last_updated) > self.CACHE_EXPIRY

    def _fetch_and_cache(self):
        try:
            response = requests.get(self.URL, stream=True)
            response.raise_for_status()
        except requests.RequestException as e:
            print(e)
            raise Exception("Failed to fetch compound words")

        self.__compound_words = []
        for line in tqdm(
            response.iter_lines(), desc="Getting compound words from jdm..."
        ):
            line = line.decode("ANSI").strip()
            match = self.WORD_PATTERN.match(line)
            if match:
                self.__compound_words.append(match.group(2).lower())

        self.last_updated = datetime.now()
        self._save_cache()

        print(f"Compound words fetched and cached. Total: {len(self.__compound_words)}")

    def _save_cache(self):
        with open(self.CACHE_FILE, "wb") as f:
            pickle.dump((self.__compound_words, self.last_updated), f)

    def _load_cache(self) -> bool:
        if self.CACHE_FILE.exists():
            with open(self.CACHE_FILE, "rb") as f:
                self.__compound_words, self.last_updated = pickle.load(f)
            return True
        return False

    @property
    def compound_words(self) -> List[str]:
        if self.__compound_words is None:
            self.get_compound_words()

        return self.__compound_words
