import networkx as nx
from typing import List
import matplotlib.pyplot as plt
from .compount_words import CompoundWordsCache
import re


class Extractor:
    def __init__(self):
        self._graph = nx.Graph()
        self._words: List[str] = []
        self._pattern = re.compile(r"(\S+)'(\S+)|(\S+)")

        self._compound_words_store = CompoundWordsCache()

    def _tokenizer(self, text) -> List[str]:
        tokens = self._pattern.findall(text)
        tokens = [token for match in tokens for token in match if token]
        return tokens

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

        # Add compound words
        for compound_word in self._compound_words_store.compound_words:
            if compound_word not in phrase:
                continue
            words = self._tokenizer(compound_word)

            # Check if the compound word is in the phrase in the correct order
            if all(word in self._words for word in words) and all(
                self._words.index(words[i]) < self._words.index(words[i + 1])
                for i in range(len(words) - 1)
            ):
                self._graph.add_node(compound_word)
                first_index = self._words.index(words[0])
                last_index = self._words.index(words[-1])
                self._graph.add_edge(
                    self._words[first_index],
                    compound_word,
                    label="r_compound",
                )
                self._graph.add_edge(
                    compound_word,
                    self._words[last_index],
                    label="r_compound",
                )

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

    def __call__(self, phrase: str):
        self._process(phrase)
