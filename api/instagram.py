import asyncio
import hashlib

import httpx

from data import logger


class InstagramAPI:

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30)
        self.base_url = 'https://getindevice.com/wp-json/aio-dl/video-data'

    async def instagram_downloader(self, link: str):
        try:
            token = hashlib.sha256("secret_key".encode()).hexdigest()
            response = await self.client.post(url=self.base_url, data={'url': link, 'token': token})
            items = response.json()
            return items
        except Exception as e:
            logger.exception(f"• Download error: {e}")
            return None


instagram_api = InstagramAPI()
# print(asyncio.run(instagram_api.instagram_downloader('https://www.instagram.com/p/DAhP1RlO-dh')))
