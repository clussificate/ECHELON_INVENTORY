# -*- coding: utf-8 -*-
"""
@Created at 2020/6/28 13:08
@Author: Kurt
@file:test.py
@Desc:
"""
import numpy as np
import datetime
from Config import ConfigX


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


if __name__ == "__main__":
    print("Simulation begin .........")
    start = datetime.datetime.now()
    CLjs = [6]
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
