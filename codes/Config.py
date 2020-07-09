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

    def __init__(self):
        self.lam = 16       # unit arrival rate
        self.distribution = "normal"
        self.parameters = (1, 0)  # parameters of distribution function
        self.capacity = 500  # maximal capacity of installations
