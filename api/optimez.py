import asyncio
import hashlib
import logging
import random

import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://getindevice.com/wp-json/aio-dl/video-data/"


def get_proxy():
    return "http://username:password@proxyserver:port"


def get_useragent():
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"


class InstagramAPI:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=15)

    async def instagram_downloader(self, link: str):
        for _ in range(2):
            proxy = get_proxy()
            user_agent = get_useragent()
            token = hashlib.sha256(str(random.random()).encode()).hexdigest()
            proxies = {"http": proxy, "https": proxy}
            proxies = {
                "http://": httpx.AsyncHTTPTransport(proxy=proxy),
                "https://": httpx.AsyncHTTPTransport(proxy=proxy),
            }
            data = {'url': link, 'token': token}
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "https://getindevice.com/",
                "User-Agent": user_agent,
                "Sec-CH-UA": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
                "Sec-CH-UA-Mobile": "?0",
                "Sec-CH-UA-Platform": '"Windows"',
            }

            try:
                response = await self.client.post(url=BASE_URL, data=data, headers=headers, )
                if response.status_code == 200:
                    return response.json()
            except httpx.RequestError:
                await asyncio.sleep(1)
        return None

    async def close(self):
        await self.client.aclose()


async def main():
    api = InstagramAPI()
    result = await api.instagram_downloader("https://www.instagram.com/p/DAhP1RlO-dh")
    print(result)
    await api.close()


asyncio.run(main())
