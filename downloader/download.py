import logging
import aiohttp
from databasedb import *
import re
from useragent import fake_agent


# async def counts(views):
#     views = int(views)
#     if views >= 1000000:
#         return f"{views / 1000000:.1f}M"
#     if views >= 1000:
#         return f"{views / 1000:.1f}K"
#     return str(views)


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

# async def insta_user_data(language: str, link: str, session: aiohttp.ClientSession) -> any:
#     try:
#         async with session.post(INSTA_API, data={'q': f"https://www.instagram.com/{link}/", 't': 'media',
#                                                  'html': 'cs'}) as response:
#             content = await response.json()
#             if 'url' not in content:
#                 return None, "Invalid response from the Instagram API"
#             async with session.get(f"{content['url']}?__a=1&__d=dis") as json_response:
#                 json_data = await json_response.json()
#                 user = json_data.get('graphql', {}).get('user')
#                 if not user:
#                     return None, "User data not found"
#                 user_id = user.get('id', '')
#                 biography = user.get('biography', '')
#                 title = user.get('bio_links', [{}])[0].get('title', '') if user.get('bio_links', [{}][0]) else None
#                 followers = await counts(user.get('edge_followed_by', {}).get('count'))
#                 following = await counts(user.get('edge_follow', {}).get('count'))
#                 username = user.get('username', '')
#                 full_name = user.get('full_name', '')
#                 profile_pic = user.get('profile_pic_url_hd', '')
#                 posts_count = user.get('edge_owner_to_timeline_media', {}).get('count')
#                 total_likes_count = await counts(
#                     sum(int(i.get('node', {}).get('edge_liked_by', {}).get('count', 0)) for i in
#                         user.get('edge_owner_to_timeline_media', {}).get('edges', [])))
#                 total_comments_count = await counts(sum(
#                     int(i.get('node', {}).get('edge_media_to_comment', {}).get('count', 0)) for i in
#                     user.get('edge_owner_to_timeline_media', {}).get('edges', [])))
#                 user_data = ""
#                 language_dict = select_lang_user_data.get(language, {})
#                 user_data += f"<b>🆔  {language_dict.get('id', '').format(user_id=user_id)}</b>"
#                 username = f"<a href='https://www.instagram.com/{username}'>{username}</a>"
#                 user_data += f"<b>👤  {language_dict.get('username', '').format(username=username)}</b>"
#                 user_data += f"👤  {language_dict.get('full_name', '').format(full_name=full_name)}"
#                 user_data += f"💬  {language_dict.get('biography', '').format(biography=biography)}"
#                 if title:
#                     user_data += f"💬  {language_dict.get('title', '').format(title=title)}"
#                 user_data += f"<b>📊  {language_dict.get('posts_count', '').format(posts_count=posts_count)}</b>"
#                 user_data += f"<b>👥  {language_dict.get('followers', '').format(followers=followers)}</b>"
#                 user_data += f"<b>👤  {language_dict.get('following', '').format(following=following)}</b>"
#                 user_data += f"<b>❤  {language_dict.get('total_likes_count', '').format(total_likes_count=total_likes_count)}</b>"
#                 user_data += f"<b>💬  {language_dict.get('total_comments_count', '').format(total_comments_count=total_comments_count)}</b>"
#                 return profile_pic, user_data
#     except Exception as e:
#         return None, str(e)

#
# async def insta_video_data(link: str, session: aiohttp.ClientSession) -> any:
#     async with session.post(INSTA_API, data={'q': link, 't': 'media', 'html': 'cs'}) as response:
#         content = await response.json()
#         async with session.get(f"{content['url']}?__a=1&__d=dis",
#                                headers={'User-Agent': fake_agent.get_random_user_agent()}) as json_response:
#             json_data = await json_response.json()
#             user = json_data.get('graphql', {}).get('shortcode_media ')
#             if user:
#                 username = user.get('edge_media_to_tagged_user', {}).get('edges', [{}])[0].get('node', {}).get(
#                     'user', {}).get('username')
#             return username
