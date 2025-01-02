import requests
from tqdm import tqdm
import re
from .cached_store import CachedStore
from datetime import datetime

CACHE_FILE = "dump_words_cache.pkl"


# TODO: add filter for the unnecessary entries
class JDMWordsStore(CachedStore):
    def __init__(self):
        super().__init__(cache_file=CACHE_FILE)

    def _get_process_data(self) -> dict:
        return {}

    def _update_and_cache(self, word: str, data: dict):
        self.data[word] = data
        self.last_updated = datetime.now()
        self._save_cache()

    @staticmethod
    def _fetch_data(word: str) -> dict:
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
        word_dump = {"eid": "", "nt": [], "e": [], "r": [], "rt": []}
        for line in tqdm(
            response.iter_lines(),
            desc=f"Getting word dump for {word} from jdm...",
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
                    second_group = e.groups()[1]
                    # check if the second group contain : > or en: or an: or bn: or :r or wiki: umls: or dbnary:, if so skip
                    if (
                        ">" in second_group
                        or "en:" in second_group
                        or "an:" in second_group
                        or "bn:" in second_group
                        or ":r" in second_group
                        or "wiki:" in second_group
                        or "umls:" in second_group
                        or "dbnary:" in second_group
                    ):
                        continue
                    word_dump["e"].append(e.groups())
                r = r_pattern.match(line.decode("latin-1"))
                if r:
                    word_dump["r"].append(r.groups())
                rt = rt_pattern.match(line.decode("latin-1"))
                if rt:
                    word_dump["rt"].append(rt.groups())
        return word_dump

    def fetch_new_data(self, data: str | list[str]) -> None:
        if isinstance(data, str) and data in self.data:
            new_data = self._fetch_data(data)
            self._update_and_cache(data, new_data)
        else:
            for word in data:
                if word in self.data:
                    continue
                new_data = self._fetch_data(word)
                self._update_and_cache(word, new_data)

    @property
    def word(self):
        return self.get_data()
