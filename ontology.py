# Minimal ontology schema for papers, techniques, and results

from typing import List, Tuple, Any
from pyvis.network import Network

# Entity base class
class Entity:
    def __init__(self, name: str):
        self.name = name
    def __repr__(self):
        return f"{self.__class__.__name__}('{self.name}')"

# Paper entity
class Paper(Entity):
    def __init__(self, name: str, year: int):
        super().__init__(name)
        self.year = year
        self.techniques: List['Technique'] = []
        self.results: List['Result'] = []
    def add_technique(self, technique: 'Technique'):
        self.techniques.append(technique)
    def add_result(self, result: 'Result'):
        self.results.append(result)
    def __repr__(self):
        return f"Paper(name='{self.name}', year={self.year})"

# Technique entity
class Technique(Entity):
    def __init__(self, name: str):
        super().__init__(name)
    def __repr__(self):
        return f"Technique('{self.name}')"

# Result entity
class Result(Entity):
    def __init__(self, metric: str, value: Any, dataset: str = None):
        name = f"{metric}: {value}" + (f" on {dataset}" if dataset else "")
        super().__init__(name)
        self.metric = metric
        self.value = value
        self.dataset = dataset
    def __repr__(self):
        return f"Result(metric='{self.metric}', value={self.value}" + (f", dataset='{self.dataset}'" if self.dataset else "") + ")"

# Relationship as a triplet (subject, predicate, object)
class Relationship:
    def __init__(self, subject: Entity, predicate: str, obj: Entity):
        self.subject = subject
        self.predicate = predicate
        self.obj = obj
    def __repr__(self):
        return f"({self.subject}, '{self.predicate}', {self.obj})"

# Example instantiation

# Techniques
seq2seq = Technique("Seq2Seq with Attention")
deep_lstm = Technique("Deep LSTM")
transformer_arch = Technique("Transformer Architecture")

# Papers
gnmt = Paper("GNMT: Google's Neural Machine Translation System", 2016)
transformer = Paper("Attention Is All You Need", 2017)

# Results
gnmt_bleu = Result("BLEU", 24.6, "WMT En->Fr")
transformer_bleu = Result("BLEU", 28.4, "WMT En->Fr")

# Associate techniques/results to papers
gnmt.add_technique(seq2seq)
gnmt.add_technique(deep_lstm)
gnmt.add_result(gnmt_bleu)

transformer.add_technique(transformer_arch)
transformer.add_result(transformer_bleu)

# Relationships (triplets)
triplets: List[Relationship] = [
    Relationship(gnmt, "uses_technique", seq2seq),
    Relationship(gnmt, "uses_technique", deep_lstm),
    Relationship(gnmt, "reports_result", gnmt_bleu),
    Relationship(transformer, "uses_technique", transformer_arch),
    Relationship(transformer, "reports_result", transformer_bleu),
]

# Print example triplets
if __name__ == "__main__":
    for t in triplets:
        print(t)

    import networkx as nx
    import matplotlib.pyplot as plt

    def visualize(triplets):
        G = nx.DiGraph()
        for rel in triplets:
            subj = rel.subject.name
            pred = rel.predicate
            obj = rel.obj.name
            G.add_node(subj)
            G.add_node(obj)
            G.add_edge(subj, obj, label=pred)

        pos = nx.spring_layout(G, seed=42)
        plt.figure(figsize=(12,8))
        nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=3000, font_size=10, font_weight='bold', arrowsize=20)
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', font_size=9)
        plt.title("Ontology Relationships Visualization")
        plt.axis('off')
        plt.show()

    def visualize_interactive(triplets, output="graph.html"):
        net = Network(directed=True)
        nodes_added = set()
        for rel in triplets:
            subj = rel.subject.name
            obj = rel.obj.name
            pred = rel.predicate
            if subj not in nodes_added:
                net.add_node(subj, label=subj)
                nodes_added.add(subj)
            if obj not in nodes_added:
                net.add_node(obj, label=obj)
                nodes_added.add(obj)
            net.add_edge(subj, obj, label=pred)
        net.show(output)

    visualize(triplets)
    visualize_interactive(triplets)