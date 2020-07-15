# -*- coding: utf-8 -*-
"""
@Created at 2020/6/28 13:08
@Author: Kurt
@file:test.py
@Desc:
"""
from Bounds import cal_base_stock
import  pickle


CLj = 5
theta = 1.2
method = "simulation"

bs = cal_base_stock(CLj, theta, method)
print(bs)

with open("simulation_table", "rb") as f:
    quantile = pickle.load(f)

print(quantile)