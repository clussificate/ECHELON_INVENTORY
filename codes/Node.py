# -*- coding: utf-8 -*-
"""
@Created at 2020/6/26 15:33
@Author: Kurt
@file:Node.py
@Desc:
"""
from utils import *


class Node:
    __slots__ = ('lead_time', 'holding_cost', 'successor', 'predecessors',
                 'number', 'label', 'echelon_holding_cost', 'total_lead_time')

    def __init__(self, lead_time, holding_cost, number=None, successor=None,
                 predecessors=None, echelon_holding_cost=None, total_lead_time=None, label=None):
        """

        :param lead_time: lead-time of the item shipped to its successor.
        :param holding_cost: installation holding cost
        :param number: original sequence
        :param echelon_holding_cost: echelon holding cost
        :param total_lead_time: total lead-time for the item and all its successors
        :param label: sequence after labeling procedure
        """

        if predecessors is None:
            predecessors = []
        self.lead_time = lead_time
        self.holding_cost = holding_cost
        self.successor = successor
        self.predecessors = predecessors
        self.number = number
        self.label = label
        self.echelon_holding_cost=echelon_holding_cost
        self.total_lead_time = total_lead_time


class Leaf(Node):
    """
    A leaf node is a most upstream component,
    and is supplied from a outside supplier.
    """

    def __init__(self, lead_time, holding_cost, number=None, successor=None):
        super().__init__(lead_time, holding_cost, number, successor, None)
        if self.predecessors:
            raise NodeTypeException()


class Root(Node):
    """
    A root node is a final product for the assembly system, and
    supplies to customers.
    """

    __slots__ = ("penalty_cost")

    def __init__(self, lead_time, holding_cost, penalty_cost, number=None, predecessors=None):
        if predecessors == None:
            predecessors = []
        super().__init__(lead_time, holding_cost, number, None, predecessors)
        self.penalty_cost = penalty_cost
        if self.successor:
            raise NodeTypeException()
