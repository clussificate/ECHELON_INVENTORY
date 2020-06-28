# -*- coding: utf-8 -*-
"""
@Created at 2020/6/26 15:45
@Author: Kurt
@file:main.py
@Desc:
"""
from Bounds import calc_bounds
from utils import *
from BOM import BOMTree, serial_merge, serial_agg


def assembly_to_serial(Json, mode=0):
    Assembly = BOMTree()
    Assembly.generate_tree(Json)
    serial = Assembly.transform_to_serial()

    serial_node = serial.leaves[0]

    # while serial_node:
    #     print("current node number: {}, lead time:{}, label:{}".format(serial_node.number,
    #                                                                    serial_node.lead_time, serial_node.label))
    #     if serial_node.successor:
    #         print("next node number:{}".format(serial_node.successor.number))
    #     else:
    #         print("Reach root node.")
    #     serial_node = serial_node.successor

    if mode == 0:
        serial2 = serial_merge(serial)
        BOM_plot(Assembly)
        BOM_plot(serial)
        BOM_plot(serial2)
    else:
        serial2 = serial_agg(serial)

    return serial2


if __name__ == "__main__":
    # example:
    """
    number: orginal sequences
    label: sequences after labeling procedure.
    """
    root = {"lead_time": 0, "holding_cost": 0.3, "penalty_cost": 15, "successor": None, "predecessors": [1, 2],
            "number": 0}
    node1 = {"lead_time": 1, "holding_cost": 0.1, "successor": 0, "predecessors": [3, 4], "number": 1}
    node2 = {"lead_time": 4, "holding_cost": 0.3, "successor": 0, "predecessors": [5, 6], "number": 2}
    node3 = {"lead_time": 2, "holding_cost": 0.1, "successor": 1, "predecessors": None, "number": 3}
    node4 = {"lead_time": 3, "holding_cost": 0.3, "successor": 1, "predecessors": None, "number": 4}
    node5 = {"lead_time": 1, "holding_cost": 0.1, "successor": 2, "predecessors": None, "number": 5}
    node6 = {"lead_time": 2, "holding_cost": 0.3, "successor": 2, "predecessors": None, "number": 6}

    Json = {0: root, 1: node1, 2: node2, 3: node3, 4: node4, 5: node5, 6: node6, "leaves": [3, 4, 5, 6], "root": 0}

    serial = assembly_to_serial(Json)
    # print("serial nodes: {}".format(serial.nodes))
    # print("serial successor: {}".format(serial.leaves[0].successor.number))
    normal_lbs, normal_ubs = calc_bounds(serial)
    print("Rounding lower bounds: {}".format(normal_lbs))
    print("Rounding upper bounds: {}".format(normal_ubs))
