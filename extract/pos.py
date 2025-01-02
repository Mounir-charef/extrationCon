from .cached_store import CachedStore

CACHE_FILE = "pos_cache.pkl"


class PosResolver(CachedStore):
    def __init__(self):
        super().__init__(cache_file=CACHE_FILE)

    def _get_process_data(self) -> dict:
        return self.fetch_data()

    @staticmethod
    def fetch_data() -> dict:
        pass
