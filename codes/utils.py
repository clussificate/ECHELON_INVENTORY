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
    # lead_times.insert(0, 0)
    holding_costs = holding_costs[1:]
    conf = ConfigX()
    unit_demand = conf.mu * conf.lam
    total_installations = len(base_stocks)

    def cal_cost_recursion(res, i):
        if i != total_installations - 1:
            print("current i:{}".format(i))
            print("current x: {}".format(res))
            echelon_cost = holding_costs[i]
            lead_time = lead_times[i]
            print("current echelon holding cost: {}".format(echelon_cost))
            print("current lead time: {}".format(lead_time))

            lead_time_demand = unit_demand * lead_time
            net_inventory = res - lead_time_demand  # y - D_i

            next_res = min(net_inventory, base_stocks[i + 1])
            current_cost = echelon_cost * net_inventory + cal_cost_recursion(next_res, i + 1)
            return current_cost
        else:
            echelon_cost = holding_costs[i]
            installation_cost = sum(holding_costs)  # local holding cost of the most downstream node.
            lead_time = lead_times[i]
            lead_time_demand = unit_demand * lead_time
            print("current i:{}".format(i))
            print("current x: {}".format(res))
            print("current echelon holding cost: {}".format(echelon_cost))
            print("current installation holding cost: {}".format(installation_cost))
            print("current lead time: {}".format(lead_time))
            return echelon_cost * lead_time_demand + (installation_cost + penalty_cost) * max(-res, 0)

    total_cost = cal_cost_recursion(base_stocks[0], 0)
    return total_cost


if __name__ == "__main__":
    """
    @ example: four stages serial system with L=0.25, h=2.5, lambda=16, see Song(2003) table 6. 
               the leaf node is a dummy node with lead time=0 and echelon holding cost = 0.001
     """

    lead_time_list = [0.25, 0.25, 0.25, 0.25, 0]
    echelon_holding_cost_list = [0.0001, 2.5, 2.5, 2.5, 0.25]
    base_stock_list = [25, 18, 14, 8]  # omit the dummy leaf node
    penalty_cost = 99
    total_cost = policy_evaluation(base_stocks=base_stock_list, holding_costs=echelon_holding_cost_list,
                                   lead_times=lead_time_list, penalty_cost=99)
    print("Total cost of base stock {} is: {} ".format(base_stock_list, total_cost))
