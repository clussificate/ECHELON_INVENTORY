# -*- coding: utf-8 -*-
"""
@Created at 2020/6/26 13:22
@Author: Kurt
@file:utils.py
@Desc:
"""
import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import write_dot, graphviz_layout
from copy import deepcopy


class NodeTypeException(Exception):
    def __init__(self):
        err = 'Incorrect Node Types. Leaf nodes have no predecessors, and root nodes have no successors'
        Exception.__init__(self, err)


class TreeTypeException(Exception):
    def __init__(self):
        err = 'Incorrect Tree Types. you must input a serial system.'
        Exception.__init__(self, err)


class InfoMissException(Exception):
    def __init__(self):
        err = 'Miss echelon holding costs, recalculate by setting mode=0.'
        Exception.__init__(self, err)


class Queue:
    def __init__(self):
        self.list = []

    def isEmpty(self):
        return self.list == []

    def push(self, data):
        self.list.append(data)

    def pop(self):
        if self.isEmpty():
            return False
        return self.list.pop(0)


class Stack:
    def __init__(self):
        self.list = list()

    def isEmpty(self):
        return self.list == []

    def push(self, data):
        self.list.append(data)

    def pop(self):
        if self.isEmpty():
            return False
        return self.list.pop()


# utils
def get_all_predecessors(node):
    """
    obtain all predecessors, including indirect predecessors
    """
    all_predecessors = []
    stack = Stack()
    stack.push(node)
    # DepthFirst Search
    while not stack.isEmpty():
        node = stack.pop()
        all_predecessors.append(node)
        predecessors = node.predecessors
        predecessors = reversed(predecessors)  # in order to obtain leaf-first-right-sencond sequence
        for predecessor in predecessors:
            stack.push(predecessor)

    return all_predecessors[1:]  # remove the first node


def get_all_successors(node):
    """
    obtain all predecessors, including indirect successors
    """
    all_successors = []
    while node:
        all_successors.append(node)
        node = node.successor
    return all_successors[1:]  # remove the first node


def BOM_plot(BOM):
    """
    Given a BOM structure, draw its network.
    """
    nodes = list(BOM.nodes.keys())
    nodes.append("customer")
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    labels = {}
    G.add_edge(BOM.root.number, "customer", len=BOM.root.lead_time)
    #     G.add_edge(BOM.root.number, "customer" ,minlen=BOM.root.lead_time)

    labels[(BOM.root.number, "customer")] = BOM.root.lead_time

    queue = Queue()
    queue.push(BOM.root)

    while not queue.isEmpty():
        current_node = queue.pop()
        preds = current_node.predecessors
        for pred in preds:
            G.add_edge(pred.number, current_node.number, len=pred.lead_time)
            #             G.add_edge(pred.number, current_node.number, minlen = pred.lead_time)
            labels[(pred.number, current_node.number)] = pred.lead_time
            # print("lead_time: {}".format(pred.lead_time))
            queue.push(pred)

    write_dot(G, 'test.dot')
    pos = graphviz_layout(G, prog='dot')
    nx.draw(G, pos, with_labels=True, font_weight='bold')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

    #     pos =  nx.spring_layout(G)
    #     nx.draw(G, pos, with_labels=True, font_weight='bold')
    #     nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

    plt.show()


def policy_evaluation(base_stocks, holding_costs, lead_times, penalty_cost):
    """
    :param penalty_cost: backorder cost at the most downstream installation
    :param base_stocks: list of installation base stock
    :param holding_costs: list of installation holding cost
    :param lead_times:list of installation lead time
    :return: total cost
    """

    pass





