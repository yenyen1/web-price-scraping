import requests
from bs4 import BeautifulSoup
import random 
import time
from typing import Optional
import logging
from .config import HEADERS, COOKIES, TIMEOUT, PROXIES, MAX_RETRIES, URL_NAME, URL, PRICE_POINT

logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        filename="check_price.log",
        filemode="a",
)

def fetch_price_from_url(session: requests.Session, url: str) -> str:
    """ Get the one-time-purchase price form the amazon url
    Args: requests.Session 
          url 
    Return: price string (CAD$1,024.99) 
            return Empty string if not found """
    response = session.get(url, timeout=TIMEOUT, proxies=PROXIES)
    if response.status_code != 200:
        return ""
    
    try:
        soup = BeautifulSoup(response.text, 'lxml')
        def exact_class(tag):
            return (
                tag.name == "div"
                and tag.has_attr("class")
                and tag["class"] == ["a-spacing-top-mini"]
            )
        tag = soup.find(exact_class).find(class_ = "a-offscreen")
        if tag:
            return tag.get_text(strip=True)
        else:
            return ""
    except Exception:
        return ""

def normalize_price_text(text: str) -> Optional[float]:
    """ Convert price string to float by remove currency symbol, comma, and whiltespace: 
    Args: string (CAD$1,024.99)
    Return: float (1024.99)
            return None if function falled """

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


def main():
    s = requests.Session()
    s.headers.update(HEADERS)
    s.cookies.update(COOKIES)
    time.sleep(random.uniform(1, 3))

    count = 0
    while count < MAX_RETRIES:
        price = get_price(s, URL)
        if price is None:
            logging.warning('%s\t.\t%d', URL_NAME, count+1)
            count += 1
            time.sleep(random.uniform(1, 2.5))
        else:
            if price < PRICE_POINT:
                # add sent mail
                print("Successful!")
            logging.info('%s\t%f\t%d', URL_NAME, price, count+1)
            count += MAX_RETRIES


if __name__ == "__main__":
    main()