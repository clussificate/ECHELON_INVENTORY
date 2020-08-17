# -*- coding: utf-8 -*-
"""
@Created at 2020/6/26 22:43
@Author: Kurt
@file:Bounds.py
@Desc:
"""
from BOM import BOMSerial
from Config import ConfigX
from utils import TreeTypeException, InfoMissException, BCMethodException, CDFsimulation
from math import sqrt, ceil, floor, isnan, isinf
from scipy.stats import norm
import pickle
import datetime
import numpy as np
import seaborn as sns

conf = ConfigX(lam=16, distribution='normal', parameters=(1, 0), samples=20000, decimal=4)
lam, params, distrib, samples, decimal = conf.lam, conf.parameters, conf.distribution, conf.samples, conf.decimal


with open("simulation_table", "rb") as f:
    quantile = pickle.load(f)


def cal_quantiles(data, thetas, leadtimes, decimals=3, n_samples=10000, to_int=True):
    if len(thetas) != len(leadtimes):
        print("The length of thetas and leadtimes do not match")
        return None

    thetas = np.around(thetas, decimals=decimals)
    leadtimes = np.array(leadtimes).astype(int)

    n_quantiles = 10 ** decimals
    quantile_mesh = np.linspace(0, 1, n_quantiles + 1)
    init_quantiles = np.quantile(data, quantile_mesh)

    max_lead = np.max(leadtimes)
    ids_size = max_lead * n_samples
    random_quantile_ids = np.random.randint(0, n_quantiles + 1, ids_size)
    sampled_quantiles = init_quantiles[random_quantile_ids]

    quantiles = []
    for i in range(len(thetas)):
        if leadtimes[i] == 0:
            quantiles.append(0)
            continue
        n_to_cut = ids_size % leadtimes[i]
        samples = sampled_quantiles[:(ids_size - n_to_cut)].reshape((leadtimes[i], -1))

        samples = np.sum(samples, axis=0)
        quantiles.append(np.quantile(samples, thetas[i]))
    return quantiles


def cal_base_stock_nonparametric(CLjs, thetas, data):
    quantiles = cal_quantiles(data=data, thetas=thetas, leadtimes=CLjs)
    return quantiles


def cal_base_stock(CLj, theta, method="approximation"):

    if str.lower(method) == "approximation":

        # Compute using normal approximations
        if theta < 1:
            z = norm.ppf(theta)
            return lam * params[0] * CLj + z * sqrt(lam * (params[0] ** 2 + params[1] ** 2) * CLj)
        else:
            # if quantile point is more than 1, we use simulation table to calculate its quantile value
            return quantile[lam*CLj][1]
    elif str.lower(method) == "simulation":
        # print("lam*l: {}".format(lam*l))
        # print("quantile: {}".format(quantile[lam*l][round(theta, 4)]))
        # return inverse_compound(theta, lam*l, params, "normal", samples)
        if CLj != 0:
            if theta < 1:
                return quantile[lam * CLj][round(theta, decimal)]
            else:
                return quantile[lam * CLj][round(1, decimal)]
        else:
            return 0
    else:
        raise BCMethodException()


def Bounds(lead_times, echelon_holding_costs, penalty_cost, mode=0,
           method="approximation", gene_table=False, data=None):
    """
    :param gene_table:
    :param data:
    :param mode: 0 - rounding up; 1 - rounding down; 2 - no rounding
    :param penalty_cost: backorder cost
    :param lead_times: transportation time for node i to its successor.
                        Differ from the definition on lead time in Song et.al (2003)
    :param echelon_holding_costs: same as the definition in Song et.al (2003)
    :param method: "approximation": normal approximation;
                      "simulation": using simulation
                      "nonparametric": demand estimation using nonparametric method
        :return: lower bounds and upper bounds
    """
    # Cumulative lead time,
    # notice the difference on the definition of lead time in Song et.al (2003)

    CLjs = []
    theta_jls = []
    theta_jus = []

    for j in range(len(echelon_holding_costs)):
        CLj = sum(lead_times[j:])
        CLjs.append(CLj)
        theta_jl = (penalty_cost + sum(echelon_holding_costs[0: j])) / \
                   (penalty_cost + sum(echelon_holding_costs))
        theta_jls.append(theta_jl)
        theta_ju = (penalty_cost + sum(echelon_holding_costs[0: j])) / \
                   (penalty_cost + sum(echelon_holding_costs[0: j+1]))
        theta_jus.append(theta_ju)

    print("theta_jls: {}".format(theta_jls))
    print("theta_jus: {}".format(theta_jus))
    print("CLjs:  {}".format(CLjs))

    if gene_table and str.lower(method) == "simulation":
        start = datetime.datetime.now()
        for clj in set(CLjs):
            print("Current processing cumulative lead time: {}".format(clj))
            quantile[clj * lam] = CDFsimulation(clj * lam, params, decimal)
        print("Simulation done .........")
        print("Simulation run time: {}".format(datetime.datetime.now() - start))

        with open("simulation_table", "wb") as f:
            pickle.dump(quantile, f)

    if str.lower(method) in ["approximation", "simulation"]:
        lbs = [cal_base_stock(x, y) for x, y in zip(CLjs, theta_jls)]
        ubs = [cal_base_stock(x, y) for x, y in zip(CLjs, theta_jus)]
    elif str.lower(method) == "nonparametric":
        lbs = cal_base_stock_nonparametric(CLjs, theta_jls, data=data)
        ubs = cal_base_stock_nonparametric(CLjs, theta_jus, data=data)

    print("Lower bounds: {}".format(lbs))
    print("Upper bounds: {}".format(ubs))

    if mode == 0:
        return [ceil(x) for x in lbs], [ceil(x) for x in ubs]
    elif mode == 1:
        return [floor(x) for x in lbs], [floor(x) for x in ubs]
    else:
        return lbs, ubs

    # try:
    #     if mode == 0:
    #         return [ceil(x) for x in lbs], [ceil(x) for x in ubs]
    #     elif mode == 1:
    #         return [floor(x) for x in lbs], [floor(x) for x in ubs]
    #     else:
    #         return lbs, ubs
    # except (OverflowError, ValueError):
    #     print("|--------------------------------------------------------------------------------------------------|")
    #     print("|----Some installations are Inf or NaN value, set the base stock bounds as 100% quantile----|")
    #     print("|--------------------------------------------------------------------------------------------------|")
    #     lbs = [capacity if isnan(x) or isinf(x) else x for x in lbs]
    #     ubs = [capacity if isnan(x) or isinf(x) else x for x in ubs]
    #     print("Modified lower bounds: {}".format(lbs))
    #     print("Modified uppers bounds: {}".format(ubs))
    #     if mode == 0:
    #         return [ceil(x) for x in lbs], [ceil(x) for x in ubs]
    #     elif mode == 1:
    #         return [floor(x) for x in lbs], [floor(x) for x in ubs]
    #     else:
    #         return lbs, ubs


