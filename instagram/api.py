import re
from typing import Union
from data import *
import httpx


class InstagramAPI:

    def __init__(self):
        self.client = httpx.AsyncClient()
        self.cache = {}

    async def close_session(self):
        await self.client.aclose()

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
            response = await self.client.post(api_url, data={'q': link, 't': 'media', 'lang': 'en'},
                                              headers={'User-Agent': fake_agent.get_random_user_agent()})
            if response.status_code == 200:
                urls = re.findall(r'https://(?:ig|download)\S+', response.json().get('data', ''))
                return [url.split('"')[0] for url in urls if 'jpg_e15' not in url]
            else:
                return None
        except Exception as e:
            return None

    async def instagram_downloader(self, link: str) -> Union[list, None]:
        try:
            for api_url in INSTA_API_LIST:
                results = await self.get_data_insta(api_url, link)
                if results:
                    return results
            return None
        except Exception as e:
            return None


instagram_api = InstagramAPI()
