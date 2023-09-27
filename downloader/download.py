import logging
import aiohttp
from databasedb import *
import re
from useragent import fake_agent


async def instagram_downloader_photo_video(link: str, session: aiohttp.ClientSession) -> any:
    try:
        async with session.post(INSTA_API, data={'q': link, 't': 'media', 'lang': 'en'},
                                headers={'User-Agent': fake_agent.get_random_user_agent()}) as response:
            content = await response.json()
            html = content['data']
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
