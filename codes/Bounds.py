# -*- coding: utf-8 -*-
"""
@Created at 2020/6/26 22:43
@Author: Kurt
@file:Bounds.py
@Desc:
"""
from BOM import BOMSerial
from utils import TreeTypeException, InfoMissException
import numpy as np
from math import sqrt
from scipy.stats import norm

"""
    :param lam: unit arrival rate
    :param sigma: standard deviation of demand batch size
    :param mu: mean of demand batch size
"""
mu = 20
sigma = 5
lam = 1


def cal_base_stock(l, z):
    return lam*mu*l + z*sqrt(lam*(mu**2 + sigma**2)*l)


def normal_bounds(lead_times, echelon_holding_costs, penalty_cost):
    """
    :param penalty_cost: backorder cost
    :param lead_times: transportation time for node i to its successor.
                        Differ from the definition on lead time in Song et.al (2003)
    :param echelon_holding_costs: same as the definition in Song et.al (2003)
    :return: lower bounds and upper bounds with normal distribution approximation
    @ example:
    serial: |6| --1--> |5| --1--> |4+2| --1--> |3| ---2--> |1|--1--> |0| ---0-->
     lower bound of node 4 (i.e. number 4+2), lead time:1+1+2+1=5
    """

    # Cumulative lead time,
    # notice the difference on the definition of lead time in Song et.al (2003)
    lead_times.insert(0, 0)  # insert 0 lead time for the first node
    Ljs = []
    theta_jls = []
    theta_jus = []

    for j in range(len(lead_times)-1):  # remove the last node
        Lj = sum(lead_times[j:])
        Ljs.append(Lj)
        theta_jl = (penalty_cost + sum(echelon_holding_costs[0: j])) / \
                   (penalty_cost + sum(echelon_holding_costs))
        theta_jls.append(theta_jl)
        theta_ju = (penalty_cost + sum(echelon_holding_costs[0: j])) / \
                   (penalty_cost + sum(echelon_holding_costs[0: j+1]))
        theta_jus.append(theta_ju)

    zjls = [norm.ppf(x) for x in theta_jls]
    zjus = [norm.ppf(x) for x in theta_jus]

    lbs = [cal_base_stock(x, y) for x, y in zip(lead_times, zjls)]
    ubs = [cal_base_stock(x, y) for x, y in zip(lead_times, zjus)]
    # cost_lb = None
    # cost_ub = None
    return lbs, ubs


def cacl_echelon_holding_cost(node):
    """
    calculate echelon holding cost
    """
    predecessors = node.predecessors
    pred_hodling_cost = sum([x.holding_cost for x in predecessors])
    return node.holding_cost - pred_hodling_cost


def calc_bounds(serial, mode=1):
    """"
    :param mode: 0 - need not calculate echelon holding cost;
                 otherwise - recalculate echelon holding cost.
    :return: lower and upper bounds
    """
    if not isinstance(serial, BOMSerial):
        raise TreeTypeException()

    echelon_holding_cost_list = []
    lead_time_list = []

    # recalculate echelon holding cost
    if mode != 0:
        current_node = serial.leaves[0]
        current_node.echelon_holding_cost = current_node.holdng_cost

        echelon_holding_cost_list.append(current_node.echelon_holding_cost)
        lead_time_list.append(current_node.lead_time)

        current_node = current_node.successor
        while current_node:
            current_node.echelon_holding_cost = cacl_echelon_holding_cost(current_node)
            current_node = current_node.successor
    else:
        current_node = serial.leaves[0]
        while current_node:
            if current_node.echelon_holding_cost is None:
                raise InfoMissException()

            echelon_holding_cost_list.append(current_node.echelon_holding_cost)
            lead_time_list.append(current_node.lead_time)

    normal_lbs, normal_ubs = normal_bounds(lead_time_list, echelon_holding_cost_list, serial.root.penalty_cost)
    return normal_lbs, normal_ubs

















