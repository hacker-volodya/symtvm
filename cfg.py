import networkx as nx
import matplotlib.pyplot as plt
import pydot
from networkx.drawing.nx_pydot import graphviz_layout


def build_graph(graph):
    g = nx.DiGraph()
    qaddr = lambda s: '"' + s.addr() + '"'
    for (from_s, to_s, symbol) in graph:
        if symbol == 's':
            g.add_node(qaddr(from_s), color='black')
            g.add_node(qaddr(to_s), color='black')
            g.add_edge(qaddr(from_s), qaddr(to_s), symbol=symbol)
        elif symbol == 'e' or symbol == 'eu':
            e = f"\"{from_s.addr()}: {to_s.exception}\""
            g.add_node(e, color='red' if symbol == 'e' else 'gray')
            g.add_edge(qaddr(from_s), e, symbol=symbol)
        elif symbol == 'u':
            g.add_edge(qaddr(from_s), qaddr(to_s), symbol=symbol)
            g.add_node(qaddr(to_s), color='gray')
        elif symbol == 'f':
            g.add_node(qaddr(from_s), color='green')

    pos = graphviz_layout(g, prog="dot")

    node_colors = [d["color"] for _, d in g.nodes(data=True)]
    nx.draw_networkx(g, pos=pos, node_color=node_colors, with_labels=False, node_size=10)
    # elabels = {(u, v): l for u, v, l in g.edges(data="symbol")}
    # nx.draw_networkx_edge_labels(g, pos, edge_labels=elabels)
    plt.show()
