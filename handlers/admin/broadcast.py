import asyncio
import re
import time
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType
from keyboards import *
from data import *
from utlis.models import User, Group


async def replace_text_with_links(text):
    def create_html_link(match):
        text_name, url = match.groups()
        return f'<a href="{url}">{text_name}</a>'

    pattern = r'\((.*?)\)\[(.*?)\]'
    return re.sub(pattern, create_html_link, text)


def format_time(elapsed_time):
    hours, rem = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{int(hours):02d} : {int(minutes):02d} : {int(seconds):02d}"


async def send_message_all(chat_id, text=None, video=None, photo=None, caption=None, keyboard=None):
    try:
        if text:
            await bot.send_message(
                chat_id=chat_id,
                text=f"<b>{text}</b>",
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
        if video:
            await bot.send_video(
                chat_id=chat_id,
                video=video,
                caption=f"<b>{caption}</b>",
                reply_markup=keyboard
            )
        if photo:
            await bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=f"<b>{caption}</b>",
                reply_markup=keyboard
            )
        return True
    except Exception as e:
        return None


async def send_messages_to_users(user_ids: list, text=None, video=None, photo=None, caption=None, keyboard=None):
    try:
        active_count = 0
        no_active_count = 0
        for user_id in user_ids:
            if await send_message_all(
                    chat_id=user_id,
                    text=text,
                    video=video,
                    photo=photo,
                    caption=caption,
                    keyboard=keyboard
            ):
                active_count += 1
            else:
                no_active_count += 1
            await asyncio.sleep(0.03)
        return active_count, no_active_count
    except Exception as e:
        return None


async def send_messages_to_groups(group_ids: list, text=None, video=None, photo=None, caption=None, keyboard=None):
    try:
        active_count = 0
        no_active_count = 0
        for group_id in group_ids:
            if await send_message_all(
                    chat_id=group_id,
                    text=text,
                    video=video,
                    photo=photo,
                    caption=caption,
                    keyboard=keyboard
            ):
                active_count += 1
            else:
                no_active_count += 1
            await asyncio.sleep(0.03)
        return active_count, no_active_count
    except Exception as e:
        return None


async def admin_send_message_all(text=None, video=None, photo=None, caption=None, keyboard=None):
    try:
        admin_language = await User.get_language(chat_id=int(ADMINS[0]))
        start_time = time.time()
        all_user_ids = await User.get_all_user(admin_language=admin_language)
        all_group_ids = await Group.get_all_group(admin_language=admin_language)
        active_users, no_active_users = await send_messages_to_users(
            user_ids=all_user_ids,
            text=text,
            video=video,
            photo=photo,
            caption=caption,
            keyboard=keyboard
        )
        active_groups, no_active_groups = await send_messages_to_groups(
            group_ids=all_group_ids,
            text=text,
            video=video,
            photo=photo,
            caption=caption,
            keyboard=keyboard
        )
        elapsed_time = time.time() - start_time
        date = format_time(elapsed_time)
        msg = f'''
┏━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📊  Sent message Statistic
┣━━━━━━━━━━━━━━━━━━━━━━━━━
┃ •  All users:  {len(all_user_ids)}
┣━━━━━━━━━━━━━━━━━━━━━━━━━
┃ •  Active users:  {active_users}
┣━━━━━━━━━━━━━━━━━━━━━━━━━
┃ •  No active users:  {no_active_users}
┣━━━━━━━━━━━━━━━━━━━━━━━━━
┃ •  All groups:  {len(all_group_ids)}
┣━━━━━━━━━━━━━━━━━━━━━━━━━
┃ •  Active groups:  {active_groups}
┣━━━━━━━━━━━━━━━━━━━━━━━━━
┃ •  No active groups:  {no_active_groups}
┣━━━━━━━━━━━━━━━━━━━━━━━━━
┃ •  Total time:  {date}
┗━━━━━━━━━━━━━━━━━━━━━━━━━'''
        await bot.send_message(chat_id=ADMINS[0], text=f"<b>{msg}</b>")
    except Exception as e:
        await bot.send_message(chat_id=ADMINS[0], text=f"Xatolik yuz berdi: {str(e)}")


