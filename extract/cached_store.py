import pickle
from datetime import datetime, timedelta
from pathlib import Path
from abc import ABC, abstractmethod
from typing import TypeVar, Optional

DATA_FOLDER = Path("data")

T = TypeVar("T")


class CachedStore(ABC):
    def __init__(self, cache_file: str, *, cache_expiry: Optional[timedelta] = None):
        self.cache_file = DATA_FOLDER / cache_file
        self._ensure_data_folder()
        self.data: T = None
        self.last_updated: Optional[datetime] = None
        self.CACHE_EXPIRY = cache_expiry or timedelta(days=7)
        self._load_or_fetch()

    @staticmethod
    def _ensure_data_folder():
        if not DATA_FOLDER.exists():
            DATA_FOLDER.mkdir(parents=True)

    def _load_or_fetch(self):
        if not self._load_cache():
            self._fetch_and_cache()

    def _is_cache_expired(self) -> bool:
        if not self.last_updated:
            return True
        return (datetime.now() - self.last_updated) > self.CACHE_EXPIRY

    def _fetch_and_cache(self):
        self.data = self._get_process_data()
        self.last_updated = datetime.now()
        self._save_cache()

    def _save_cache(self):
        with open(self.cache_file, "wb") as f:
            pickle.dump((self.data, self.last_updated), f)

    def _load_cache(self) -> bool:
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "rb") as f:
                    self.data, self.last_updated = pickle.load(f)
                if not self._is_cache_expired():
                    return True
            except EOFError:
                return False
            except pickle.UnpicklingError:
                return False
            except Exception as e:
                print(f"Failed to load cache {self.cache_file}: {e}")
        return False

    def get_data(self) -> T:
        if self._is_cache_expired():
            self._fetch_and_cache()
        return self.data

    @abstractmethod
    def _get_process_data(self) -> T:
        pass
