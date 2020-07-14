# -*- coding: utf-8 -*-
"""
@Created at 2020/6/28 13:08
@Author: Kurt
@file:test.py
@Desc:
"""
from Bounds import cal_base_stock

CLj = 5
theta = 1.2
method = "simulation"

bs = cal_base_stock(CLj, theta, method)
print(bs)
