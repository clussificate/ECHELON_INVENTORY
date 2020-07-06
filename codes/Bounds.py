# -*- coding: utf-8 -*-
"""
@Created at 2020/6/26 22:43
@Author: Kurt
@file:Bounds.py
@Desc:
"""
from BOM import BOMSerial
from utils import TreeTypeException, InfoMissException
from math import sqrt, ceil, floor, isnan, isinf
from scipy.stats import norm
from Config import ConfigX

conf = ConfigX()
mu = conf.mu
lam = conf.lam
sigma = conf.sigma
capacity = conf.capacity


def cal_base_stock(l, z):
    global mu
    global lam
    global sigma

    return lam*mu*l + z*sqrt(lam*(mu**2 + sigma**2)*l)


def poisson_bounds(lead_times, echelon_holding_costs, penalty_cost):
    """
    TODO

    Question: how to calculate the inverse of cdf of compound poisson distribution? Simulation?
    """
    pass


def normal_bounds(lead_times, echelon_holding_costs, penalty_cost, mode=0):
    """

    :param mode: 0 - rounding up; 1 - rounding down; 2 - no rounding
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
    Ljs = []
    theta_jls = []
    theta_jus = []

    for j in range(len(echelon_holding_costs)):
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

    print("theta_jls: {}".format(theta_jls))
    print("theta_jus: {}".format(theta_jus))
    print("zjls: {}".format(zjls))
    print("zjus: {}".format(zjus))
    print("Ljs:  {}".format(Ljs))

    lbs = [cal_base_stock(x, y) for x, y in zip(Ljs, zjls)]
    ubs = [cal_base_stock(x, y) for x, y in zip(Ljs, zjus)]
    # cost_lb = None
    # cost_ub = None
    try:
        print("Normal approximation of Lower bounds: {}".format(lbs))
        print("Normal approximation of Upper bounds: {}".format(ubs))
        if mode == 0:
            return [ceil(x) for x in lbs], [ceil(x) for x in ubs]
        elif mode == 1:
            return [floor(x) for x in lbs], [floor(x) for x in ubs]
        else:
            return lbs, ubs
    except OverflowError:
        print("|--------------------------------------------------------------------------------------------------|")
        print("|----Some installations are Inf or NaN value, set the base stock bounds as the maximal capacity----|")
        print("|--------------------------------------------------------------------------------------------------|")
        lbs = [capacity if isnan(x) or isinf(x) else x for x in lbs]
        ubs = [capacity if isnan(x) or isinf(x) else x for x in ubs]
        print("Modified normal approximation of lower bounds: {}".format(lbs))
        print("Modified normal approximation of uppers bounds: {}".format(ubs))
        if mode == 0:
            return [ceil(x) for x in lbs], [ceil(x) for x in ubs]
        elif mode == 1:
            return [floor(x) for x in lbs], [floor(x) for x in ubs]
        else:
            return lbs, ubs


def cacl_echelon_holding_cost(node):
    """
    calculate echelon holding cost
    """
    predecessors = node.predecessors
    pred_holding_cost = sum([x.holding_cost for x in predecessors])
    return node.holding_cost - pred_holding_cost


def calc_bounds(serial, recalc=False):
    """"
    :param recalc: False - need not calculate echelon holding cost;
                 otherwise - recalculate echelon holding cost.
    :return: lower and upper bounds of echelon base stock levels
    """
    if not isinstance(serial, BOMSerial):
        raise TreeTypeException()

    # initial lists with the first dummy node
    lead_time_list = [0]
    echelon_holding_cost_list = []

    # recalculate echelon holding cost
    if recalc:
        print("----------------Recalculate echelon holding cost: begin----------------------")
        current_node = serial.leaves[0]
        current_node.echelon_holding_cost = current_node.holding_cost

        echelon_holding_cost_list.append(current_node.echelon_holding_cost)
        lead_time_list.append(current_node.lead_time)

        current_node = current_node.successor
        # print("Successor of Leaf node: {}".format(current_node.number))
        while current_node:
            current_node.echelon_holding_cost = cacl_echelon_holding_cost(current_node)
            echelon_holding_cost_list.append(current_node.echelon_holding_cost)
            lead_time_list.append(current_node.lead_time)
            current_node = current_node.successor

        print("----------------Recalculate echelon holding cost: done----------------------")
    else:
        current_node = serial.leaves[0]
        while current_node:
            if current_node.echelon_holding_cost is None:
                raise InfoMissException()

            echelon_holding_cost_list.append(current_node.echelon_holding_cost)
            lead_time_list.append(current_node.lead_time)
            current_node = current_node.successor

    # initial lists with the second dummy node
    echelon_holding_cost_list.append(0.0001)

    print("Echelon holding costs: {}".format(echelon_holding_cost_list))
    print("Installation lead times: {}".format(lead_time_list))
    print("Penalty cost: {}".format(serial.root.penalty_cost))
    print("-----------------------------------------------------------------------------")
    normal_lbs, normal_ubs = normal_bounds(lead_times=lead_time_list,
                                           echelon_holding_costs=echelon_holding_cost_list,
                                           penalty_cost=serial.root.penalty_cost)
    return normal_lbs, normal_ubs


if __name__ == "__main__":
    # notice: Due to the different definition on lead time in Song (2003),
    #         we need set two dummy nodes with sufficiently small holding cost,
    #         we also need set the lead time of root node to be zero.
    lead_time_list = [0, 0.25, 0.25, 0.25, 0.25, 0]
    """
    @ example: four stages serial system with L=0.25, h=2.5, lambda=16, see Song(2003) table 6. 
    """
    echelon_holding_cost_list = [0.0001, 2.5, 2.5, 2.5, 2.5, 0.0001]
    penalty_cost = 99
    lbs, ubs = normal_bounds(lead_time_list, echelon_holding_cost_list, penalty_cost)
    print("Rounding lbs: {}".format(lbs))
    print("Rounding ubs: {}".format(ubs))

