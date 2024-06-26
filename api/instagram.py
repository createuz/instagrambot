import asyncio
import re
from typing import Union, List
import httpx

from data import logger, fake_agent, INSTA_API_LIST


class InstagramAPI:

    def __init__(self):
        self.client = httpx.AsyncClient(headers={'User-Agent': fake_agent.get_random_user_agent()})
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
            for api_url in INSTA_API_LIST:
                results = await self.get_data_insta(api_url, link)
                if results:
                    return results
            return None
        except Exception as e:
            return None

    # async def get_data_instas(self, api_url: str, link: str) -> Union[List[str], None]:
    #     try:
    #         response = await self.client.post(
    #             api_url,
    #             data={'q': link, 't': 'media', 'lang': 'en'},
    #             headers={'User-Agent': fake_agent.get_random_user_agent()}
    #         )
    #         if response.status_code == 200:
    #             urls = re.findall(r'https://(?:ig|download)\S+', response.json().get('data'))
    #             return [url.split('"')[0] for url in urls if 'jpg_e15' not in url]
    #     except Exception as e:
    #         return None
    #
    # async def instagram_downloaders(self, link: str) -> Union[List[str], None]:
    #     tasks = [asyncio.create_task(self.get_data_instas(api_url, link)) for api_url in INSTA_API_LIST]
    #     done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    #     result = None
    #     for task in done:
    #         try:
    #             result = task.result()
    #             if result:
    #                 break
    #         except Exception as e:
    #             print(f"Task raised an exception: {e}")
    #             continue
    #     for task in pending:
    #         task.cancel()
    #     return result


instagram_api = InstagramAPI()


# async def main():
#     link = 'https://pin.it/yCWjfPX7L'
#     res = await instagram_api.instagram_downloader(link)
#     print(res)
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
