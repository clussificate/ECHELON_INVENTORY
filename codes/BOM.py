# -*- coding: utf-8 -*-
"""
@Created at 2020/6/26 15:29
@Author: Kurt
@file:BOM.py
@Desc:
"""
from Node import *
import collections
from utils import Queue
from copy import deepcopy


class BOMSerial:
    """
    Serial system
    @nodes: nodes indexed by number
    @labeled_nodes: nodes indexed by label
    """
    __slots__ = ('root', "leaves", "nodes", 'labeled_nodes',
                 'number_to_label', 'label_to_number')

    def __init__(self):
        self.root = None
        self.leaves = []
        self.nodes = {}
        self.labeled_nodes = collections.OrderedDict()
        self.number_to_label = {}
        self.label_to_number = {}

    def generate_labels(self):
        """
        :return: generate labels for serial systems.
                 start with label 0, which means the most downstream installation
        """
        self.labeled_nodes.clear()
        self.number_to_label.clear()
        self.label_to_number.clear()
        self.nodes.clear()

        current_node = self.root
        i = 0

        while current_node:
            current_node.label = str(i)
            self.nodes[str(current_node.number)] = current_node
            self.labeled_nodes[str(i)] = current_node
            self.label_to_number[str(i)] = str(current_node.number)
            self.number_to_label[str(current_node.number)] = str(i)
            if current_node.predecessors:
                current_node = current_node.predecessors[0]
            else:
                break
            i += 1

    def __len__(self):
        """
        return # of all nodes
        """
        return len(self.nodes)

    def __getitem__(self, label):
        """
        :param: label - str type
        get the node by its label (i.e. sequence after labeling procedure)
        """
        return self.labeled_nodes[label]