def cacl_echelon_holding_cost(node):
    """
    calculate echelon holding cost
    """
    predecessors = node.predecessors
    pred_holding_cost = sum([x.holding_cost for x in predecessors])
    return node.holding_cost - pred_holding_cost


def calc_bounds(serial, recalc=False, method="approximation", gene_table=False, conf=None, data=None):
    """"
    :param recalc: False - need not calculate echelon holding cost;
                 otherwise - recalculate echelon holding cost.
    :param conf: configure class which defines demand process
    :param method: "approximation": normal approximation;
                      "simulation": using simulation
                    "nonparametric": demand estimation using nonparametric method
    :param data: required data for nonparametric demand estimation
    :return: lower and upper bounds of echelon base stock levels
    """
    if not isinstance(serial, BOMSerial):
        raise TreeTypeException()

    if method != "nonparametric":
        lam = conf.lam
        params = conf.parameters
        distrib = conf.distribution
        samples = conf.samples
        decimal = conf.decimal

    # initial lists with the first dummy node
    lead_time_list = [0]
    echelon_holding_cost_list = []
    node_number = []

    # recalculate echelon holding cost
    if recalc:
        print("----------------Recalculate echelon holding cost: begin----------------------")
        current_node = serial.leaves[0]
        current_node.echelon_holding_cost = current_node.holding_cost

        echelon_holding_cost_list.append(current_node.echelon_holding_cost)
        lead_time_list.append(current_node.lead_time)
        node_number.append(current_node.number)

        current_node = current_node.successor
        # print("Successor of Leaf node: {}".format(current_node.number))
        while current_node:
            current_node.echelon_holding_cost = cacl_echelon_holding_cost(current_node)
            echelon_holding_cost_list.append(current_node.echelon_holding_cost)
            lead_time_list.append(current_node.lead_time)
            node_number.append(current_node.number)
            current_node = current_node.successor

        print("----------------Recalculate echelon holding cost: done----------------------")
    else:
        current_node = serial.leaves[0]
        while current_node:
            if current_node.echelon_holding_cost is None:
                raise InfoMissException()

            echelon_holding_cost_list.append(current_node.echelon_holding_cost)
            lead_time_list.append(current_node.lead_time)
            node_number.append(current_node.number)
            current_node = current_node.successor

    # initial lists with the second dummy node
    echelon_holding_cost_list.append(0.0001)

    print("Echelon holding costs: {}".format(echelon_holding_cost_list))
    print("Installation lead times: {}".format(lead_time_list))
    print("Penalty cost: {}".format(serial.root.penalty_cost))
    print("-----------------------------------------------------------------------------")

    # start = datetime.datetime.now()
    lbs, ubs = Bounds(lead_times=lead_time_list,
                      echelon_holding_costs=echelon_holding_cost_list,
                      penalty_cost=serial.root.penalty_cost,
                      method=method, gene_table=gene_table,
                      data=data)

    # print("Bounds calculate time: {}".format(datetime.datetime.now()-start))

    dict_bound = dict(zip(node_number, [x for x in zip(lbs, ubs)]))

    return dict_bound


if __name__ == "__main__":
    # notice: Due to the different definition on lead time in Song (2003),
    #         we need set two dummy nodes with sufficiently small holding cost,
    #         we also need set the lead time of root node to be zero.
    Lead_time_list = [0, 0.25, 0.25, 0.25, 0.25, 0]
    """
    @ example: four stages serial system with L=0.25, h=2.5, lambda=16, see Song(2003) table 6. 
    """
    Echelon_holding_cost_list = [0.0001, 2.5, 2.5, 2.5, 2.5, 0.0001]
    penalty_cost = 99

    lbs, ubs = Bounds(Lead_time_list, Echelon_holding_cost_list, penalty_cost, 1, "Simulation", True)
    print("Rounding lbs: {}".format(lbs))
    print("Rounding ubs: {}".format(ubs))

