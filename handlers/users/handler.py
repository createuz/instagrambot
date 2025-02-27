import time

from aiogram import Router, F
from aiogram.types import Message, InputMediaPhoto, InputMediaVideo

from api import instagram_api
from data import bot, logger
from db import User
from handlers.users.langs import langs_text

download_router = Router()


@download_router.message(F.text.regexp(''))
async def send_pinterest_all_media(message: Message):
    link = message.text
    await message.delete()
    language = await User.get_language(message.chat.id)
    try:
        cached_data = instagram_api.cache.get(link, {})
        if cached_data.get('timestamp', 0) >= time.time() - 2629746:
            media = cached_data.get('result')
            if 'mp4' in media:
                return await bot.send_video(
                    chat_id=message.chat.id,
                    video=media,
                    caption=f"<b>📥 {langs_text[language]['saved']} @pintersrobot</b>"
                )
            if 'jpg' in media:
                return await bot.send_photo(
                    chat_id=message.chat.id,
                    photo=media,
                    caption=f"<b>📥 {langs_text[language]['saved']} @pintersrobot</b>"
                )
        wait_msg = await bot.send_message(
            chat_id=message.chat.id,
            text=f"<b>{langs_text.get(language).get('wait')}</b>",
            protect_content=True
        )
        urls = await instagram_api.pinterest_downloader(link=link)
        if urls is None or not urls:
            await wait_msg.delete()
            return await bot.send_message(
                chat_id=message.chat.id,
                text=langs_text.get(language).get('error').format(message.text),
                disable_web_page_preview=True
            )
        if 'mp4' in urls:
            await bot.send_video(
                chat_id=message.chat.id,
                video=urls,
                caption=f"<b>📥 {langs_text[language]['saved']} @pintersrobot</b>"
            )
        if 'jpg' in urls:
            await bot.send_photo(
                chat_id=message.chat.id,
                photo=urls,
                caption=f"<b>📥 {langs_text[language]['saved']} @pintersrobot</b>"
            )
        await wait_msg.delete()
        instagram_api.cache[link] = {'result': urls, 'timestamp': time.time()}
    except Exception as e:
        logger.exception("Error while sending Instagram photo: %s", e)
        return await bot.send_message(
            chat_id=message.chat.id,
            text=langs_text.get(language).get('error').format(message.text),
            disable_web_page_preview=True
        )


@download_router.message(F.text.regexp(r'https?:\/\/(www\.)?instagram\.com\/(reel|p)\/([-_a-zA-Z0-9]{11})'))
async def send_instagram_media(message: Message):
    await message.delete()
    global wait_msg
    language = await User.get_language(chat_id=message.chat.id)
    try:
        cached_data = instagram_api.cache.get(message.text, {})
        if cached_data.get('timestamp', 0) >= time.time() - 2629746:
            media = cached_data.get('result')
            return await bot.send_media_group(chat_id=message.chat.id, media=media)
        wait_msg = await bot.send_message(
            chat_id=message.chat.id,
            text=f"<b>{langs_text.get(language).get('waiting')}</b>",
            protect_content=True
        )
        urls = await instagram_api.instagram_downloader(link=message.text)
        if urls is None or not urls:
            await wait_msg.delete()
            return await bot.send_message(
                chat_id=message.chat.id,
                text=langs_text.get(language).get('error').format(message.text),
                disable_web_page_preview=True
            )
        media = [InputMediaPhoto(url) if 'jpg' in url else InputMediaVideo(url) for url in urls]
        media[-1].caption = f"<b>{langs_text.get(language).get('saved')} 📥</b>"
        await bot.send_media_group(chat_id=message.chat.id, media=media)
        await wait_msg.delete()
        instagram_api.cache[message.text] = {'result': media, 'timestamp': time.time()}
    except Exception as e:
        await wait_msg.delete()
        logger.exception("Error while sending Instagram photo: %s", e)
        return await bot.send_message(
            chat_id=message.chat.id,
            text=langs_text.get(language).get('error').format(message.text),
            disable_web_page_preview=True
        )


@download_router.message(F.text.regexp(r'https?:\/\/(www\.)?api\.com\/(stories)'))
async def send_instagram_media(message: Message):
    await message.delete()
    global wait_msg
    language = await User.get_language(chat_id=message.chat.id)
    try:
        wait_msg = await bot.send_message(
            chat_id=message.chat.id,
            text=f"<b>{langs_text.get(language).get('waiting')}</b>",
            protect_content=True
        )
        urls = await instagram_api.instagram_downloader(link=message.text)
        if urls is None or not urls:
            await wait_msg.delete()
            return await bot.send_message(
                chat_id=message.chat.id,
                text=langs_text.get(language).get('error').format(message.text),
                disable_web_page_preview=True
            )
        media_groups = [urls[i:i + 10] for i in range(0, len(urls), 10)]
        for group in media_groups:
            media = [InputMediaPhoto(url) if 'jpg' in url else InputMediaVideo(url) for url in group]
            media[-1].caption = f"<b>{langs_text.get(language).get('saved')} 📥</b>"
            await bot.send_media_group(chat_id=message.chat.id, media=media)
        await wait_msg.delete()
    except Exception as e:
        logger.exception("Error while sending Instagram photo: %s", )
        await wait_msg.delete()
        return await bot.send_message(
            chat_id=message.chat.id,
            text=langs_text.get(language).get('error').format(message.text),
            disable_web_page_preview=True
        )
