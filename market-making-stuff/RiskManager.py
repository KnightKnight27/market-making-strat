"""
Run Risk Checks on the basis of position,order constraints etc
Since this is covering a single pair, hence risk exposure to having a big position of some coin could be adverse
# umm Maybe we can hedge with some perps and minimize risk or don't send orders violating position constraints
"""
import logging


class RiskManager:
    def __init__(self, simulator):
        self.__logger = logging.getLogger("RiskManager")
        self.__simulator = simulator
        self.__max_order_size = 1000
        self.__threshold_position = 1000

    def run_risk_checks(self, qty):
        self.__logger.info("Running risk checks")
        if qty > self.__max_order_size:
            return False
        position = self.__simulator.position(0)
        if position > self.__max_order_size:
            return False
        balance = self.__simulator.state_values(0).balance
        # an improvement could be to send multiple orders instead of sending simple order which exceeds order limit
        return True
