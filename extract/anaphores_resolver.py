import networkx as nx


class AnaphoresResolver:
    def __init__(self, graph: nx.Graph):
        """
        Initialize the resolver with the graph and disambiguation store.
        :param graph: The graph representing the text.
        """
        self.graph = graph

    def resolve_anaphores(self):
        """
        Resolve anaphores in the graph by linking pronouns to their most likely antecedents.
        """
        antecedents = self._find_antecedents()
        pronouns = self._find_pronouns()

        for pronoun in pronouns:
            # Find the best antecedent for the pronoun
            best_antecedent = None
            best_score = float('-inf')

            for article, antecedent in antecedents.items():
                score = self._score_antecedent(antecedent, pronoun)
                if score > best_score:
                    best_antecedent = antecedent
                    best_score = score

            if best_antecedent:
                # Link the pronoun to the best antecedent
                self.graph.add_edge(pronoun, best_antecedent, label="r_reference")

    def _find_antecedents(self):
        """
        Identify potential antecedents in the graph.
        :return: List of antecedent nodes.
        """
        articles = {
            "le",
            "la",
            "les",
            "l",
            "un",
            "une",
            "des",
            "du",
            "de la",
            "de l",
            "de les",
        }

        # the antecedent is next word in the graph with relation of "r_succ"
        antecedents = {}
        for node in self.graph.nodes:
            if node in articles:
                for neighbor in self.graph.neighbors(node):
                    if self.graph[node][neighbor]["label"] == "r_succ":
                        antecedents[node] = neighbor
        print(antecedents)
        return antecedents

    def _find_pronouns(self):
        """
        Identify pronouns in the graph.
        :return: List of pronoun nodes.
        """
        pronouns = {"il", "elle", "ils", "elles", "le", "la", "les", "lui", "leur"}
        return [node for node in self.graph.nodes if node in pronouns]

    def _score_antecedent(self, antecedent, pronoun):
        # TODO: Improve the scoring function
        """
        Score the antecedent based on its distance from the pronoun.
        :param antecedent: The potential antecedent node.
        :param pronoun: The pronoun node.
        :return: The score of the antecedent.
        """
        return 1 / (1 + nx.shortest_path_length(self.graph, source=antecedent, target=pronoun))
