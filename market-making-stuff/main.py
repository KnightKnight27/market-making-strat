import argparse
import asyncio
import logging

from MMStrategy import MMStrategy
from TradeTickReader import TradeTickReader

# Configure global logging settings
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s-%(levelname)s-%(name)s-%(message)s",
    handlers=[
        logging.FileHandler("output.log", mode='a'),
        logging.StreamHandler()
    ]
)
arg_reader_logger = logging.getLogger("ArgReader")


async def main(path: str, instrument: str, process: str):
    arg_reader_logger.info(f"Running main with path: {path}, instrument: {instrument}, process: {process}")
    tick_reader = TradeTickReader(path, instrument)
    strategy = MMStrategy(tick_reader.tick_data, instrument)
    # Can use a strategy design pattern or some factory but
    # focussing on completion for now
    await strategy.run()


if __name__ == "__main__":
    arg_reader_logger.info("Starting the script - Night Watchman MM!")

    parser = argparse.ArgumentParser(
        description="Script that takes a path, an instrument, and process information as input.")
    parser.add_argument("--path", type=str, help="The path to the file or directory.")
    parser.add_argument("--instrument", type=str, help="The name of the instrument.")
    parser.add_argument("-p", "--process", type=str, required=True, help="The name of the process (mandatory).")
    parser.add_argument("-s", "--stdout", action="store_true",
                        help="Prints output to stdout if specified. If not, writes to process_name.out file.")

    args = parser.parse_args()
    arg_reader_logger.info("Parsed arguments: %s", args)

    try:
        asyncio.run(main(args.path, args.instrument, args.process))
    except Exception as e:
        arg_reader_logger.exception("An error occurred during script execution: %s", e)