class BOMTree(BOMSerial):
    """
    Assembly system
    """
    __slots__ = ()

    def __init__(self, NodeJson=None):
        super().__init__()
        if NodeJson:
            self.generate_tree(NodeJson)

    def generate_tree(self, NodeJson):
        """
        Generating the assembly system
        """
        # BreadthFist
        queue = Queue()
        root_json = NodeJson[NodeJson['root']]  # get root node json
        root = Root(lead_time=root_json["lead_time"], penalty_cost=root_json["penalty_cost"],
                    holding_cost=root_json["holding_cost"], number=str(root_json["number"]))
        queue.push(root)
        #         print(queue.list[0])
        self.root = root

        print("---------BFS for generating assembly network: begin.------------")

        while not queue.isEmpty():

            current_node = queue.pop()
            print("Process node number: {} ".format(current_node.number))
            self.nodes[str(current_node.number)] = current_node
            #             print(current_node.number)
            node_json = NodeJson[int(current_node.number)]  # get root node json

            if node_json["predecessors"]:  # non-leaf node
                predecessors_cost = 0
                for predecessor_number in node_json["predecessors"]:
                    predecessor_json = NodeJson[predecessor_number]
                    predecessor = Node(lead_time=predecessor_json["lead_time"],
                                       holding_cost=predecessor_json["holding_cost"],
                                       number=str(predecessor_json["number"]))
                    self.nodes[str(predecessor.number)] = predecessor.number
                    predecessors_cost += predecessor.holding_cost

                    current_node.predecessors.append(predecessor)
                    predecessor.successor = current_node

                    queue.push(predecessor)

                # update echelon holding cost
                current_node.echelon_holding_cost = current_node.holding_cost - predecessors_cost

            else:  # get a leaf node
                current_node.echelon_holding_cost = current_node.holding_cost
                self.leaves.append(current_node)

        print("---------BFS for generating assembly network: done.------------")

        self.leaf_warpper()  # transform to leaf type for all leaves

    def leaf_warpper(self):
        for idx, leaf in enumerate(self.leaves):
            self.leaves[idx] = Leaf(lead_time=leaf.lead_time, echelon_holding_cost=leaf.echelon_holding_cost,
                                    holding_cost=leaf.holding_cost, number=leaf.number,
                                    successor=leaf.successor)

    def calc_total_lead_time(self):
        """
        Caculate total lead-time for item i and all its successors
        """
        stack = Stack()
        self.root.total_lead_time = self.root.lead_time
        stack.push(self.root)
        print("----------------DFS for total lead times: begin.---------------")
        while not stack.isEmpty():
            node = stack.pop()

            total_lead_time = node.total_lead_time
            print("Process node number: {}, total_lead_time:{}".format(node.number, node.total_lead_time))

            # stack
            predecessors = node.predecessors
            predecessors = reversed(predecessors)  # in order to obtain leaf-first-right-sencond sequence
            for predecessor in predecessors:
                predecessor.total_lead_time = predecessor.lead_time + total_lead_time
                stack.push(predecessor)
        print("----------------DFS for total lead times: done.---------------")

    def generate_labels(self):
        """
        Generate node labels by a labeling procedure,
        which sorts all nodes from smallest to largest by their total lead times.
        """
        self.label_to_number.clear()
        self.number_to_label.clear()
        self.labeled_nodes.clear()

        sorted_nodes = sorted(self.nodes.items(), key=lambda item: item[1].total_lead_time)
        i = 0
        for number, node in sorted_nodes:
            node.label = str(i)
            self.labeled_nodes[str(i)] = node
            self.number_to_label[number] = str(i)
            self.label_to_number[str(i)] = number
            i += 1

    def transform_to_serial_default(self):
        """
         Assumption:
            all echelon holding costs are positive which realizes the Long-Run Balance (see. Kaj Rosling et al.1989)
        :return:
        """
        self.calc_total_lead_time()  # calculate total lead time for each node
        self.generate_labels()  # generate labels by a labeling procedure

        serial = BOMSerial()
        serial.nodes = self.nodes
        serial.labeled_nodes = self.labeled_nodes
        serial.number_to_label = self.number_to_label
        serial.label_to_number = self.number_to_label

        ordered_nodes = list(self.labeled_nodes.values())  # ordered by total lead times
        root = ordered_nodes[0]
        current_node = root
        serial.root = Root(lead_time=root.lead_time, echelon_holding_cost=root.echelon_holding_cost,
                           holding_cost=root.holding_cost, penalty_cost=root.penalty_cost, number=root.number)
        serial.root.label = root.label
        serial_current_node = serial.root

        for idx, next_node in enumerate(ordered_nodes[1:]):
            print("Next node:{}".format(next_node.number))
            equivalent_lead_time = next_node.total_lead_time - current_node.total_lead_time
            #             print("equivalent_lead_time",equivalent_lead_time)

            serial_next_node = Node(lead_time=equivalent_lead_time, successor=serial_current_node,
                                    holding_cost=next_node.holding_cost,
                                    echelon_holding_cost=next_node.echelon_holding_cost, number=next_node.number)
            serial_next_node.label = next_node.label

            serial_current_node.predecessors.append(serial_next_node)

            #             print("successor:", serial_next_node.successor.number)
            #             print("predecessor:",serial_current_node.predecessors[0].number)

            current_node = next_node
            serial_current_node = serial_next_node
        #             print("ture successor:", serial_current_node.successor.number)
        #             print("-------------------------")

        #         print("Leaf node: {},current node.successor:{}".format(current_node.number,
        #         serial_current_node.successor.number))
        # last node serve as leaf node
        serial.leaves.append(Leaf(lead_time=serial_current_node.lead_time,
                                  echelon_holding_cost=serial_current_node.echelon_holding_cost,
                                  holding_cost=serial_current_node.holding_cost,
                                  successor=serial_current_node.successor,
                                  number=serial_current_node.number))
        serial.leaves[0].label = serial_current_node.label
        return serial

    def transform_to_serial_elim(self):
        """
        Generalized Assumption:  the sum of the echelon holding costs of item i and all its predecessors are positive
                                 (see. Kaj Rosling et al.1989)
        :return: serial system which eliminates all nodes with negative echelon holding cost
        """

        self.nodes.clear()  # clear nodes information
        self.leaves.clear()  # reset leaf node

        stack = Stack()
        stack.push(self.root)
        while not stack.isEmpty():
            current_node = stack.pop()

            # aggregating until echelon holding cost of the current node greater than 0
            # it means that we may aggregate several nodes.
            while current_node.echelon_holding_cost <= 0 and current_node.predecessors:
                predecessors = current_node.predecessors
                ehcs = [x.echelon_holding_cost for x in predecessors]
                ind = ehcs.index(min(ehcs))  # index of the predecessor with minimal echelon holding cost
                merge_node = predecessors[ind]
                current_node.number = current_node.number + ',' + merge_node.number
                current_node.echelon_holding_cost = current_node.echelon_holding_cost + \
                                                    merge_node.echelon_holding_cost
                current_node.lead_time = current_node.lead_time + merge_node.lead_time

                current_node.holding_cost = None

                for i, pre in enumerate(predecessors):
                    if i != ind:
                        pre.lead_time = pre.lead_time - merge_node.lead_time

                current_node.predecessors.extend(merge_node.predecessors)
                current_node.predecessors.remove(merge_node)

            if current_node.predecessors is None:  # reach the leaf node
                self.leaves.append(current_node)

            for predecessor in current_node.predecessors:
                predecessor.successor = current_node
                stack.push(predecessor)

            self.nodes[current_node.number] = current_node    # update current node

        self.leaf_warpper()
        serial = self.transform_to_serial_default()
        return serial

    def transform_to_serial(self, mode=0):
        """
        Generate a equivalent serial system.
        :param: mode: default 0, for positive echelon holding cost assumption.
                          other, for generalized assumption (see. Kaj Rosling et al.1989)
        """
        print("----------Generate equivalent serial system: begin.......-------------")
        if mode == 0:
            serial = self.transform_to_serial_default()
        else:
            serial = self.transform_to_serial_elim()
        print("--------Generate equivalent serial system: done!-----------")
        return serial


