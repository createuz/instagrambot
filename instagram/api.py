import time, re, asyncio, httpx
from typing import Union, Tuple
from data import *
from data.settings import headers
from useragent.user_agent import fake_agent


class InstagramAPI:

    def __init__(self):
        self.client = httpx.AsyncClient()
        self.headers = headers
        self.cache = {}

    async def instagram_downloader(self, vid: str) -> Union[list, None]:
        try:
            response = await self.client.get(f'https://www.instagram.com/p/{vid}/?__a=1&__d=dis', headers=self.headers)
            items = response.json().get('items', [{}])[0]
            is_carousel = items.get('product_type') == 'carousel_container'
            get_url = lambda item, key: next(iter(item.get(key, [{}])), {}).get('url')
            urls = [get_url(i, 'video_versions') or get_url(i.get('image_versions2', {}), 'candidates')
                    for i in items.get('carousel_media', [{}])] if is_carousel else [
                get_url(items, 'video_versions') or get_url(items.get('image_versions2', {}), 'candidates')]
            return urls
        except Exception as e:
            logger.error(f"• Download error: {e}")
            return None

    async def counts(self, views):
        views = int(views)
        if views >= 1000000:
            return f"{views / 1000000:.1f}M"
        elif views >= 1000:
            return f"{views / 1000:.1f}K"
        else:
            return str(views)

    async def instagram_user_data(self, link: str) -> Union[Tuple[str], None]:
        cached_data = self.cache.get(link, {})
        if cached_data.get('timestamp', 0) >= time.time() - 2629746:
            return cached_data.get('result')
        try:
            response = await self.client.get(f'{link}?__a=1&__d=dis', headers=self.headers)
            user = response.json().get('graphql', {}).get('user', {})
            if not user:
                return None
            user_id, username, full_name, biography = (user.get('id', ''), user.get('username', ''),
                                                       user.get('full_name', ''), user.get('biography', ''))
            bio_links = ' • '.join(
                [f"<a href='{link.get('url', '')}'>{link.get('title', '')}</a>" for link in user.get('bio_links', [])])
            followers = await self.counts(user.get('edge_followed_by', {}).get('count', ''))
            following = await self.counts(user.get('edge_follow', {}).get('count', ''))
            posts_count = user.get('edge_owner_to_timeline_media', {}).get('count', '')
            total_likes_count = await self.counts(
                sum(int(i.get('node', {}).get('edge_liked_by', {}).get('count', 0)) for i in
                    user.get('edge_owner_to_timeline_media', {}).get('edges', [])))
            total_comments_count = await self.counts(sum(
                int(i.get('node', {}).get('edge_media_to_comment', {}).get('count', 0)) for i in
                user.get('edge_owner_to_timeline_media', {}).get('edges', [])))
            user_data = f"🆔  <b>ID:</b>  {user_id}\n" if user_id else ""
            user_data += f"👤  <b>Foydalanuvchi nomi:</b> <a href='https://www.instagram.com/{username}'> <b>{username}</b></a> \n" if username else ""
            user_data += f"👤  <b>Toʻliq ismi:</b>  {full_name}\n" if full_name else ""
            user_data += f"💬  <b>Biografiyasi:</b>  {biography}\n" if biography else ""
            user_data += f"🔗  <b>Links:</b>  {bio_links}\n" if bio_links else ""
            user_data += f"📊  <b>Postlar soni:</b>  {posts_count}\n" if posts_count else ""
            user_data += f"👥  <b>Kuzatuvchilari:</b>  {followers}\n" if followers else ""
            user_data += f"👤  <b>Obuna bo'lgan:</b>  {following}\n" if following else ""
            user_data += f"❤  <b>Likes:</b>  {total_likes_count}\n" if total_likes_count else ""
            user_data += f"💬  <b>Comments:</b>  {total_comments_count}\n" if total_comments_count else ""
            data = (user.get('profile_pic_url_hd', ''), user_data)
            self.cache[link] = {'result': data, 'timestamp': time.time()}
            return data
        except Exception as e:
            logger.error(f"• User data error: {e}")
            return None

    async def instagram_stories(self, link: str) -> Union[list, None]:
        try:
            response = await self.client.post('https://savefree.app/api/ajaxSearch',
                                              data={'q': link, 't': 'media', 'lang': 'en'},
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
            return urls.extend(lazy_urls)
        except Exception as e:
            logger.exception("Error while inserting video data: %s", e)
            return None

# tests = InstagramAPI()
# print(asyncio.run(tests.instagram_stories('https://instagram.com/stories/abdullaziz_mee/3246259030128328437?utm_source=ig_story_item_share&igshid=NmJiYWZiY2E0Mg==')))
