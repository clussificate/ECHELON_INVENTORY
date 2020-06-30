# -*- coding: utf-8 -*-
"""
@Created at 2020/6/30 11:59
@Author: Kurt
@file:PolicyEvaluation.py
@Desc:
"""
from Config import ConfigX


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

    lead_time_list = [0.25, 0.25, 0.25, 0.25, 0.]
    echelon_holding_cost_list = [0.0001, 2.5, 2.5, 2.5, 0.25]
    base_stock_list = [25, 18, 14, 8]  # omit the dummy leaf node
    penalty_cost = 99
    total_cost = policy_evaluation(base_stocks=base_stock_list, holding_costs=echelon_holding_cost_list,
                                   lead_times=lead_time_list, penalty_cost=99)
    print("Total cost of base stock {} is: {} ".format(base_stock_list, total_cost))