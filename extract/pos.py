from cached_store import CachedStore
import requests
from datetime import datetime
from tqdm import tqdm

CACHE_FILE = "pos_cache.pkl"
ENDPOINT_URL = "https://jdm-api.demo.lirmm.fr/v0/relations/from/{word}"
POS_TYPE = 4


class PosStore(CachedStore):
    def __init__(self):
        super().__init__(cache_file=CACHE_FILE)

    def _get_process_data(self) -> dict:
        return {}

    @staticmethod
    def _fetch_process_data(word) -> dict:
        try:
            response = requests.get(ENDPOINT_URL.format(word=word))
            response.raise_for_status()
            response = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error during POS request for {word}: {e}")
            response = {}

        data = {}
        for entry in tqdm(response['nodes'], desc=f"Processing POS data for {word}"):
            if entry['type'] == POS_TYPE and 'name' in entry:
                data[entry['name']] = entry['w']

        return data

    def _update_and_cache(self, word, data):
        self.data[word] = data
        self.last_updated = datetime.now()
        self._save_cache()

    def get_highest_post(self, word):
        pos_data = self.get(word)
        if not pos_data:
            return None
        return max(pos_data, key=pos_data.get)

    def get(self, word):
        if word not in self.data:
            self._update_and_cache(word, self._fetch_process_data(word))
        return self.data.get(word, {})
