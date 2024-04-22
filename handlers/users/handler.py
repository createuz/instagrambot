import time
from aiogram.types import InputMediaPhoto, InputMediaVideo
from api import instagram_api
from db.models import *
from data import *
from keyboards import *


@dp.message_handler(regexp=r'https?:\/\/(www\.)?api\.com\/(reel|p)\/([-_a-zA-Z0-9]{11})',
                    chat_type=types.ChatType.PRIVATE)
async def send_instagram_media(message: types.Message):
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
        media[-1].caption = f"<b>{main_caption}{langs_text.get(language).get('saved')} 📥</b>"
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


@dp.message_handler(regexp=r'https?:\/\/(www\.)?api\.com\/(stories)', chat_type=types.ChatType.PRIVATE)
async def send_instagram_media(message: types.Message):
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
            media[-1].caption = f"<b>{main_caption}{langs_text.get(language).get('saved')} 📥</b>"
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
