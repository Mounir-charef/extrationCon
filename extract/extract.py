# import networkx as nx

class Extractor:
    def __init__(self):
        self._graph = None
        self.words: [str] = None


    def _process(self, phrase: str, *, sep=" ") -> None:
        self.words = phrase.split(sep)


    def __call__(self, phrase, *, sep=" "):
        return self._process(phrase, sep=sep)