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
import numpy as np
import seaborn as sns
import pickle
import datetime
from Config import ConfigX


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


class BCMethodException(Exception):
    def __init__(self):
        err = 'Methods to calculate bounds only allows "approximation" and "simulation".'
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


def quantile_table(demands, decimal):
    """
    :param demands
    :param decimal
    :return: quantile table
    """
    quantile_table = {}
    solve_quantile = np.quantile

    quantile_points = np.around(np.concatenate((np.arange(0, 1, 1 / (10 ** decimal)), [1])), decimal)
    quantiles = solve_quantile(demands, quantile_points)
    quantile_table = dict(zip(quantile_points, quantiles))

    return quantile_table


def CDFsimulation(lamda, parameters, decimal=4, distrib="normal", n_sample=20000):
    """
     parameters and distrib:
    - beta: a, b
    - gamma: alpha, lamda
    - normal: loc, scale
    - uniform: low, high
    - exponential: scale
    """

    machine = ""
    arrivals = np.random.poisson(lamda, n_sample)
    print("Distribution: {}".format(distrib))
    if distrib == "normal":
        machine = np.random.normal
    if distrib == "uniform":
        machine = np.random.uniform
    if distrib == "beta":
        machine = np.random.beta
    if distrib == "gamma":
        machine = np.random.gamma
    if distrib == "exp":
        machine = np.random.exponential
        parameters = [parameters[0]]

    demands = []
    for arrival in arrivals:
        count = 0
        if arrival == 0:
            demands.append(count)
        else:
            samples = machine(*parameters, arrival)
            demands.append(np.sum(samples))

    quantile = quantile_table(demands, decimal)

    return quantile


def inverse_compound(quantile, lamda, parameters,
                     distrib="normal", n_sample=20000, show=False):
    """
     parameters and distrib:
    - beta: a, b
    - gamma: alpha, lamda
    - normal: loc, scale
    - uniform: low, high
    - exponential: scale
    """
    arrivals = np.random.poisson(lamda, n_sample)

    print("Distribution: {}".format(distrib))
    if distrib == "normal":
        machine = np.random.normal
    if distrib == "uniform":
        machine = np.random.uniform
    if distrib == "beta":
        machine = np.random.beta
    if distrib == "gamma":
        machine = np.random.gamma
    if distrib == "exp":
        machine = np.random.exponential
        parameters = [parameters[0]]

    demands = []
    for arrival in arrivals:
        count = 0
        if arrival == 0:
            demands.append(count)
        else:
            samples = machine(*parameters, arrival)
            demands.append(np.sum(samples))
    sns.distplot(demands)

    if quantile < 0:
        quantile = 0
    if quantile > 1:
        quantile = 1
    plt.scatter([np.quantile(demands, quantile)], [0], s=[100], c='r', marker='o')
    if show:
        plt.show()
    return np.quantile(demands, quantile)


if __name__ == "__main__":
    print("Simulation begin .........")
    start = datetime.datetime.now()
    CLjs = [6, 6, 5, 4, 0]
    conf = ConfigX()
    lam = conf.lam
    method = "simulation"
    quantile = {}
    params = conf.parameters
    dec = conf.decimal

    if method == "simulation":
        for clj in set(CLjs):
            print("Current processing cumulative lead time: {}".format(clj))
            quantile[clj * lam] = CDFsimulation(clj * lam, params, dec)
    print("Simulation done .........")
    print("Simulation run time: {}".format(datetime.datetime.now() - start))
    with open("simulation_table", "wb") as f:
        pickle.dump(quantile, f)

    with open("simulation_table", "rb") as f:
        data = pickle.load(f)
    print(data[0])
