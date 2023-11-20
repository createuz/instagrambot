import asyncio, logging, time, httpx, re
from typing import Union
from databasedb import *
from useragent import fake_agent

cache = {}


async def download_media(link: str) -> Union[list, None]:
    cached_data = cache.get(link, {})
    if cached_data.get('timestamp', 0) >= time.time() - 2629746:
        return cached_data.get('result')
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(INSTA_API, data={'q': link, 't': 'media', 'lang': 'en'},
                                         headers={'User-Agent': fake_agent.get_random_user_agent()})
        urls = []
        html = response.json().get('data', '')
        video_urls = re.findall(r'href="(https?://download[^"]+)"', html)
        urls.extend(video_urls)
        # patterns = re.compile(
        #     r'<div class="download-items__thumb">\s*<img src="([^"]+)"[^>]*>\s*<span class="format-icon"><i class="icon (icon-dlimage|icon-dlvideo)"></i></span>\s*</div>|<img class="lazy" src="/imgs/loader.gif" data-src="([^"]+)"[^>]*>')
        # matches = patterns.findall(html)
        # urls.extend(x for match in matches for x in filter(lambda x: x and x.startswith('https://'), match))
        cache[link] = {'result': urls, 'timestamp': time.time()}
        for i in urls:
            print(i)
    except Exception as e:
        logging.exception("Error while inserting video data: %s", e)
        return None


# print(asyncio.run(download_media('https://www.instagram.com/p/CqtAnkbu-6M/')))
print(asyncio.run(download_media('https://www.instagram.com/p/CyEDQ5ktCfo/')))


async def insta_down(link: str) -> any:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(INSTA_API, data={'q': link, 't': 'media', 'lang': 'en'},
                                         headers={'User-Agent': fake_agent.get_random_user_agent()})
            html = response.json().get('data', '')
            urls = []
            video_urls = re.findall(r'href="(https?://download[^"]+)"', html)
            urls.extend(video_urls)
            pattern = r'<div class="download-items__thumb">\s*<img src="([^"]+)"[^>]*>\s*<span class="format-icon"><i class="icon (icon-dlimage|icon-dlvideo)"></i></span>\s*</div>'
            image_urls = [match.group(1) for match in re.finditer(pattern, html) if
                          match.group(2) == 'icon-dlimage']
            urls.extend(image_urls)
            pattern = r'<img class="lazy" src="/imgs/loader.gif" data-src="([^"]+)"[^>]*>'
            lazy_urls = re.findall(pattern, html)
            urls.extend(lazy_urls)
            return urls
    except Exception as e:
        logging.exception("Error while inserting video data: %s", e)
        return None
# print(asyncio.run(insta_down('https://www.instagram.com/p/CyEDQ5ktCfo/')))