## =============================== SEND A TEXT ===================================


@dp.callback_query_handler(text="text", chat_id=ADMINS[0])
async def send_voice_to_all(call: types.CallbackQuery):
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="<b>📄 Textni yuboring!</b>"
    )
    await SendText.text.set()


@dp.message_handler(state=SendText.text, content_types=ContentType.TEXT)
async def video_caption(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = await replace_text_with_links(text=message.text)
    await bot.send_message(
        chat_id=message.chat.id,
        text="<b>Xabar uchun tugma yaratishni hohlaysizmi?</b>",
        reply_markup=add_kb
    )
    await SendText.waiting_for_new_btn.set()


@dp.callback_query_handler(state=SendText.waiting_for_new_btn, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'add_kb':
            await bot.send_message(
                chat_id=call.message.chat.id,
                text='<b>Iltimos, 1️⃣ - tugma nomini kiriting!</b>'
            )
            await SendText.waiting_for_button_name_1.set()
        elif call.data == 'send_message':
            async with state.proxy() as data:
                text = data.get('text')
            await bot.send_message(
                chat_id=ADMINS[0],
                text=f"<b>{text}</b>",
                disable_web_page_preview=True
            )
            await bot.send_message(
                chat_id=ADMINS[0],
                text=send_message_type,
                reply_markup=tasdiqlash
            )
            await SendText.waiting_for_is_not_btn.set()
        else:
            await call.message.delete()
            await state.finish()
    except Exception as e:
        return


@dp.callback_query_handler(state=SendText.waiting_for_is_not_btn, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'send_message':
            async with state.proxy() as data:
                text = data.get('text')
                await admin_send_message_all(text=text)
                await state.finish()
        else:
            await call.message.delete()
            await state.finish()
    except Exception as e:
        return


@dp.message_handler(state=SendText.waiting_for_button_name_1, content_types=ContentType.TEXT)
async def bot_echo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["kb_1"] = message.text
    await bot.send_message(
        chat_id=message.chat.id,
        text="Iltimos, 1️⃣ - tugma uchun URL manzilini kiriting."
    )
    await SendText.waiting_for_button_url_1.set()


@dp.message_handler(state=SendText.waiting_for_button_url_1, content_types=ContentType.TEXT)
async def photo_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['url_1'] = message.text
    await bot.send_message(
        chat_id=message.chat.id,
        text="1️⃣ - tugma uchun URL manzili qabul qilindi.",
        reply_markup=kb_2
    )
    await SendText.next_call_2.set()


@dp.callback_query_handler(state=SendText.next_call_2, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'kb_2':
            await bot.send_message(
                chat_id=call.message.chat.id,
                text='Iltimos, 2️⃣ - tugma nomini kiriting.'
            )
            await SendText.waiting_for_button_name_2.set()
        elif call.data == 'send_message':
            async with state.proxy() as data:
                text = data.get('text')
            keyboard = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(text=data["kb_1"], url=data['url_1']))
            await bot.send_message(
                chat_id=ADMINS[0],
                text=f"<b>{text}</b>",
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
            await bot.send_message(
                chat_id=ADMINS[0],
                text=send_message_type,
                reply_markup=tasdiqlash
            )
            await SendText.send_all_1.set()
        else:
            await call.message.delete()
            await state.finish()
    except Exception as e:
        return


@dp.callback_query_handler(state=SendText.send_all_1, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'send_message':
            async with state.proxy() as data:
                text = data.get('text')
                keyboard = InlineKeyboardMarkup(row_width=1).add(
                    InlineKeyboardButton(text=data["kb_1"], url=data['url_1']))
            await admin_send_message_all(text=text, keyboard=keyboard)
            await state.finish()
        else:
            await call.message.delete()
            await state.finish()
    except Exception as e:
        return


@dp.message_handler(state=SendText.waiting_for_button_name_2, content_types=ContentType.TEXT)
async def photo_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["kb_2"] = message.text
    await bot.send_message(
        chat_id=message.chat.id,
        text="Iltimos, 2️⃣ - tugma uchun URL manzilini kiriting."
    )
    await SendText.waiting_for_button_url_2.set()


@dp.message_handler(state=SendText.waiting_for_button_url_2, content_types=ContentType.TEXT)
async def photo_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['url_2'] = message.text
    await bot.send_message(
        chat_id=message.chat.id,
        text="2️⃣ - tugma uchun URL manzili qabul qilindi.",
        reply_markup=kb_5
    )
    await SendText.next_call_3.set()


@dp.callback_query_handler(state=SendText.next_call_3, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'send_message':
            async with state.proxy() as data:
                text = data.get('text')
                keyboard = InlineKeyboardMarkup(row_width=1).add(
                    InlineKeyboardButton(text=data["kb_1"], url=data['url_1']),
                    InlineKeyboardButton(text=data["kb_2"], url=data['url_2']))
            await bot.send_message(
                chat_id=ADMINS[0],
                text=f"<b>{text}</b>",
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
            await bot.send_message(
                chat_id=ADMINS[0],
                text=send_message_type,
                reply_markup=tasdiqlash
            )
            await SendText.send_all_2.set()
        else:
            await call.message.delete()
            await state.finish()
    except Exception as e:
        return


@dp.callback_query_handler(state=SendText.send_all_2, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'send_message':
            async with state.proxy() as data:
                text = data.get('text')
                keyboard = InlineKeyboardMarkup(row_width=1).add(
                    InlineKeyboardButton(text=data["kb_1"], url=data['url_1']),
                    InlineKeyboardButton(text=data["kb_2"], url=data['url_2']))
            await admin_send_message_all(text=text, keyboard=keyboard)
            await state.finish()
        else:
            await call.message.delete()
            await state.finish()
    except Exception as e:
        return


## =============================== SEND A PHOTO ===================================


@dp.callback_query_handler(text="photo", chat_id=ADMINS[0])
async def send_photo_to_all(call: types.CallbackQuery):
    chat_id = call.from_user.id
    callback_id = call.message.message_id
    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=callback_id,
        text="🖼 SEND A PHOTO"
    )
    await SendPhoto.photo.set()


@dp.message_handler(state=SendPhoto.photo, content_types=ContentType.PHOTO)
async def send_photo_to_all(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["photo"] = message.photo[-1].file_id
    await bot.send_message(
        chat_id=message.chat.id,
        text="Iltimos, photo uchun ma'lumotlarni kiriting."
    )
    await SendPhoto.waiting_for_caption.set()


@dp.message_handler(state=SendPhoto.waiting_for_caption, content_types=ContentType.TEXT)
async def video_caption(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['caption'] = await replace_text_with_links(message.text)
    await bot.send_message(
        chat_id=message.chat.id,
        text="Xabar uchun tugma yaratishni hohlaysizmi?",
        reply_markup=add_kb
    )
    await SendPhoto.waiting_for_new_btn.set()


@dp.callback_query_handler(state=SendPhoto.waiting_for_new_btn, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'add_kb':
            await bot.send_message(
                chat_id=call.message.chat.id,
                text='Iltimos, 1️⃣ - tugma nomini kiriting.'
            )
            await SendPhoto.waiting_for_button_name_1.set()
        elif call.data == 'send_message':
            async with state.proxy() as data:
                photo = data["photo"]
                caption = data['caption']
            await bot.send_photo(
                chat_id=ADMINS[0],
                photo=photo,
                caption=f"<b>{caption}</b>"
            )
            await bot.send_message(
                chat_id=ADMINS[0],
                text=send_message_type,
                reply_markup=tasdiqlash
            )
            await SendPhoto.waiting_for_is_not_btn.set()
        else:
            await call.message.delete()
            await state.finish()
    except Exception as e:
        return


@dp.callback_query_handler(state=SendPhoto.waiting_for_is_not_btn, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'send_message':
            async with state.proxy() as data:
                photo = data["photo"]
                caption = data['caption']
            await admin_send_message_all(photo=photo, caption=caption)
            await state.finish()
        else:
            await call.message.delete()
            await state.finish()
    except Exception as e:
        return


@dp.message_handler(state=SendPhoto.waiting_for_button_name_1, content_types=ContentType.TEXT)
async def photo_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["kb_1"] = message.text
    await bot.send_message(
        chat_id=message.chat.id,
        text="Iltimos, 1️⃣ - tugma uchun URL manzilini kiriting."
    )
    await SendPhoto.waiting_for_button_url_1.set()


@dp.message_handler(state=SendPhoto.waiting_for_button_url_1, content_types=ContentType.TEXT)
async def photo_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['url_1'] = message.text
    await bot.send_message(
        chat_id=message.chat.id,
        text="1️⃣ - tugma uchun URL manzili qabul qilindi.",
        reply_markup=kb_2
    )
    await SendPhoto.next_call_2.set()


@dp.callback_query_handler(state=SendPhoto.next_call_2, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'kb_2':
            await bot.send_message(
                chat_id=call.message.chat.id,
                text='Iltimos, 2️⃣ - tugma nomini kiriting.'
            )
            await SendPhoto.waiting_for_button_name_2.set()
        elif call.data == 'send_message':
            async with state.proxy() as data:
                photo = data["photo"]
                caption = data['caption']
                keyboard = InlineKeyboardMarkup(row_width=1).add(
                    InlineKeyboardButton(text=data["kb_1"], url=data['url_1']))
            await bot.send_photo(
                chat_id=ADMINS[0],
                photo=photo,
                caption=caption,
                reply_markup=keyboard
            )
            await bot.send_message(
                chat_id=ADMINS[0],
                text=send_message_type,
                reply_markup=tasdiqlash
            )
            await SendPhoto.send_all_1.set()
        else:
            await call.message.delete()
            await state.finish()
    except Exception as e:
        return


@dp.callback_query_handler(state=SendPhoto.send_all_1, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'send_message':
            async with state.proxy() as data:
                photo = data["photo"]
                caption = data['caption']
                keyboard = InlineKeyboardMarkup(row_width=1).add(
                    InlineKeyboardButton(text=data["kb_1"], url=data['url_1']))
            await admin_send_message_all(photo=photo, caption=caption, keyboard=keyboard)
            await state.finish()
        else:
            await call.message.delete()
            await state.finish()
    except Exception as e:
        return


@dp.message_handler(state=SendPhoto.waiting_for_button_name_2, content_types=ContentType.TEXT)
async def photo_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["kb_2"] = message.text
    await bot.send_message(
        hat_id=message.chat.id,
        text="Iltimos, 2️⃣ - tugma uchun URL manzilini kiriting."
    )
    await SendPhoto.waiting_for_button_url_2.set()


@dp.message_handler(state=SendPhoto.waiting_for_button_url_2, content_types=ContentType.TEXT)
async def photo_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['url_2'] = message.text
    await bot.send_message(
        chat_id=message.chat.id,
        text="2️⃣ - tugma uchun URL manzili qabul qilindi.",
        reply_markup=kb_3
    )
    await SendPhoto.next_call_3.set()


@dp.callback_query_handler(state=SendPhoto.next_call_3, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'kb_3':
            await bot.send_message(
                chat_id=call.message.chat.id,
                text='Iltimos, 3️⃣ - tugma nomini kiriting.'
            )
            await SendPhoto.waiting_for_button_name_3.set()
        elif call.data == 'send_message':
            async with state.proxy() as data:
                photo = data["photo"]
                caption = data['caption']
                keyboard = InlineKeyboardMarkup(row_width=1).add(
                    InlineKeyboardButton(text=data["kb_1"], url=data['url_1']),
                    InlineKeyboardButton(text=data["kb_2"], url=data['url_2']))
            await bot.send_photo(
                chat_id=ADMINS[0],
                photo=photo,
                caption=caption,
                reply_markup=keyboard
            )
            await bot.send_message(
                chat_id=ADMINS[0],
                text=send_message_type,
                reply_markup=tasdiqlash
            )
            await SendPhoto.send_all_2.set()
        else:
            await call.message.delete()
            await state.finish()
    except Exception as e:
        return


@dp.callback_query_handler(state=SendPhoto.send_all_2, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'send_message':
            async with state.proxy() as data:
                photo = data["photo"]
                caption = data['caption']
                keyboard = InlineKeyboardMarkup(row_width=1).add(
                    InlineKeyboardButton(text=data["kb_1"], url=data['url_1']),
                    InlineKeyboardButton(text=data["kb_2"], url=data['url_2']))
            await admin_send_message_all(photo=photo, caption=caption, keyboard=keyboard)
            await state.finish()
        else:
            await call.message.delete()
            await state.finish()
    except Exception as e:
        return


@dp.message_handler(state=SendPhoto.waiting_for_button_name_3, content_types=ContentType.TEXT)
async def photo_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["kb_3"] = message.text
    await bot.send_message(
        chat_id=message.chat.id,
        text="Iltimos, 3️⃣ - tugma uchun URL manzilini kiriting."
    )
    await SendPhoto.waiting_for_button_url_3.set()


@dp.message_handler(state=SendPhoto.waiting_for_button_url_3, content_types=ContentType.TEXT)
async def photo_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['url_3'] = message.text
    await bot.send_message(
        chat_id=message.chat.id,
        text="3️⃣ - tugma uchun URL manzili qabul qilindi.",
        reply_markup=kb_4
    )
    await SendPhoto.next_call_4.set()


@dp.callback_query_handler(state=SendPhoto.next_call_4, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'kb_4':
            await bot.send_message(
                chat_id=call.message.chat.id,
                text="Iltimos, 4️⃣ - tugma nomini kiriting."
            )
            await SendPhoto.waiting_for_button_name_4.set()
        elif call.data == 'send_message':
            async with state.proxy() as data:
                photo = data["photo"]
                caption = data['caption']
                keyboard = InlineKeyboardMarkup(row_width=2).add(
                    InlineKeyboardButton(text=data["kb_1"], url=data['url_1']),
                    InlineKeyboardButton(text=data["kb_2"], url=data['url_2']),
                    InlineKeyboardButton(text=data["kb_3"], url=data['url_3']))
            await bot.send_photo(
                chat_id=ADMINS[0],
                photo=photo,
                caption=caption,
                reply_markup=keyboard
            )
            await bot.send_message(
                chat_id=ADMINS[0],
                text=send_message_type,
                reply_markup=tasdiqlash
            )
            await SendPhoto.send_all_3.set()
        else:
            await call.message.delete()
            await state.finish()
    except Exception as e:
        return


@dp.callback_query_handler(state=SendPhoto.send_all_3, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'send_message':
            async with state.proxy() as data:
                photo = data["photo"]
                caption = data['caption']
                keyboard = InlineKeyboardMarkup(row_width=2).add(
                    InlineKeyboardButton(text=data["kb_1"], url=data['url_1']),
                    InlineKeyboardButton(text=data["kb_2"], url=data['url_2']),
                    InlineKeyboardButton(text=data["kb_3"], url=data['url_3']))
            await admin_send_message_all(photo=photo, caption=caption, keyboard=keyboard)
            await state.finish()
        else:
            await call.message.delete()
            await state.finish()
    except Exception as e:
        return


@dp.message_handler(state=SendPhoto.waiting_for_button_name_4, content_types=ContentType.TEXT)
async def photo_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["kb_4"] = message.text
    await bot.send_message(
        chat_id=message.chat.id,
        text="Iltimos, 3️⃣ - tugma uchun URL manzilini kiriting."
    )
    await SendPhoto.waiting_for_button_url_4.set()


@dp.message_handler(state=SendPhoto.waiting_for_button_url_4, content_types=ContentType.TEXT)
async def photo_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['url_4'] = message.text
    await bot.send_message(
        chat_id=message.chat.id,
        text="4️⃣ - tugma uchun URL manzili qabul qilindi.",
        reply_markup=kb_5
    )
    await SendPhoto.next_call_5.set()


@dp.callback_query_handler(state=SendPhoto.next_call_5, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if call.data == 'send_message':
        async with state.proxy() as data:
            photo = data["photo"]
            caption = data['caption']
            keyboard = InlineKeyboardMarkup(row_width=2).add(
                InlineKeyboardButton(text=data["kb_1"], url=data['url_1']),
                InlineKeyboardButton(text=data["kb_2"], url=data['url_2']),
                InlineKeyboardButton(text=data["kb_3"], url=data['url_3']),
                InlineKeyboardButton(text=data["kb_4"], url=data['url_4']))
        await bot.send_photo(
            chat_id=ADMINS[0],
            photo=photo,
            caption=caption,
            reply_markup=keyboard
        )
        await bot.send_message(
            chat_id=ADMINS[0],
            text=send_message_type,
            reply_markup=tasdiqlash
        )
        await SendPhoto.send_all_4.set()
    else:
        await call.message.delete()
        await state.finish()


@dp.callback_query_handler(state=SendPhoto.send_all_4, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if call.data == 'send_message':
        async with state.proxy() as data:
            photo = data["photo"]
            caption = data['caption']
            keyboard = InlineKeyboardMarkup(row_width=2).add(
                InlineKeyboardButton(text=data["kb_1"], url=data['url_1']),
                InlineKeyboardButton(text=data["kb_2"], url=data['url_2']),
                InlineKeyboardButton(text=data["kb_3"], url=data['url_3']),
                InlineKeyboardButton(text=data["kb_4"], url=data['url_4']))
        await admin_send_message_all(photo=photo, caption=caption, keyboard=keyboard)
        await state.finish()
    else:
        await call.message.delete()
        await state.finish()


## =============================== SEND A VIDEO ===================================


@dp.callback_query_handler(text="video", chat_id=ADMINS[0])
async def send_video_to_all(call: types.CallbackQuery):
    chat_id = call.from_user.id
    callback_id = call.message.message_id
    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=callback_id,
        text="🎥 SEND A VIDEO"
    )
    await SendVideo.video.set()


@dp.message_handler(state=SendVideo.video, content_types=ContentType.VIDEO)
async def send_video_to_all(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["video"] = message.video.file_id
    await bot.send_message(
        chat_id=message.chat.id,
        text="Iltimos, video uchun ma'lumotlarni kiriting."
    )
    await SendVideo.waiting_for_caption.set()


@dp.message_handler(state=SendVideo.waiting_for_caption, content_types=ContentType.TEXT)
async def video_caption(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['caption'] = await replace_text_with_links(message.text)
    await bot.send_message(
        chat_id=message.chat.id,
        text="Xabar uchun tugma yaratishni hohlaysizmi?",
        reply_markup=add_kb
    )
    await SendVideo.waiting_for_new_btn.set()


@dp.callback_query_handler(state=SendVideo.waiting_for_new_btn, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if call.data == 'add_kb':
        await bot.send_message(
            chat_id=call.message.chat.id,
            text='Iltimos, 1️⃣ - tugma nomini kiriting.'
        )
        await SendVideo.waiting_for_button_name_1.set()
    elif call.data == 'send_message':
        async with state.proxy() as data:
            video = data["video"]
            caption = data['caption']
        await bot.send_video(
            chat_id=ADMINS[0],
            video=video,
            caption=f"<b>{caption}</b>"
        )
        await bot.send_message(
            chat_id=ADMINS[0],
            text=send_message_type,
            reply_markup=tasdiqlash
        )
        await SendPhoto.waiting_for_is_not_btn.set()
    else:
        await call.message.delete()
        await state.finish()


@dp.callback_query_handler(state=SendPhoto.waiting_for_is_not_btn, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if call.data == 'send_message':
        async with state.proxy() as data:
            video = data["video"]
            caption = data['caption']
        await admin_send_message_all(video=video, caption=caption)
        await state.finish()
    else:
        await call.message.delete()
        await state.finish()


@dp.message_handler(state=SendVideo.waiting_for_button_name_1, content_types=ContentType.TEXT)
async def video_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["kb_1"] = message.text
    await bot.send_message(
        chat_id=message.chat.id,
        text="Iltimos, 1️⃣ - tugma uchun URL manzilini kiriting."
    )
    await SendVideo.waiting_for_button_url_1.set()


@dp.message_handler(state=SendVideo.waiting_for_button_url_1, content_types=ContentType.TEXT)
async def video_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['url_1'] = message.text
    await bot.send_message(
        chat_id=message.chat.id,
        text="1️⃣ - tugma uchun URL manzili qabul qilindi.",
        reply_markup=kb_2
    )
    await SendVideo.next_call_2.set()


@dp.callback_query_handler(state=SendVideo.next_call_2, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if call.data == 'kb_2':
        await bot.send_message(
            chat_id=call.message.chat.id,
            text='Iltimos, 2️⃣ - tugma nomini kiriting.'
        )
        await SendVideo.waiting_for_button_name_2.set()
    elif call.data == 'send_message':
        async with state.proxy() as data:
            video = data["video"]
            caption = data['caption']
            keyboard = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(text=data["kb_1"], url=data['url_1']))
        await bot.send_video(
            chat_id=ADMINS[0],
            video=video,
            caption=caption,
            reply_markup=keyboard
        )
        await bot.send_message(
            chat_id=ADMINS[0],
            text=send_message_type,
            reply_markup=tasdiqlash
        )
        await SendVideo.send_all_1.set()
    else:
        await call.message.delete()
        await state.finish()


@dp.callback_query_handler(state=SendVideo.send_all_1, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if call.data == 'send_message':
        async with state.proxy() as data:
            video = data["video"]
            caption = data['caption']
            keyboard = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(text=data["kb_1"], url=data['url_1']))
        await admin_send_message_all(video=video, caption=caption, keyboard=keyboard)
        await state.finish()
    else:
        await call.message.delete()
        await state.finish()


@dp.message_handler(state=SendVideo.waiting_for_button_name_2, content_types=ContentType.TEXT)
async def video_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["kb_2"] = message.text
    await bot.send_message(
        chat_id=message.chat.id,
        text="Iltimos, 2️⃣ - tugma uchun URL manzilini kiriting."
    )
    await SendVideo.waiting_for_button_url_2.set()


@dp.message_handler(state=SendVideo.waiting_for_button_url_2, content_types=ContentType.TEXT)
async def video_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['url_2'] = message.text
    await bot.send_message(
        chat_id=message.chat.id,
        text="2️⃣ - tugma uchun URL manzili qabul qilindi.",
        reply_markup=kb_3
    )
    await SendVideo.next_call_3.set()


@dp.callback_query_handler(state=SendVideo.next_call_3, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if call.data == 'kb_3':
        await bot.send_message(
            chat_id=call.message.chat.id,
            text='Iltimos, 3️⃣ - tugma nomini kiriting.'
        )
        await SendVideo.waiting_for_button_name_3.set()
    elif call.data == 'send_message':
        async with state.proxy() as data:
            video = data["video"]
            caption = data['caption']
            keyboard = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(text=data["kb_1"], url=data['url_1']),
                InlineKeyboardButton(text=data["kb_2"], url=data['url_2']))
        await bot.send_video(
            chat_id=ADMINS[0],
            video=video,
            caption=caption,
            reply_markup=keyboard
        )
        await bot.send_message(
            chat_id=ADMINS[0],
            text=send_message_type,
            reply_markup=tasdiqlash
        )
        await SendVideo.send_all_2.set()
    else:
        await call.message.delete()
        await state.finish()


@dp.callback_query_handler(state=SendVideo.send_all_2, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if call.data == 'send_message':
        async with state.proxy() as data:
            video = data["video"]
            caption = data['caption']
            keyboard = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(text=data["kb_1"], url=data['url_1']),
                InlineKeyboardButton(text=data["kb_2"], url=data['url_2']))
        await admin_send_message_all(video=video, caption=caption, keyboard=keyboard)
        await state.finish()
    else:
        await call.message.delete()
        await state.finish()


@dp.message_handler(state=SendVideo.waiting_for_button_name_3, content_types=ContentType.TEXT)
async def video_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["kb_3"] = message.text
    await bot.send_message(
        chat_id=message.chat.id,
        text="Iltimos, 3️⃣ - tugma uchun URL manzilini kiriting."
    )
    await SendVideo.waiting_for_button_url_3.set()


@dp.message_handler(state=SendVideo.waiting_for_button_url_3, content_types=ContentType.TEXT)
async def video_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['url_3'] = message.text
    await bot.send_message(
        chat_id=message.chat.id,
        text="3️⃣ - tugma uchun URL manzili qabul qilindi.",
        reply_markup=kb_4
    )
    await SendVideo.next_call_4.set()


@dp.callback_query_handler(state=SendVideo.next_call_4, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if call.data == 'kb_4':
        await bot.send_message(
            chat_id=call.message.chat.id,
            text="Iltimos, 4️⃣ - tugma nomini kiriting."
        )
        await SendVideo.waiting_for_button_name_4.set()
    elif call.data == 'send_message':
        async with state.proxy() as data:
            video = data["video"]
            caption = data['caption']
            keyboard = InlineKeyboardMarkup(row_width=2).add(
                InlineKeyboardButton(text=data["kb_1"], url=data['url_1']),
                InlineKeyboardButton(text=data["kb_2"], url=data['url_2']),
                InlineKeyboardButton(text=data["kb_3"], url=data['url_3']))
        await bot.send_video(
            chat_id=ADMINS[0],
            video=video,
            caption=caption,
            reply_markup=keyboard
        )
        await bot.send_message(
            chat_id=ADMINS[0],
            text=send_message_type,
            reply_markup=tasdiqlash
        )
        await SendVideo.send_all_3.set()
    else:
        await bot.send_message(
            chat_id=call.message.chat.id,
            text='❌Xabar yuborish bekor qilindi.'
        )
        return await state.finish()


@dp.callback_query_handler(state=SendVideo.send_all_3, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if call.data == 'send_message':
        async with state.proxy() as data:
            video = data["video"]
            caption = data['caption']
            keyboard = InlineKeyboardMarkup(row_width=2).add(
                InlineKeyboardButton(text=data["kb_1"], url=data['url_1']),
                InlineKeyboardButton(text=data["kb_2"], url=data['url_2']),
                InlineKeyboardButton(text=data["kb_3"], url=data['url_3']))
        await admin_send_message_all(video=video, caption=caption, keyboard=keyboard)
        await state.finish()
    else:
        await call.message.delete()
        await state.finish()


@dp.message_handler(state=SendVideo.waiting_for_button_name_4, content_types=ContentType.TEXT)
async def video_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["kb_4"] = message.text
    await bot.send_message(
        chat_id=message.chat.id,
        text="Iltimos, 3️⃣ - tugma uchun URL manzil kiriting."
    )
    await SendVideo.waiting_for_button_url_4.set()


@dp.message_handler(state=SendVideo.waiting_for_button_url_4, content_types=ContentType.TEXT)
async def video_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['url_4'] = message.text
    await bot.send_message(
        chat_id=message.chat.id,
        text="4️⃣ - tugma uchun URL manzili qabul qilindi.",
        reply_markup=kb_5
    )
    await SendVideo.next_call_5.set()


@dp.callback_query_handler(state=SendVideo.next_call_5, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if call.data == 'send_message':
        async with state.proxy() as data:
            video = data["video"]
            caption = data['caption']
        keyboard = InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton(text=data["kb_1"], url=data['url_1']),
            InlineKeyboardButton(text=data["kb_2"], url=data['url_2']),
            InlineKeyboardButton(text=data["kb_3"], url=data['url_3']),
            InlineKeyboardButton(text=data["kb_4"], url=data['url_4']))
        await bot.send_video(
            chat_id=ADMINS[0],
            video=video,
            caption=caption,
            reply_markup=keyboard
        )
        await bot.send_message(
            chat_id=ADMINS[0],
            text=send_message_type,
            reply_markup=tasdiqlash
        )
        await SendVideo.send_all_4.set()
    else:
        await call.message.delete()
        await state.finish()


@dp.callback_query_handler(state=SendVideo.send_all_4, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if call.data == 'send_message':
        async with state.proxy() as data:
            video = data["video"]
            caption = data['caption']
            keyboard = InlineKeyboardMarkup(row_width=2).add(
                InlineKeyboardButton(text=data["kb_1"], url=data['url_1']),
                InlineKeyboardButton(text=data["kb_2"], url=data['url_2']),
                InlineKeyboardButton(text=data["kb_3"], url=data['url_3']),
                InlineKeyboardButton(text=data["kb_4"], url=data['url_4']))
        await admin_send_message_all(video=video, caption=caption, keyboard=keyboard)
        await state.finish()
    else:
        await call.message.delete()
        await state.finish()
