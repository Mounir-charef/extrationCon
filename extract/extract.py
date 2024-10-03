import networkx as nx
from typing import List
import matplotlib.pyplot as plt


class Extractor:
    def __init__(self):
        self._graph = nx.Graph()
        self._words: List[str] = []

    def _process(self, phrase: str, *, sep=" ") -> None:
        assert phrase, "The phrase is empty"
        self._words = phrase.split(sep)

        self._graph.add_nodes_from(self._words)
        self._graph.add_node("T")
        self._graph.add_node("⊥")

        if not self._words:
            raise Exception("No words founds")
        self._graph.add_edge("T", self._words[0], label="r_succ")
        self._graph.add_edge(self._words[-1], "⊥", label="r_succ")

        for index in range(len(self._words) - 1):
            self._graph.add_edge(
                self._words[index], self._words[index + 1], label="r_succ"
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

    def __call__(self, phrase: str, *, sep=" "):
        self._process(phrase, sep=sep)
