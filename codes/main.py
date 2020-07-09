# -*- coding: utf-8 -*-
"""
@Created at 2020/6/26 15:45
@Author: Kurt
@file:main.py
@Desc:
"""
import datetime
from Bounds import calc_bounds
from utils import *
from BOM import BOMTree, serial_merge


def assembly_to_serial(Json, mode=0, show=False):
    """
    :param Json:
    :param mode: default 0, no elimination procedure of negative echelon holding costs
                 otherwise, use elimination procedure of negative echelon holding costs
    :return:
    """
    Assembly = BOMTree()
    Assembly.generate_tree(Json)
    if show: BOM_plot(Assembly)
    serial = Assembly.transform_to_serial(mode=mode)
    if show: BOM_plot(serial)
    # serial_node = serial.leaves[0]
    # while serial_node:
    #     print("current node number: {}, lead time:{}, label:{}".format(serial_node.number,
    #                                                                    serial_node.lead_time, serial_node.label))
    #     if serial_node.successor:
    #         print("next node number:{}".format(serial_node.successor.number))
    #     else:
    #         print("Reach root node.")
    #     serial_node = serial_node.successor
    print("-----------Merge zero lead time nodes: begin....------------")
    serial2 = serial_merge(serial)
    print("-----------Merge zero lead time nodes: done!-----------------")
    if show: BOM_plot(serial2)

    return serial2


if __name__ == "__main__":
    # example:
    """
    lead_time: process time of current to its unique successor. 
             (Just suitable for assembly system, note that this is not a classical definition.) 
    number: original sequences
    label: sequences after labeling procedure.
    """
    root = {"lead_time": 0, "holding_cost": 0.7, "penalty_cost": 9, "successor": None, "predecessors": [1, 2],
            "number": 0}
    node1 = {"lead_time": 1, "holding_cost": 0.2, "successor": 0, "predecessors": [3, 4], "number": 1}
    node2 = {"lead_time": 4, "holding_cost": 0.4, "successor": 0, "predecessors": [5, 6], "number": 2}
    node3 = {"lead_time": 2, "holding_cost": 0.1, "successor": 1, "predecessors": None, "number": 3}
    node4 = {"lead_time": 3, "holding_cost": 0.2, "successor": 1, "predecessors": None, "number": 4}
    node5 = {"lead_time": 1, "holding_cost": 0.1, "successor": 2, "predecessors": None, "number": 5}
    node6 = {"lead_time": 2, "holding_cost": 0.2, "successor": 2, "predecessors": None, "number": 6}
    Json = {0: root, 1: node1, 2: node2, 3: node3, 4: node4, 5: node5, 6: node6, "leaves": [3, 4, 5, 6], "root": 0}

    start = datetime.datetime.now()
    serial = assembly_to_serial(Json=Json, mode=1)
    print("Transformation run time: {}".format(datetime.datetime.now()-start))

    # print("serial nodes: {}".format(serial.nodes))
    # print("serial successor: {}".format(serial.leaves[0].successor.number))
    normal_lbs, normal_ubs = calc_bounds(serial, method="simulation")
    print("Rounding lower bounds: {}".format(normal_lbs))
    print("Rounding upper bounds: {}".format(normal_ubs))
    print("Total run time: {}".format(datetime.datetime.now()-start))