def serial_merge(serial):
    """
    :return: serial system which merges zero lead time nodes.
    """
    serial = deepcopy(serial)

    if not isinstance(serial, BOMSerial):
        raise TreeTypeException()

    # Also note that, the lead time of the source node to root must not equal to 0 for assembly system.
    # due to the specificity of the root node (i.e. penalty cost),
    # we suggest traversal from leaf to node, and even need not to specially treat the root node.
    current_node = serial.leaves[0]

    while current_node:
        successor = current_node.successor
        if successor is None:
            print("Reach the root node, end!")
            break
        #         print("current node: {}".format(current_node.number))
        #         print("successor node: {}".format(successor.number))
        #         print("current lead time: {}".format(current_node.lead_time))
        if current_node.lead_time == 0:
            print("--------find a 0 lead time!--------")
            print("current node: {}".format(current_node.number))
            current_node.echelon_holding_cost = current_node.echelon_holding_cost + successor.echelon_holding_cost
            current_node.holding_cost = None
            current_node.number = current_node.number + "," + successor.number
            current_node.lead_time = successor.lead_time
            current_node.successor = successor.successor
            successor.successor.predecessors = [current_node]

            print("current node change to: {}".format(current_node.number))
            # print("successor: {}".format(current_node.successor.number))
            # print("predecessors: {}".format(current_node.successor.predecessors[0].number))
            print("----------------------------------")

        current_node = current_node.successor

    # recalculate all local holding costs
    print("-----------------recalculate all local holding costs-----------------")
    cum = 0  # Cumulative local holding cost
    current_node = serial.leaves[0]
    while current_node:
        cum = current_node.echelon_holding_cost + cum
        current_node.holding_cost = cum
        current_node = current_node.successor
    serial.generate_labels()  # update label information for serial system (BOMSerial.generate_labels())
    return serial
