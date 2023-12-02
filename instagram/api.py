import time, re, asyncio, httpx
from typing import Union, Tuple
from data import headers, logger
from keyboards import select_lang_user_data
from useragent.user_agent import fake_agent


class InstagramAPI:

    def __init__(self):
        self.client = httpx.AsyncClient()
        self.headers = headers()
        self.cache = {}

    async def instagram_downloader(self, vid: str) -> Union[list, None]:
        try:
            response = await self.client.get(f'https://www.instagram.com/p/{vid}/?__a=1&__d=dis', headers=self.headers)
            items = response.json().get('items', [{}])[0]
            is_carousel = items.get('product_type') == 'carousel_container'
            get_url = lambda item, key: next(iter(item.get(key, [{}])), {}).get('url')
            return [get_url(i, 'video_versions') or get_url(i.get('image_versions2', {}), 'candidates')
                    for i in items.get('carousel_media', [{}])] if is_carousel else [
                get_url(items, 'video_versions') or get_url(items.get('image_versions2', {}), 'candidates')]
        except Exception as e:
            logger.exception(f"• Download error: {e}")
            return None

    async def counts(self, views):
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
            user_data = f"🆔  {language_dict.get('id', '').format(user_id=user_id)}" if user_id else ""
            user_data += f"👤  {language_dict.get('username', '').format(username=username)}" if username else ""
            user_data += f"👤  {language_dict.get('full_name', '').format(full_name=full_name)}" if full_name else ""
            user_data += f"💬  {language_dict.get('biography', '').format(biography=biography)}" if biography else ""
            user_data += f"🔗  {language_dict.get('links', '').format(links=bio_links)}" if bio_links else ""
            user_data += f"📊  {language_dict.get('posts_count', '').format(posts_count=posts_count)}" if posts_count else ""
            user_data += f"👥  {language_dict.get('followers', '').format(followers=followers)}" if followers else ""
            user_data += f"👤  {language_dict.get('following', '').format(following=following)}" if following else ""
            user_data += f"❤  {language_dict.get('total_likes_count', '').format(total_likes_count=total_likes_count)}" if total_likes_count else ""
            user_data += f"💬  {language_dict.get('total_comments_count', '').format(total_comments_count=total_comments_count)}" if total_comments_count else ""
            return user
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


# 'https://www.instagram.com/abdullaziz_mee/?e=0ddc5e7e-6c7a-4084-85e4-ca7c2eecebc5&g=5'
#
# tests = InstagramAPI()
# print(asyncio.run(tests.instagram_user_data('Uzbek', 'sh.coder')))
