import networkx as nx
from typing import List
import matplotlib.pyplot as plt
from .compount_words import CompoundWordsStore
from .disambiguate_terms import DisambiguateTermsStore
from .jdmLoad import JDMWordsStore
from .anaphores_resolver import AnaphoresResolver
import re
import datetime


class Extractor:
    def __init__(self):
        self._graph = nx.Graph()
        self._words: List[str] = []
        self._pattern = re.compile(r"(\S+)'(\S+)|(\S+)", re.IGNORECASE)
        self._punctuation_pattern = re.compile(r"[^\w'-]")
        self._compound_words_store = CompoundWordsStore(
            cache_expiry=datetime.timedelta(days=30)
        )
        self._disambiguate_terms_store = DisambiguateTermsStore()
        self.jdm_words_store = JDMWordsStore()
        self._anaphores_resolver = AnaphoresResolver(self._graph)

    def plot_graph(self):
        pos = nx.spring_layout(self._graph)
        labels = nx.get_edge_attributes(self._graph, "label")

        plt.figure(figsize=(10, 8))
        nx.draw(
            self._graph,
            pos,
            with_labels=True,
            node_size=3000,
            node_color="skyblue",
            font_size=15,
            font_weight="bold",
            edge_color="gray",
        )
        nx.draw_networkx_edge_labels(self._graph, pos, edge_labels=labels)
        plt.title("Graph Visualization")
        plt.show()

    def _tokenizer(self, text) -> List[str]:
        tokens = self._pattern.findall(text)
        # flatten the list
        tokens = [token for match in tokens for token in match if token]
        clean_tokens = [self._punctuation_pattern.sub("", token) for token in tokens]
        return [token for token in clean_tokens if token]

    def _process(self, phrase: str) -> None:
        assert phrase, "The phrase is empty"
        assert isinstance(phrase, str), "The phrase should be a string"

        phrase = phrase.lower()

        self._words = self._tokenizer(phrase)
        self._words.insert(0, "⊤")
        self._words.append("⊥")

        self._graph.add_nodes_from(self._words)

        if not self._words:
            raise Exception("No words founds")

        for index in range(len(self._words) - 1):
            self._graph.add_edge(
                self._words[index], self._words[index + 1], label="r_succ"
            )

        # Add JDM words
        self._get_data_info()

        # Add compound words
        self._find_compound_words(phrase)

        # Resolve disambiguate terms
        self._resolve_disambiguate_terms()

        # Resolve anaphores
        self._anaphores_resolver.resolve_anaphores()

    def _find_compound_words(self, phrase: str) -> None:
        """
        Find compound words in the phrase and add them to the graph as nodes and connect them to the words
        :param phrase: str
        :return: None
        """
        for compound_word in self._compound_words_store.compound_words:
            if compound_word not in phrase:
                continue
            words = self._tokenizer(compound_word)

            start_index = 0
            while start_index < len(self._words):
                try:
                    first_index = self._words.index(words[0], start_index)
                    if all(
                        self._words[first_index + i] == words[i]
                        for i in range(len(words))
                    ):
                        self._graph.add_node(compound_word)
                        last_index = first_index + len(words) - 1

                        if first_index > 0:
                            self._graph.add_edge(
                                self._words[first_index - 1],
                                compound_word,
                                label="r_succ",
                            )
                        if last_index < len(self._words) - 1:
                            self._graph.add_edge(
                                compound_word,
                                self._words[last_index + 1],
                                label="r_succ",
                            )

                        start_index = last_index + 1
                    else:
                        start_index = first_index + 1
                except ValueError:
                    break

    def _resolve_disambiguate_terms(self) -> None:
        """
        Resolve disambiguate terms in the graph by adding the most likely term as a node and connecting the original term to the most likely term
        :return: None
        """
        found_words = list(self._graph.nodes)
        for word in found_words:
            if word in self._disambiguate_terms_store.disambiguate_terms:
                most_likely = sorted(
                    self._disambiguate_terms_store.get_disambiguate_term(word)
                )[-1]
                self._graph.add_node(most_likely[0])
                self._graph.add_edge(word, most_likely[0], label="r_disambiguate")

    def _get_data_info(self) -> None:
        """
        Retrieve data from the JDMWordsStore
        if any word is not in the Store, fetch it and cache it
        else just display the data
        """
        self.jdm_words_store.fetch_new_data(self._words)

    def __call__(self, phrase: str):
        self._process(phrase)
