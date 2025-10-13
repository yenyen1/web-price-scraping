import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    filename="check_price.log",
    filemode="a",
)


def get_logger(name: str):
    return logging.getLogger(name)
