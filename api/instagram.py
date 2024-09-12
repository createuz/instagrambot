import asyncio
import re
from io import StringIO
from typing import Union, List
import httpx
from bs4 import BeautifulSoup
from lxml import etree

from settings import logger, fake_agent, config
from pyquery import PyQuery as pq


class InstagramAPI:

    def __init__(self):
        self.client = httpx.AsyncClient(headers={'User-Agent': fake_agent.get_random_user_agent()}, timeout=30)
        self.cache = {}

    async def instagram_download_stories(self, username: str) -> Union[list, None]:
        try:
            response = await self.client.get(
                f'https://storiesig.info/api/ig/story?url=https://www.instagram.com/stories/{username}')
            get_url = lambda item, key: next(iter(item.get(key, [{}])), {}).get('url')
            return [get_url(item, 'video_versions') or get_url(item.get('image_versions2', {}), 'candidates')
                    for item in response.json().get('result', [{}])]
        except Exception as e:
            logger.exception(f"• User stories error: {e}")
            return None

    async def get_data_insta(self, api_url: str, link: str) -> Union[list, None]:
        try:
            response = await self.client.post(api_url, data={'q': link, 't': 'media', 'lang': 'en'})
            if response.status_code == 200:
                urls = re.findall(r'https://(?:ig|download)\S+', response.json().get('data', ''))
                return [url.split('"')[0] for url in urls if 'jpg_e15' not in url]
            else:
                return None
        except Exception as e:
            return None

    async def instagram_downloader(self, link: str) -> Union[list, None]:
        try:
            for api_url in config.API_LIST:
                results = await self.get_data_insta(api_url, link)
                if results:
                    return results
            return None
        except Exception as e:
            return None

    # async def tiktok_downloader(self, link: str) -> Union[list, None]:
    #     try:
    #         response = await self.client.post(
    #             'https://tikwm.com/api/',
    #             data={'url': link, 'count': 12, 'cursor': 0, 'web': 1, 'hd': 1}
    #         )
    #         return response.json()
    #     except Exception as e:
    #         logger.exception(f"• User stories error: {e}")
    #         return None

    # async def tiktok_downloader(self, link: str) -> Union[list, None]:
    #     try:
    #         response = await self.client.post(
    #             'https://ssstik.io/abc?url=dl',
    #             data={'id': link, 'locale': 'en', 'tt': 'ODNwWFk2'}
    #         )
    #         return response.text
    #     except Exception as e:
    #         logger.exception(f"• User stories error: {e}")
    #         return None

    # async def likee_downloader(self, link: str) -> any:
    #     try:
    #         response = await self.client.post('https://likeedownloader.com/process', data={'id': link, 'locale': 'en'})
    #         parser = etree.HTMLParser()
    #         tree = etree.parse(StringIO(response.text), parser)
    #         links = tree.xpath('//a/@href')
    #         return links[0].replace("\\/", "/").replace('\\"', ''), links[1].replace("\\/", "/").replace('\\"', '')
    #     except Exception as e:
    #         logger.exception("Error while inserting video data: %s", e)
    #         return None


instagram_api = InstagramAPI()
