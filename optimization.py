from .booking import AnalysisFlowUnit

from .utils import Node

import logging
logger = logging.getLogger(__name__)



class Graph(Node):
    """
    A Graph is itself a node and every node has other nodes as children.
    Due to the way it is constructed, the root node will always be of
    kind 'dataset'.

    Args:
        analysis_flow_unit (AnalysisFlowUnit): analysis flow unit
            object from which a graph in its basic form is generated
    """
    def __init__(self, afu = None):
        if afu:
            Node.__init__(self,
                afu.dataset.name,
                'dataset',
                afu.dataset)
            nodes = self.__nodes_from_afu(afu)
            for no_last, no_first in zip(
                    nodes[:-1], nodes[1:]):
                no_last.children.append(no_first)
            self.children.append(nodes[0])
            logger.debug('%%%%%%%%%% Constructing graph from AFU')

    def __nodes_from_afu(self, afu):
        nodes = []
        for selection in afu.selections:
            nodes.append(
                Node(
                    selection.name,
                    'selection',
                    selection))
        nodes.append(
            Node(
                afu.action.name,
                'action',
                afu.action))
        return nodes


class GraphManager:
    """
    Manager for Graph-type objects, with the main function of
    optimize/merge them with the 'optimize' function.

    Args:
        analysis_flow_units (list): List of AnalysisFlowUnit
            objects used to fill the 'graphs' attribute

    Attributes:
        graphs (list): List of Graph objects that at some point
            will be merged and optimized
    """
    def __init__(self, analysis_flow_units):
        self.graphs = [
            Graph(unit) \
                for unit in analysis_flow_units]

    def add_graph(self, graph):
        self.graphs.append(graph)

    def add_graph_from_afu(self, afu):
        self.graphs.append(Graph(afu))

    def optimize(self):
        self.merge_datasets()

    def merge_datasets(self):
        logger.debug('%%%%%%%%%% Merging datasets:')
        merged_graphs = list()
        for graph in self.graphs:
            if graph not in merged_graphs:
                merged_graphs.append(graph)
            else:
                for merged_graph in merged_graphs:
                    if merged_graph == graph:
                        for child in graph.children:
                            merged_graph.children.append(child)
        # Debug
        def print_merged_graphs():
            logger.debug('%%%%%%%%%% Merging datasets: DONE')
            print('Merged graphs:')
            for graph in merged_graphs:
                print(graph)
        print_merged_graphs()

        self.graphs = merged_graphs
