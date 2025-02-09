import asyncio

import httpx

from data import logger

headers = {
    "authority": "www.instagram.com",
    "method": "GET",
    "path": "/p/DFp17y5MymE/?__a=1&__d=dis",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "uz-UZ,uz;q=0.9,en-US;q=0.8,en;q=0.7",
    "cookie": 'csrftoken=zYz6E2hZIsHSBv8gzjAjwU; datr=FEamZ_F8Uy6Bnsf65YMOsmt2; ig_did=85DB4704-1DE7-49DE-9CCA-575F5DFC4C37; dpr=1.25; wd=1536x742; mid=Z6ZGFQALAAG1hGuqUddzT3gEHXR-; ig_nrcb=1; ps_l=1; ps_n=1; sessionid=49596389611%3Ax2XBrOAoJvXeFj%3A5%3AAYe6F-G59il7VQ3tdHsdijAfdGS9CO0PkXfaZph7Ww; ds_user_id=49596389611; rur="NCG,49596389611,1770583561:01f7cfee8fc46d3ebcb410263533e3c0317c409aa1c6aec867cb2a096e10af0ece6fcdb3"',
    "dpr": "1.25",
    "priority": "u=0, i",
    "sec-ch-prefers-color-scheme": "dark",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "sec-ch-ua-full-version-list": '"Not(A:Brand";v="99.0.0.0", "Google Chrome";v="133.0.6943.59", "Chromium";v="133.0.6943.59"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"Windows"',
    "sec-ch-ua-platform-version": '"19.0.0"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "viewport-width": "1536"
}


class InstagramAPI:

    def __init__(self):
        self.client = httpx.AsyncClient(headers=headers, timeout=30)

    async def instagram_downloader(self, vid: str):
        try:
            response = await self.client.get(f'https://www.instagram.com/p/{vid}/?__a=1&__d=dis')
            items = response.json().get('items', [{}])[0]
            is_carousel = items.get('product_type') == 'carousel_container'
            get_url = lambda item, key: next(iter(item.get(key, [{}])), {}).get('url')
            return [get_url(i, 'video_versions') or get_url(i.get('image_versions2', {}), 'candidates')
                    for i in items.get('carousel_media', [{}])] if is_carousel else [
                get_url(items, 'video_versions') or get_url(items.get('image_versions2', {}), 'candidates')]
        except Exception as e:
            logger.exception(f"• Download error: {e}")
            return None


instagram_api = InstagramAPI()
print(asyncio.run(instagram_api.instagram_downloader('DFp17y5MymE')))
