import json
from typing import Optional, Union
import requests
from tqdm import tqdm
import re
from .cached_store import CachedStore
from datetime import datetime, timedelta

CACHE_FILE = "dump_words_cache.pkl"


# TODO: add filter for the unnecessary entries
class JDMWordsStore(CachedStore):
    def __init__(self):
        super().__init__(cache_file=CACHE_FILE)

    def _get_process_data(self, *args, **kwargs) -> dict:
        return self._fetch_new_data(*args, **kwargs)

    def _update_and_cache(self, word: str, data: dict):
        self.data[word] = data
        self.last_updated = datetime.now()
        self._save_cache()

    def _fetch_new_data(self, word: str = None) -> dict:
        if word is None:
            return {}
        URL = (
            "https://www.jeuxdemots.org/rezo-dump.php?gotermsubmit=Chercher&gotermrel="
            + word.replace(" ", "+")
            + "&rel=?gotermsubmit=Chercher&gotermrel="
            + word.replace(" ", "+")
            + "&rel="
        )
        nt_pattern = re.compile(r"nt;(\d+);'([^']*)'")
        e_pattern = re.compile(r"e;(\d+);'([^']+)';(\d+);(\d+)(?:;'([^']+)')?")
        r_pattern = re.compile(r"r;(\d+);(\d+);(\d+);(\d+);(\d+);([\d.]+);(\d+)")
        rt_pattern = re.compile(
            r"rt;(\d+);'([^']+)';'([^']+)';(.*?)(?=rt;|//|$)", re.DOTALL
        )
        try:
            response = requests.get(URL, stream=True)
            response.raise_for_status()
        except requests.RequestException as e:
            print(e)
            raise Exception("Failed to fetch compound words")
        word_dump = {}
        word_dump["eid"] = ""
        word_dump["nt"] = []
        word_dump["e"] = []
        word_dump["r"] = []
        word_dump["rt"] = []
        for line in tqdm(
            response.iter_lines(),
            desc="Downloading content...",
        ):
            if line:
                if "(eid=" in line.decode("latin-1"):
                    eid = line.decode("latin-1").split("eid=")[1].split(")")[0]
                    word_dump["eid"] = eid
                nt = nt_pattern.match(line.decode("latin-1"))
                if nt:
                    word_dump["nt"].append(nt.groups())
                e = e_pattern.match(line.decode("latin-1"))
                if e:
                    word_dump["e"].append(e.groups())
                r = r_pattern.match(line.decode("latin-1"))
                if r:
                    word_dump["r"].append(r.groups())
                rt = rt_pattern.match(line.decode("latin-1"))
                if rt:
                    word_dump["rt"].append(rt.groups())
        print("Data fetched successfully")
        return word_dump

    @property
    def word(self):
        return self.get_data()
