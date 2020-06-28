# -*- coding: utf-8 -*-
"""
@Created at 2020/6/28 13:00
@Author: Kurt
@file:Config.py
@Desc:
"""


class ConfigX:
    """
    The class define the parameters of demand process.
    """
    __slots__ = ("lam", "sigma", "mu")

    def __init__(self):
        self.lam = 16       # unit arrival rate
        self.sigma = 0     # standard deviation of demand batch size
        self.mu = 1       # mean of demand batch size
