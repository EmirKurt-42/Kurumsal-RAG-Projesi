"""
Adapter: IWebFetcher'in requests + robots.txt ile gerceklestirimi.
TUM gateway'ler bu SINIFIN AYNI ORNEGINI (instance) paylasir - boylece
robots.txt onbellegi ve rate-limit tum siteler icin ortak calisir.

ONEMLI: urllib.robotparser KULLANMIYORUZ - Allow+Disallow kombinasyonunu
bazi durumlarda yanlis yorumladigi tespit edildi (merhabahaber.com'un
"Allow: / / Disallow: /api" kuralinda alakasiz sayfalari bile yanlislikla
engelliyordu). Kendi basit "en uzun eslesen kural kazanir" mantigimizi
kullaniyoruz.
"""
import socket
import time
from typing import Optional
from urllib.parse import urlparse

import requests

from src.application.interfaces import IWebFetcher

USER_AGENT = "KonyaVeriBotu/1.0 (staj projesi; iletisim: ogrenci@ornek.com)"
REQUEST_DELAY_SECONDS = 1.0
ROBOTS_TIMEOUT_SECONDS = 5


def _parse_robots_rules(robots_text: str):
    rules = []
    applies_to_us = False

    for raw_line in robots_text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue

        key, _, value = line.partition(":")
        key = key.strip().lower()
        value = value.strip()

        if key == "user-agent":
            applies_to_us = (value == "*")
        elif applies_to_us and key == "allow":
            rules.append((value, True))
        elif applies_to_us and key == "disallow":
            rules.append((value, False))

    return rules


class RequestsFetcher(IWebFetcher):
    def __init__(self) -> None:
        self._rules_cache: dict = {}

    def _get_rules(self, url: str):
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        if domain in self._rules_cache:
            return self._rules_cache[domain]

        eski_timeout = socket.getdefaulttimeout()
        rules = []
        try:
            socket.setdefaulttimeout(ROBOTS_TIMEOUT_SECONDS)
            response = requests.get(domain + "/robots.txt", timeout=ROBOTS_TIMEOUT_SECONDS)
            if response.status_code == 200:
                rules = _parse_robots_rules(response.text)
        except Exception:
            rules = []
        finally:
            socket.setdefaulttimeout(eski_timeout)

        self._rules_cache[domain] = rules
        return rules

    def _can_fetch(self, url: str) -> bool:
        rules = self._get_rules(url)
        if not rules:
            return True

        path = urlparse(url).path or "/"
        best_match_length = -1
        allowed = True
        for rule_path, is_allow in rules:
            if rule_path and path.startswith(rule_path):
                if len(rule_path) > best_match_length:
                    best_match_length = len(rule_path)
                    allowed = is_allow

        return allowed

    def fetch(self, url: str, check_robots: bool = True) -> Optional[str]:
        if check_robots and not self._can_fetch(url):
            return None

        headers = {"User-Agent": USER_AGENT}
        try:
            response = requests.get(url, headers=headers, timeout=15)
        except requests.exceptions.RequestException:
            return None

        time.sleep(REQUEST_DELAY_SECONDS)

        if response.status_code != 200:
            return None

        response.encoding = response.apparent_encoding
        return response.text