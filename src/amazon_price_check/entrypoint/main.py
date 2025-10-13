import random
import time
from typing import Optional
from argparse import ArgumentParser
import logging
import json

import requests
from bs4 import BeautifulSoup


from amazon_price_check.mail_service import send_email
from amazon_price_check import header_config
from amazon_price_check.logger import get_logger

logger = get_logger(__name__)


def fetch_price_from_url(session: requests.Session, url: str) -> str:
    """Get the one-time-purchase price form the amazon url
    Args: requests.Session
          url
    Return: price string (CAD$1,024.99)
            return Empty string if not found"""
    response = session.get(
        url, timeout=header_config.TIMEOUT, proxies=header_config.PROXIES
    )
    if response.status_code != 200:
        return ""

    try:
        soup = BeautifulSoup(response.text, "lxml")

        def exact_class(tag):
            return (
                tag.name == "div"
                and tag.has_attr("class")
                and tag["class"] == ["a-spacing-top-mini"]
            )

        tag = soup.find(exact_class).find(class_="a-offscreen")
        if tag:
            return tag.get_text(strip=True)
        else:
            return ""
    except Exception:
        return ""


def normalize_price_text(text: str) -> Optional[float]:
    """Convert price string to float by remove currency symbol, comma, and whiltespace:
    Args: string (CAD$1,024.99)
    Return: float (1024.99)
            return None if function falled"""

    import re

    t = text.strip()
    t = re.sub(r"[^\d.]", "", t)
    try:
        return float(t)
    except Exception:
        return None


def get_price(session: requests.Session, url: str) -> Optional[float]:
    price = fetch_price_from_url(session, url)
    if price != "":
        return normalize_price_text(price)
    else:
        return None


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "-c", "--credentials", type=str, help="Path of Gmail API credentials.json"
    )
    parser.add_argument("-t", "--token", type=str, help="Path of Gmail API token.json")
    parser.add_argument("--config", type=str, help="Path of config json file")
    return parser.parse_args()


def main():
    args = parse_args()
    token = args.token
    credentials = args.credentials
    config = args.config

    s = requests.Session()
    s.headers.update(header_config.HEADERS)
    s.cookies.update(header_config.COOKIES)
    time.sleep(random.uniform(1, 3))

    with open(config, "r", encoding="utf-8") as f:
        data = json.load(f)
    urlname = data["urlname"]
    price_point = data["price_point"]
    url = data["url"]
    receiver = data["receiver"]
    sender = data["sender"]

    count = 0
    while True:
        price = get_price(s, url)
        if price is None:
            logging.warning("%s\t.\t%d", urlname, count + 1)
            count += 1
            time.sleep(random.uniform(1, 2.5))
        else:
            if price < price_point:
                subject = f"[PRICE ALERT] '{urlname}' is now only ${price:.2f}"
                body = f"""
Hi,

The product you're tracking has dropped in price.

    Product name: {urlname}
    Product url: {url}
    Current price: ${price:.2f}
    Alert price point: ${price_point:.2f}

PriceCheckBot
"""

                send_email(token, credentials, receiver, sender, subject, body)
            logging.info("%s\t%f\t%d", urlname, price, count + 1)
            count += header_config.MAX_RETRIES

        if count > header_config.MAX_RETRIES:
            time.sleep(14400)


if __name__ == "__main__":
    main()
