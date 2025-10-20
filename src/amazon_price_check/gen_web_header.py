import random
from fake_useragent import UserAgent
from amazon_price_check.logger import get_logger

PROXIES = None
TIMEOUT = 15
MAX_RETRIES = 3
USER_AGENT = [
    # macOS / Chrome
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    # Windows / Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Linux / Chrome
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    # macOS / Safari
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    # Windows / Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edg/118.0.0.0 Chrome/118.0.0.0 Safari/537.36",
]
COOKIES = {"i18n-prefs": "CAD", "lc-acbca": "en_CA"}

logger = get_logger(__name__)


def _get_user_agent(seed=None, cache=True) -> str:
    if seed is not None:
        random.seed(seed)
    try:
        mobile_indicators = [
            "mobile",
            "iphone",
            "ipad",
            "android",
            "android 10",
            "android 11",
            "silk/",
            "opera mini",
            "windows phone",
        ]
        user_agent = ""
        is_mobile = True
        ua = UserAgent()
        while is_mobile:
            user_agent = ua.random
            ua_lower = user_agent.lower()
            is_mobile = any(k in ua_lower for k in mobile_indicators)
        return user_agent
    except Exception:
        logger.warning(
            "[_get_user_agent] can not get user agent from fake_useragent. line 33 in header_config.py."
        )
        return random.choice(USER_AGENT)


def _get_sec_ch_ua(ua_str: str) -> str:
    def _extract_chrome_major(ua_str: str) -> str:
        import re

        m = re.search(r"(?:Chrome|Chromium|Edg|Edge)/(\d+)", ua_str)
        if m:
            return m.group(1)
        logger.warning(
            "[_extrct_chrome_major] Chome major is not found. line 49 in header_config.py."
        )
        return str(random.randint(80, 140))

    brands = []
    if "Brave" in ua_str:
        brands.append(("Brave", _extract_chrome_major(ua_str)))
    if "Chromium" in ua_str:
        brands.append(("Chromium", _extract_chrome_major(ua_str)))
    if "Chrome/" in ua_str:
        brands.append(("Google Chrome", _extract_chrome_major(ua_str)))
    if "Edg/" in ua_str or "Edge/" in ua_str:
        brands.append(("Microsoft Edge", _extract_chrome_major(ua_str)))

    if not brands:
        brands = [("Chromium", "100")]

    parts = [f'"{name}";v="{ver}"' for name, ver in brands[:2]]
    parts.insert(0, '"Not;A=Brand";v="99"')
    return ", ".join(parts)


def _get_desktop_platform(ua: str) -> tuple[str, str]:
    import re

    ua_lower = ua.lower()
    if "windows" in ua_lower:
        match = re.search(r"windows nt ([\d.]+)", ua_lower)
        version = ""
        if match:
            version = match.group(1) if match else "10"
        else:
            logger.warning(
                '[_get_desktop_platform] Using random.choice becauce "window nt" is not exist. line 72 in header_config.py.'
            )
            version = random.choice(["10", "11", "6.1", "6.3"])
        return ("Windows", f'"{version}"')
    if "macintosh" in ua_lower or "mac os" in ua_lower:
        match = re.search(r"mac os x (\d+)[._](\d+)[._]?(\d+)?", ua_lower)
        if match:
            major, minor, patch = match.group(1), match.group(2), match.group(3) or "0"
            return ("macOS", f'"{major}.{minor}.{patch}"')
        else:
            logger.warning(
                '[_get_desktop_platform] Using random.choice becauce "mac os x" is not exist. line 81 in header_config.py.'
            )
            major = random.choice(["10", "11", "12", "13", "14", "15"])
            minor = random.randint(0, 6)
            patch = random.randint(0, 2)
            return ("macOS", f'"{major}.{minor}.{patch}"')
    if "linux" in ua_lower or "x11" in ua_lower:
        return ("Linux", '"0"')
    logger.warning(
        '[_get_desktop_platform] Return default setting "(Windows, 10)". line 93 in header_config.py.'
    )
    return ("Windows", '"10"')


def get_random_header(seed=None, overrides=None) -> str:
    ua = _get_user_agent(seed=seed)
    accept = random.choice(
        [
            "text/html, application/json",
            "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        ]
    )
    accept_encoding = random.choice(["gzip, deflate, br", "gzip, deflate, br, zstd"])
    accept_language = random.choice(
        ["en-US,en;q=0.8", "en-US,en;q=0.9", "zh-TW,zh;q=0.9,en-US;q=0.7"]
    )
    sec_ch_ua = _get_sec_ch_ua(ua)
    (platform, platform_version) = _get_desktop_platform(ua)

    headers = {
        "User-Agent": ua,
        "Accept": accept,
        "Accept-Encoding": accept_encoding,
        "Accept-Language": accept_language,
        "sec-ch-ua": sec_ch_ua,
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": platform,
        "sec-ch-ua-platform-version": platform_version,
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "Connection": "keep-alive",
    }
    return headers
