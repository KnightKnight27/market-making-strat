import logging

from hftbacktest import BacktestAsset, HashMapMarketDepthBacktest

from AutomatedTrader import AutomatedTrader
from utils import Side

"""
OrderBook Imbalance Ratio
"""


class OIR:
    def __init__(self, bid_price, ask_price, oir_ratio, volume):
        self.__bid_price = bid_price
        self.__ask_price = ask_price
        self.__oir = oir_ratio
        self.__total_volume = volume

    @property
    def ask_price(self):
        return self.__ask_price

    @property
    def bid_price(self):
        return self.__bid_price

    @property
    def oir(self):
        return self.__oir

    @property
    def total_volume(self):
        return self.__total_volume

    def __repr__(self):
        return f"<OrderImbalance(bid_price={self.__bid_price}, ask_price={self.__ask_price}, imbalance_ratio={self.__oir:.2f})>"


"""
Market Making Strategy based on Order Imbalance
"""


class MMStrategy:
    def __init__(self, tick_data, instrument):
        self.__logger = logging.getLogger("Strategy")
        self.__tick_data = tick_data
        self.__spot_pair = instrument
        self.__asset_simulation = self.__get_asset_from_ticks()
        self.__testing_simulation = self.__get_backtest_simulation()
        self.__bot_trader = AutomatedTrader(self.__testing_simulation)
        self.__capture_bp = 10  # should be configurable

    def __get_backtest_simulation(self):
        self.__logger.info(f"{self.__spot_pair} hashmap backtest simulation construction")
        return HashMapMarketDepthBacktest([self.__asset_simulation])

    def __get_asset_from_ticks(self):
        self.__logger.info(f"{self.__spot_pair} asset simulation construction")
        # these variables should be config controlled, so look for adding a config here
        asset_simulation = (
            BacktestAsset()
            .data([self.__tick_data])
            .linear_asset(1.0)
            .constant_latency(10_000_000, 10_000_000)
            .risk_adverse_queue_model()
            .no_partial_fill_exchange()
            .trading_value_fee_model(0.0002, 0.0007)
            .tick_size(0.1)
            .lot_size(0.001)
        )
        self.__logger.info(f"{self.__spot_pair} asset simulation finished")
        return asset_simulation

    def __calculate_orderbook_imbalance_ratio(self, timestamp, bid_qty, ask_qty):
        self.__logger.info(f"Calculating OIR ratio at {timestamp}")
        return (bid_qty - ask_qty) / (bid_qty + ask_qty)

    # generator function to get order book ratio for every 1 seconds
    def __get_orderbook_imbalance_at_timestamp(self):
        while self.__testing_simulation.elapse(1_000_000_000) == 0:
            self.__logger.info('current_timestamp: %s', self.__testing_simulation.current_timestamp)
            depth = self.__testing_simulation.depth(0)
            bid_price = depth.best_bid_tick
            bid_qty = depth.bid_qty_at_tick(bid_price)
            ask_price = depth.best_ask_tick
            ask_qty = depth.ask_qty_at_tick(ask_price)
            assert (bid_price < ask_price, "Exchange can't have unmatched orders")
            oir = OIR(bid_price, ask_price,
                      self.__calculate_orderbook_imbalance_ratio(self.__testing_simulation.current_timestamp, bid_qty,
                                                                 ask_qty), bid_qty + ask_qty)
            yield oir
        yield None

    """
        The OIR value typically ranges from -1 to 1.
        -1: Indicates a strong sell imbalance (only sell orders).
        0: Indicates a balanced order book (equal buy and sell volumes).
        1: Indicates a strong buy imbalance (only buy orders).

        This func will decide to make a trade only when
        abs(oir_ratio) >=  1 - delta_diff_to_trade
        tells us if have a weak trend or a strong trend in market
    """

    def __make_trading_decision_using_oir(self, imbalance, delta_diff_to_trade=0.3):
        self.__bot_trader.clear_inactive_orders()
        if abs(imbalance.oir) < 1 - delta_diff_to_trade:
            # Let's not trade
            return
        if imbalance.oir < 0:
            self.__negative_oir_trading(imbalance)
        else:
            self.__positive_oir_trading(imbalance)

    """
       Exact Actions:
       Adjust Ask Price Upwards: Raise your ask price to capitalize on the buying pressure, ensuring that you are not providing liquidity too cheaply.
       Action: Place limit sell orders slightly above the current best ask price to capture higher prices.
       Place Competitive Bid Orders: Place buy orders at competitive prices to accumulate inventory.
       Action: Submit limit buy orders at or just below the current best bid to ensure you are still offering liquidity to buyers while managing inventory.
    """

    @staticmethod
    def __mean_price_to_quote(imbalance):
        return (imbalance.bid_price + imbalance.ask_price) / 2

    @staticmethod
    def __target_volume_to_quote(bp, imbalance):
        return (imbalance.total_volume * bp) / 10 ** 4

    @staticmethod
    def __price_delta(price, imbalance, bp):
        return bp * (price - imbalance.bid_price) / 10 ** 4

    def __positive_oir_trading(self, imbalance):
        target_price = self.__mean_price_to_quote(imbalance)
        target_volume = self.__target_volume_to_quote(self.__capture_bp, imbalance)
        price_delta = self.__price_delta(target_price, imbalance, self.__capture_bp)
        self.__bot_trader.submit_order(Side.SELL, target_price + 2 * price_delta, target_volume)
        self.__bot_trader.submit_order(Side.BUY, target_price - price_delta, target_volume)

    """
        Exact Actions:
        Lower Bid Price: Decrease your bid price to avoid buying too high during significant selling pressure.
        Action: Place limit buy orders below the current best bid price to accumulate inventory at more favorable rates.
        Place Competitive Ask Orders: Adjust your ask price to stay competitive while ensuring you're not caught in a declining market.
        Action: Submit limit sell orders at or just below the current best ask to offload inventory and realize profits before prices potentially drop further.
        Widen the Spread for Safety: During high sell pressure, increase the spread to account for potential rapid price drops.
        Action: Adjust the spread based on your risk model to maintain profitability.
    """

    def __negative_oir_trading(self, imbalance):
        target_price = self.__mean_price_to_quote(imbalance)
        target_volume = self.__target_volume_to_quote(self.__capture_bp, imbalance)
        price_delta = self.__price_delta(target_price, imbalance, self.__capture_bp)
        self.__bot_trader.submit_order(Side.BUY, target_price - 2 * price_delta, target_volume)
        self.__bot_trader.submit_order(Side.SELL, target_price - price_delta, target_volume)

    async def run(self):
        self.__logger.info("Tada Let's Start Adding some liquidity")
        for oir in self.__get_orderbook_imbalance_at_timestamp():
            if oir is None:
                break
            self.__logger.info(oir)
            self.__make_trading_decision_using_oir(oir)
