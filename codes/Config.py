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

    def __init__(self, lam=16, distribution="normal", parameters=(10, 3), samples=2000, decimal=4):
        self.lam = lam       # unit arrival rate
        self.distribution = distribution
        self.parameters = parameters  # parameters of distribution function
        self.samples = samples      # number of simulation samples
        self.decimal = decimal          # precision of quantile points.

