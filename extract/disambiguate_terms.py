import re
import requests
from tqdm import tqdm
import zipfile
import io
from collections import defaultdict

from .cached_store import CachedStore

CACHE_FILE = "disambiguate_terms_cache.pkl"


class DisambiguateTermsStore(CachedStore):
    URL = "https://www.jeuxdemots.org/JDM-LEXICALNET-FR/20241010-LEXICALNET-JEUXDEMOTS-R1.txt.zip"
    WORD_PATTERN = re.compile(r"^(.*?)\s;\s(.*?)\s;\s(\d+)$")

    def __init__(self):
        super().__init__(cache_file=CACHE_FILE)

    def _get_process_data(self) -> dict[str, list[tuple[str, int]]]:
        try:
            response = requests.get(self.URL)
            response.raise_for_status()
        except requests.RequestException as e:
            print(e)
            raise Exception("Failed to fetch disambiguate terms")

        terms = defaultdict(list)
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
            with zip_file.open(zip_file.namelist()[0]) as file:
                for line in tqdm(file, desc="Reading disambiguate terms"):
                    line = line.decode("latin1").strip().lower()
                    match = self.WORD_PATTERN.match(line)
                    if match:
                        term = match.group(1)
                        disambiguate_term = match.group(2).split(">")
                        if len(disambiguate_term) < 2:
                            continue
                        weight = int(match.group(3))
                        terms[term].append((disambiguate_term[1], weight))
        return terms

    @property
    def disambiguate_terms(self) -> dict[str, list[tuple[str, int]]]:
        return self.get_data()

    def get_disambiguate_term(self, term: str) -> list[tuple[str, int]]:
        return self.disambiguate_terms.get(term, [])
