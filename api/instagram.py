import asyncio

import httpx

from data import logger

headerss = {
    's': 'ps_n=1;datr=FEamZ_F8Uy6Bnsf65YMOsmt2;ig_nrcb=1;ds_user_id=49596389611;csrftoken=ZxkOQYjwK6ku97Sd5l9NF31SWqRnLwkv;ig_did=85DB4704-1DE7-49DE-9CCA-575F5DFC4C37;ps_l=1;wd=1536x742;mid=Z7BKLwALAAHqOBTFtZGaM97Q-w9J;sessionid=49596389611%3A6M3mGknfAj1yJn%3A5%3AAYeFNQt0euQduP71_3BANNNIX2eNkqOnOGzPXdbsUA;dpr=1.25;rur="RVA\05449596389611\0541772200010:01f787b22794ed157ce0f9c04e23b819f778999e16f6d43190bc3c89b0a3ba1cd47df3c9"'
}
headers = {
    "authority": "www.instagram.com",
    "method": "GET",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "cookie": 'ps_n=1;datr=FEamZ_F8Uy6Bnsf65YMOsmt2;ig_nrcb=1;ds_user_id=49596389611;csrftoken=ZxkOQYjwK6ku97Sd5l9NF31SWqRnLwkv;ig_did=85DB4704-1DE7-49DE-9CCA-575F5DFC4C37;ps_l=1;wd=1536x742;mid=Z7BKLwALAAHqOBTFtZGaM97Q-w9J;sessionid=49596389611%3A6M3mGknfAj1yJn%3A5%3AAYeFNQt0euQduP71_3BANNNIX2eNkqOnOGzPXdbsUA;dpr=1.25;rur="RVA\05449596389611\0541772200010:01f787b22794ed157ce0f9c04e23b819f778999e16f6d43190bc3c89b0a3ba1cd47df3c9"',
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
}


class InstagramAPI:

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30)
        self.cache = {}

    async def instagram_downloader(self, vid: str):
        try:
            response = await self.client.get(f'https://www.instagram.com/p/{vid}/?__a=1&__d=dis', headers=headers)
            items = response.json().get('items', [{}])[0]
            is_carousel = items.get('product_type') == 'carousel_container'
            get_url = lambda item, key: next(iter(item.get(key, [{}])), {}).get('url')
            return [get_url(i, 'video_versions') or get_url(i.get('image_versions2', {}), 'candidates')
                    for i in items.get('carousel_media', [{}])] if is_carousel else [
                get_url(items, 'video_versions') or get_url(items.get('image_versions2', {}), 'candidates')]
        except Exception as e:
            logger.exception(f"• Download error: {e}")
            return None
    #
    # @staticmethod
    # async def counts(views):
    #     views = int(views)
    #     if views >= 1000000:
    #         return f"{views / 1000000:.1f}M"
    #     elif views >= 1000:
    #         return f"{views / 1000:.1f}K"
    #     else:
    #         return str(views)
    #
    # async def instagram_user_data(self, language: str, link: str):
    #     try:
    #         url = link.replace('@', '')
    #         response = await self.client.get(f'https://www.instagram.com/{url}/?__a=1&__d=dis')
    #         if response.status_code != 200:
    #             return None, None
    #         user = response.json().get('graphql', {}).get('user', {})
    #         user_id, username, full_name, biography = (user.get('id', ''), user.get('username', ''),
    #                                                    user.get('full_name', ''), user.get('biography', ''))
    #         bio_links = [f"<a href='{link.get('url')}'>{link.get('title', '• link')}</a>" for link in
    #                      user.get('bio_links', []) if link.get('url')]
    #         bio_links = ' • '.join(bio_links) if bio_links else ''
    #         followers = await self.counts(user.get('edge_followed_by', {}).get('count', ''))
    #         following = await self.counts(user.get('edge_follow', {}).get('count', ''))
    #         posts_count = user.get('edge_owner_to_timeline_media', {}).get('count', '')
    #         total_likes_count = await self.counts(
    #             sum(int(i.get('node', {}).get('edge_liked_by', {}).get('count', 0)) for i in
    #                 user.get('edge_owner_to_timeline_media', {}).get('edges', [])))
    #         total_comments_count = await self.counts(
    #             sum(int(i.get('node', {}).get('edge_media_to_comment', {}).get('count', 0)) for i in
    #                 user.get('edge_owner_to_timeline_media', {}).get('edges', [])))
    #         # language_dict = select_lang_user_data.get(language, {})
    #         language_dict = {}
    #         username = f"<a href='https://www.instagram.com/{username}'><b>{username}</b></a>" if username else ""
    #         user_data = f"🆔  {language_dict.get('id', '').format(user_id=str(user_id))}" if user_id else ""
    #         user_data += f"👤  {language_dict.get('username', '').format(username=username)}" if username else ""
    #         user_data += f"👤  {language_dict.get('full_name', '').format(full_name=full_name)}" if full_name else ""
    #         user_data += f"💬  {language_dict.get('biography', '').format(biography=biography)}" if biography else ""
    #         user_data += f"🔗  {language_dict.get('links', '').format(links=bio_links)}" if bio_links else ""
    #         user_data += f"📊  {language_dict.get('posts_count', '').format(posts_count=posts_count)}" if posts_count else ""
    #         user_data += f"👥  {language_dict.get('followers', '').format(followers=followers)}" if followers else ""
    #         user_data += f"👤  {language_dict.get('following', '').format(following=following)}" if following else ""
    #         user_data += f"❤  {language_dict.get('total_likes_count', '').format(total_likes_count=total_likes_count)}" if total_likes_count else ""
    #         user_data += f"💬  {language_dict.get('total_comments_count', '').format(total_comments_count=total_comments_count)}" if total_comments_count else ""
    #         return user.get('profile_pic_url_hd'), user_data
    #     except Exception as e:
    #         logger.exception(f"• User data error: {e}")
    #         return None

# 'https://www.instagram.com/p/DGVMuEHsclg/'
instagram_api = InstagramAPI()
# print(asyncio.run(instagram_api.instagram_downloader('DGVMuEHsclg')))
