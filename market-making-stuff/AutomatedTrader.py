import logging

from hftbacktest import LIMIT, GTC

from RiskManager import RiskManager
from utils import Side

"""
Trading Bot for triggering orders,canceling etc
"""


class AutomatedTrader:
    def __init__(self, backtest_simulator):
        self.__logger = logging.getLogger("BotTrader")
        self.__simulator = backtest_simulator
        self.__order_id = 1
        self.__risk_controller = RiskManager(backtest_simulator)

    def submit_order(self, side, price, qty, order_type=LIMIT):
        assert price > 0, "Price must be greater than 0."
        assert qty > 0, "Quantity must be greater than 0."
        assert isinstance(order_type, int), "Order type must be an integer."
        self.__logger.info("Submitting order - Side: %s, Price: %.6f, Quantity: %.6f, Order Type: %s",
                           "BUY" if side == Side.BUY else "SELL", price, qty, order_type)
        time_in_force = GTC  # Good 'till cancel
        if self.__risk_controller.run_risk_checks(qty):
            if side == Side.BUY:
                self.__simulator.submit_buy_order(0, self.__order_id, price, qty, time_in_force, order_type, False)
            else:
                self.__simulator.submit_sell_order(0, self.__order_id, price, qty, time_in_force, order_type, False)
            self.__order_id += 1

    def clear_inactive_orders(self):
        self.__logger.info("clearing inactive orders")
        self.__simulator.clear_inactive_orders(0)
