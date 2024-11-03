import logging

import numpy as np
from hftbacktest.data.utils import binancefutures


class TradeTickReader:
    def __init__(self, file_path, instrument):
        self.__logger = logging.getLogger("TradeTickReader")
        self.__spot_pair = instrument
        self.__tick_data = self.__parse_tick_data_file(file_path)

    def __parse_tick_data_file(self, file_path):
        self.__logger.info("Parsing tick data in memory!")
        output_file = f'{self.__spot_pair}_normalized.npz'
        _ = binancefutures.convert(
            file_path,
            output_filename=output_file,
            combined_stream=True
        )
        return np.load(output_file)['data']

    @property
    def tick_data(self):
        return self.__tick_data
