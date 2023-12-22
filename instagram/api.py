import time, re, asyncio, httpx
from typing import Union, Tuple, List
from data import headers, logger, INSTA_API
from keyboards import select_lang_user_data
from useragent.user_agent import fake_agent


class InstagramAPI:

    def __init__(self):
        self.client = httpx.AsyncClient()
        self.headers = headers()
        self.cache = {}
        self.url_patterns = {
            'video': re.compile(r'href="(https?://download[^"]+)"'),
            'image': re.compile(r'<div class="download-items__thumb">\s*<img src="([^"]+)"[^>]*>\s*<span '
                                r'class="format-icon"><i class="icon (icon-dlimage|icon-dlvideo)"></i></span>\s*</div>'),
            'lazy': re.compile(r'<img class="lazy" src="/imgs/loader.gif" data-src="([^"]+)"[^>]*>')
        }

    async def close_session(self):
        await self.client.aclose()

    async def instagram_downloader(self, vid: str) -> Union[list, None]:
        try:
            response = await self.client.get(f'https://www.instagram.com/p/C0jqndJii3V/?__a=1&__d=dis',
                                             headers=self.headers)
            items = response.json().get('items', [{}])[0]
            is_carousel = items.get('product_type') == 'carousel_container'
            get_url = lambda item, key: next(iter(item.get(key, [{}])), {}).get('url')
            return [get_url(i, 'video_versions') or get_url(i.get('image_versions2', {}), 'candidates')
                    for i in items.get('carousel_media', [{}])] if is_carousel else [
                get_url(items, 'video_versions') or get_url(items.get('image_versions2', {}), 'candidates')]
        except Exception as e:
            logger.exception(f"• Download error: {e}")
            return None

    @staticmethod
    async def counts(views):
        views = int(views)
        if views >= 1000000:
            return f"{views / 1000000:.1f}M"
        elif views >= 1000:
            return f"{views / 1000:.1f}K"
        else:
            return str(views)

    async def instagram_user_data(self, language: str, link: str) -> Union[Tuple[str], None]:
        try:
            url = link.replace('@', '')
            response = await self.client.get(f'https://www.instagram.com/{url}/?__a=1&__d=dis',
                                             headers=self.headers)
            if response.status_code != 200:
                return None, None
            user = response.json().get('graphql', {}).get('user', {})
            user_id, username, full_name, biography = (user.get('id', ''), user.get('username', ''),
                                                       user.get('full_name', ''), user.get('biography', ''))
            bio_links = [f"<a href='{link.get('url')}'>{link.get('title', '• link')}</a>" for link in
                         user.get('bio_links', []) if link.get('url')]
            bio_links = ' • '.join(bio_links) if bio_links else ''
            followers = await self.counts(user.get('edge_followed_by', {}).get('count', ''))
            following = await self.counts(user.get('edge_follow', {}).get('count', ''))
            posts_count = user.get('edge_owner_to_timeline_media', {}).get('count', '')
            total_likes_count = await self.counts(
                sum(int(i.get('node', {}).get('edge_liked_by', {}).get('count', 0)) for i in
                    user.get('edge_owner_to_timeline_media', {}).get('edges', [])))
            total_comments_count = await self.counts(
                sum(int(i.get('node', {}).get('edge_media_to_comment', {}).get('count', 0)) for i in
                    user.get('edge_owner_to_timeline_media', {}).get('edges', [])))
            language_dict = select_lang_user_data.get(language, {})
            username = f"<a href='https://www.instagram.com/{username}'><b>{username}</b></a>" if username else ""
            user_data = f"🆔  {language_dict.get('id', '').format(user_id=str(user_id))}" if user_id else ""
            user_data += f"👤  {language_dict.get('username', '').format(username=username)}" if username else ""
            user_data += f"👤  {language_dict.get('full_name', '').format(full_name=full_name)}" if full_name else ""
            user_data += f"💬  {language_dict.get('biography', '').format(biography=biography)}" if biography else ""
            user_data += f"🔗  {language_dict.get('links', '').format(links=bio_links)}" if bio_links else ""
            user_data += f"📊  {language_dict.get('posts_count', '').format(posts_count=posts_count)}" if posts_count else ""
            user_data += f"👥  {language_dict.get('followers', '').format(followers=followers)}" if followers else ""
            user_data += f"👤  {language_dict.get('following', '').format(following=following)}" if following else ""
            user_data += f"❤  {language_dict.get('total_likes_count', '').format(total_likes_count=total_likes_count)}" if total_likes_count else ""
            user_data += f"💬  {language_dict.get('total_comments_count', '').format(total_comments_count=total_comments_count)}" if total_comments_count else ""
            return user.get('profile_pic_url_hd'), user_data
        except Exception as e:
            logger.exception(f"• User data error: {e}")
            return None

    async def instagram_user_stories(self, username: str) -> Union[list, None]:
        try:
            response = await self.client.get(
                f'https://storiesig.info/api/ig/story?url=https://www.instagram.com/stories/{username}')
            get_url = lambda item, key: next(iter(item.get(key, [{}])), {}).get('url')
            return [get_url(item, 'video_versions') or get_url(item.get('image_versions2', {}), 'candidates')
                    for item in response.json().get('result', [{}])]
        except Exception as e:
            logger.exception(f"• User stories error: {e}")
            return None

    async def instagram_downloader_stories(self, link: str) -> Union[List[str], None]:
        try:
            response = await self.client.post(INSTA_API, data={'q': link, 't': 'media', 'lang': 'en'},
                                              headers={'User-Agent': fake_agent.get_random_user_agent()})
            content = response.json()
            html = content.get('data')
            if not html:
                return None

            async def fetch_urls(pattern, html):
                if pattern == self.url_patterns.get('image'):
                    return [match.group(1) for match in pattern.finditer(html) if match.group(2) == 'icon-dlimage']
                return pattern.findall(html)

            tasks = [fetch_urls(pattern, html) for pattern in self.url_patterns.values()]
            results = await asyncio.gather(*tasks)
            return [url for result in results for url in result if 'jpg_e15' not in url]
        except Exception as e:
            logger.exception("Unexpected error: %s", e)
            return None
    # async def instagram_downloader_stories(self, link: str) -> Union[list, None]:
    #     try:
    #         response = await self.client.post(INSTA_API, data={'q': link, 't': 'media', 'lang': 'en'},
    #                                           headers={'User-Agent': fake_agent.get_random_user_agent()})
    #         content = response.json()
    #         html = content.get('data')
    #         urls = []
    #         video_urls = re.findall(r'href="(https?://download[^"]+)"', html)
    #         urls.extend(video_urls)
    #         pattern = r'<div class="download-items__thumb">\s*<img src="([^"]+)"[^>]*>\s*<span class="format-icon"><i class="icon (icon-dlimage|icon-dlvideo)"></i></span>\s*</div>'
    #         image_urls = [match.group(1) for match in re.finditer(pattern, html) if
    #                       match.group(2) == 'icon-dlimage']
    #         urls.extend(image_urls)
    #         pattern = r'<img class="lazy" src="/imgs/loader.gif" data-src="([^"]+)"[^>]*>'
    #         lazy_urls = re.findall(pattern, html)
    #         urls.extend(lazy_urls)
    #         return urls
    #     except Exception as e:
    #         logger.exception("Error while inserting video data: %s", e)
    #         return None


# 'https://www.instagram.com/abdullaziz_mee/?e=0ddc5e7e-6c7a-4084-85e4-ca7c2eecebc5&g=5'
#
# tests = InstagramAPI()
# print(asyncio.run(tests.instagram_downloader_stories('https://www.instagram.com/p/C0jqndJii3V')))
