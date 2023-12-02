import asyncio
import re
import time

from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType

from keyboards import *
from data import *
from utlis.models import User, Group

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)


async def replace_text_with_links(text):
    def create_html_link(match):
        text_name, url = match.groups()
        return f'<a href="{url}">{text_name}</a>'

    pattern = r'\((.*?)\)\[(.*?)\]'
    replaced_text = re.sub(pattern, create_html_link, text)
    return replaced_text


def format_time(elapsed_time):
    hours, rem = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{int(hours):02d} : {int(minutes):02d} : {int(seconds):02d}"


async def send_message_all(chat_id, text=None, video=None, photo=None, caption=None, keyboard=None):
    try:
        if text:
            await bot.send_message(chat_id=chat_id, text=f"<b>{text}</b>", reply_markup=keyboard,
                                   disable_web_page_preview=True)
        if video:
            await bot.send_video(chat_id=chat_id, video=video, caption=f"<b>{caption}</b>", reply_markup=keyboard, )
        if photo:
            await bot.send_photo(chat_id=chat_id, photo=photo, caption=f"<b>{caption}</b>", reply_markup=keyboard)
        return True
    except Exception as e:
        logger.exception("Xabarni yuborishda xatolik: %s", e)
        return False


async def send_messages_to_users(user_ids: list, text=None, video=None, photo=None, caption=None, keyboard=None):
    try:
        active_count = 0
        no_active_count = 0
        for user_id in user_ids:
            if await send_message_all(user_id, text=text, video=video, photo=photo, caption=caption, keyboard=keyboard):
                active_count += 1
            else:
                no_active_count += 1
            await asyncio.sleep(0.04)
        return active_count, no_active_count
    except Exception as e:
        logging.exception("Xabarni yuborishda xatolik: %s", e)
        return False


async def send_messages_to_groups(group_ids: list, text=None, video=None, photo=None, caption=None, keyboard=None):
    try:
        active_count = 0
        no_active_count = 0
        for group_id in group_ids:
            if await send_message_all(group_id, text=text, video=video, photo=photo, caption=caption,
                                      keyboard=keyboard):
                active_count += 1
            else:
                no_active_count += 1
            await asyncio.sleep(0.04)
        return active_count, no_active_count
    except Exception as e:
        logging.exception("Xabarni yuborishda xatolik: %s", e)
        return False


async def admin_send_message_all(text=None, video=None, photo=None, caption=None, keyboard=None):
    try:
        admin_language = await User.get_language(int(ADMINS[0]))
        start_time = time.time()
        all_user_ids = await User.get_all_user(admin_language)
        all_group_ids = await Group.get_all_group(admin_language)
        active_users, no_active_users = await send_messages_to_users(all_user_ids, text=text, video=video, photo=photo,
                                                                     caption=caption, keyboard=keyboard)
        active_groups, no_active_groups = await send_messages_to_groups(all_group_ids, text=text, video=video,
                                                                        photo=photo, caption=caption, keyboard=keyboard)
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
        await bot.send_message(ADMINS[0], text=f"<b>{msg}</b>")
    except Exception as e:
        logging.exception("Xabarni yuborishda xatolik: %s", e)
        await bot.send_message(ADMINS[0], 'Xabarni yuborishda xatolik yuz berdi.')


## =============================== SEND A TEXT ===================================


@dp.callback_query_handler(text="text", chat_id=ADMINS[0])
async def send_voice_to_all(call: types.CallbackQuery):
    chat_id = call.from_user.id
    callback_id = call.message.message_id
    await bot.edit_message_text(chat_id=chat_id, message_id=callback_id, text="🎙 SEND A TEXT")
    await SendText.text.set()


@dp.message_handler(state=SendText.text, content_types=ContentType.TEXT)
async def video_caption(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = await replace_text_with_links(message.text)
    await bot.send_message(chat_id=message.chat.id, text="<b>Xabar uchun tugma yaratishni hohlaysizmi?</b>",
                           reply_markup=add_btn)
    await SendText.waiting_for_new_btn.set()


@dp.callback_query_handler(state=SendText.waiting_for_new_btn, chat_id=ADMINS[0])
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'add_btn':
            await call.message.answer('Iltimos, birinchi tugma nomini kiriting.')
            await SendText.waiting_for_button_name_1.set()
        elif call.data == 'send_message':
            async with state.proxy() as data:
                text = data['text']
            await bot.send_message(chat_id=ADMINS[0], text=f"<b>{text}</b>", disable_web_page_preview=True)
            await bot.send_message(chat_id=ADMINS[0],
                                   text="<b>Siz yubormoqchi bo'lgan xabar\nxuddi shu ko'rinishda bo'ladi!\n\n"
                                        "✅ Tastiqlash   |   🗑 Bekor qilish</b>", reply_markup=tasdiqlash)
            await SendText.waiting_for_is_not_btn.set()
        else:
            await call.message.delete()
            await state.finish()
    except Exception as e:
        logging.exception("Xabarni yuborishda xatolik: %s", e)
        return


@dp.callback_query_handler(state=SendText.waiting_for_is_not_btn, chat_id=ADMINS[0])
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'send_message':
            async with state.proxy() as data:
                text = data['text']
                await admin_send_message_all(text=text)
                await state.finish()
        else:
            await call.message.delete()
            await state.finish()
    except Exception as e:
        logging.exception("Xabarni yuborishda xatolik: %s", e)
        return


@dp.message_handler(state=SendText.waiting_for_button_name_1, content_types=ContentType.TEXT)
async def bot_echo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["btname_1"] = message.text
    await message.answer("Iltimos, birinchi tugma uchun URL manzilini kiriting.")
    await SendText.waiting_for_button_url_1.set()


@dp.message_handler(state=SendText.waiting_for_button_url_1, content_types=ContentType.TEXT)
async def photo_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['url_1'] = message.text
    await message.answer("Birinchi tugma uchun URL manzili qabul qilindi.", reply_markup=button_2)
    await SendText.next_call_2.set()


@dp.callback_query_handler(state=SendText.next_call_2, chat_id=ADMINS[0])
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'button_2':
            await call.message.answer('Iltimos, ikkinchi tugma nomini kiriting.')
            await SendText.waiting_for_button_name_2.set()
        elif call.data == 'send_message':
            async with state.proxy() as data:
                text = data['text']
                keyboard = InlineKeyboardMarkup(row_width=1, resize_keyboard=True).add(
                    InlineKeyboardButton(text=data["btname_1"], url=data['url_1']))
            await bot.send_message(chat_id=ADMINS[0], text=f"<b>{text}</b>", reply_markup=keyboard,
                                   disable_web_page_preview=True)
            await bot.send_message(chat_id=ADMINS[0],
                                   text="<b>Siz yubormoqchi bo'lgan xabar\nxuddi shu ko'rinishda bo'ladi!\n\n"
                                        "✅ Tastiqlash   |   🗑 Bekor qilish</b>", reply_markup=tasdiqlash)
            await SendText.send_all_1.set()
        else:
            await call.message.delete()
            await state.finish()
    except Exception as e:
        logging.exception("Xabarni yuborishda xatolik: %s", e)
        return


@dp.callback_query_handler(state=SendText.send_all_1, chat_id=ADMINS[0])
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'send_message':
            async with state.proxy() as data:
                text = data['text']
                keyboard = InlineKeyboardMarkup(row_width=1, resize_keyboard=True).add(
                    InlineKeyboardButton(text=data["btname_1"], url=data['url_1']))
            await admin_send_message_all(text=text, keyboard=keyboard)
            await state.finish()
        else:
            await call.message.delete()
            await state.finish()
    except Exception as e:
        logging.exception("Xabarni yuborishda xatolik: %s", e)
        return


@dp.message_handler(state=SendText.waiting_for_button_name_2, content_types=ContentType.TEXT)
async def photo_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["btname_2"] = message.text
    await message.answer("Iltimos, ikkinchi tugma uchun URL manzilini kiriting.")
    await SendText.waiting_for_button_url_2.set()


@dp.message_handler(state=SendText.waiting_for_button_url_2, content_types=ContentType.TEXT)
async def photo_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['url_2'] = message.text
    await message.answer("Ikkinchi tugma uchun URL manzili qabul qilindi.", reply_markup=button_5)
    await SendText.next_call_3.set()


@dp.callback_query_handler(state=SendText.next_call_3, chat_id=ADMINS[0])
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'send_message':
            async with state.proxy() as data:
                text = data['text']
                keyboard = InlineKeyboardMarkup(row_width=1, resize_keyboard=True).add(
                    InlineKeyboardButton(text=data["btname_1"], url=data['url_1']),
                    InlineKeyboardButton(text=data["btname_2"], url=data['url_2']))
            await bot.send_message(chat_id=ADMINS[0], text=f"<b>{text}</b>", reply_markup=keyboard,
                                   disable_web_page_preview=True)
            await bot.send_message(chat_id=ADMINS[0],
                                   text="<b>Siz yubormoqchi bo'lgan xabar\nxuddi shu ko'rinishda bo'ladi!\n\n"
                                        "✅ Tastiqlash   |   🗑 Bekor qilish</b>", reply_markup=tasdiqlash)
            await SendText.send_all_2.set()
        else:
            await call.message.delete()
            await state.finish()
    except Exception as e:
        logging.exception("Xabarni yuborishda xatolik: %s", e)
        return


@dp.callback_query_handler(state=SendText.send_all_2, chat_id=ADMINS[0])
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'send_message':
            async with state.proxy() as data:
                text = data['text']
                keyboard = InlineKeyboardMarkup(row_width=1, resize_keyboard=True).add(
                    InlineKeyboardButton(text=data["btname_1"], url=data['url_1']),
                    InlineKeyboardButton(text=data["btname_2"], url=data['url_2']))
            await admin_send_message_all(text=text, keyboard=keyboard)
            await state.finish()
        else:
            await call.message.delete()
            await state.finish()
    except Exception as e:
        logging.exception("Xabarni yuborishda xatolik: %s", e)
        return


## =============================== SEND A PHOTO ===================================


@dp.callback_query_handler(text="photo", chat_id=ADMINS[0])
async def send_photo_to_all(call: types.CallbackQuery):
    chat_id = call.from_user.id
    callback_id = call.message.message_id
    await bot.edit_message_text(chat_id=chat_id, message_id=callback_id, text="🖼 SEND A PHOTO")
    await SendPhoto.photo.set()


@dp.message_handler(state=SendPhoto.photo, content_types=ContentType.PHOTO)
async def send_photo_to_all(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["photo_file"] = message.photo[-1].file_id
    await message.answer("Iltimos, photo uchun ma'lumotlarni kiriting.")
    await SendPhoto.waiting_for_caption.set()


@dp.message_handler(state=SendPhoto.waiting_for_caption, content_types=ContentType.TEXT)
async def video_caption(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['caption'] = await replace_text_with_links(message.text)
    await message.answer("Xabar uchun tugma yaratishni hohlaysizmi?", reply_markup=add_btn)
    await SendPhoto.waiting_for_new_btn.set()


@dp.callback_query_handler(state=SendPhoto.waiting_for_new_btn, chat_id=ADMINS[0])
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'add_btn':
            await call.message.answer('Iltimos, birinchi tugma nomini kiriting.')
            await SendPhoto.waiting_for_button_name_1.set()
        elif call.data == 'send_message':
            async with state.proxy() as data:
                photo_file = data["photo_file"]
                caption = data['caption']
            await bot.send_photo(chat_id=ADMINS[0], photo=photo_file, caption=f"<b>{caption}</b>")
            await bot.send_message(chat_id=ADMINS[0],
                                   text="<b>Siz yubormoqchi bo'lgan xabar\nxuddi shu ko'rinishda bo'ladi!\n\n"
                                        "✅ Tastiqlash   |   🗑 Bekor qilish</b>", reply_markup=tasdiqlash)
            await SendPhoto.waiting_for_is_not_btn.set()
        else:
            await call.message.delete()
            await state.finish()
    except Exception as e:
        logging.exception("Xabarni yuborishda xatolik: %s", e)
        return


@dp.callback_query_handler(state=SendPhoto.waiting_for_is_not_btn, chat_id=ADMINS[0])
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'send_message':
            async with state.proxy() as data:
                photo_file = data["photo_file"]
                caption = data['caption']
            await admin_send_message_all(photo=photo_file, caption=caption)
            await state.finish()
        else:
            await call.message.delete()
            await state.finish()
    except Exception as e:
        logging.exception("Xabarni yuborishda xatolik: %s", e)
        return


@dp.message_handler(state=SendPhoto.waiting_for_button_name_1, content_types=ContentType.TEXT)
async def photo_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["btname_1"] = message.text
    await message.answer("Iltimos, birinchi tugma uchun URL manzilini kiriting.")
    await SendPhoto.waiting_for_button_url_1.set()


@dp.message_handler(state=SendPhoto.waiting_for_button_url_1, content_types=ContentType.TEXT)
async def photo_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['url_1'] = message.text
    await message.answer("Birinchi tugma uchun URL manzili qabul qilindi.", reply_markup=button_2)
    await SendPhoto.next_call_2.set()


@dp.callback_query_handler(state=SendPhoto.next_call_2, chat_id=ADMINS[0])
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'button_2':
            await call.message.answer('Iltimos, ikkinchi tugma nomini kiriting.')
            await SendPhoto.waiting_for_button_name_2.set()
        elif call.data == 'send_message':
            async with state.proxy() as data:
                photo_file = data["photo_file"]
                caption = data['caption']
                keyboard = InlineKeyboardMarkup(row_width=1, resize_keyboard=True).add(
                    InlineKeyboardButton(text=data["btname_1"], url=data['url_1']))
            await bot.send_photo(chat_id=ADMINS[0], photo=photo_file, caption=caption, reply_markup=keyboard)
            await bot.send_message(chat_id=ADMINS[0],
                                   text="<b>Siz yubormoqchi bo'lgan xabar\nxuddi shu ko'rinishda bo'ladi!\n\n"
                                        "✅ Tastiqlash   |   🗑 Bekor qilish</b>", reply_markup=tasdiqlash)
            await SendPhoto.send_all_1.set()
        else:
            await call.message.delete()
            await state.finish()
    except Exception as e:
        logging.exception("Xabarni yuborishda xatolik: %s", e)
        return


@dp.callback_query_handler(state=SendPhoto.send_all_1, chat_id=ADMINS[0])
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'send_message':
            async with state.proxy() as data:
                photo_file = data["photo_file"]
                caption = data['caption']
                keyboard = InlineKeyboardMarkup(row_width=1, resize_keyboard=True).add(
                    InlineKeyboardButton(text=data["btname_1"], url=data['url_1']))
            await admin_send_message_all(photo=photo_file, caption=caption, keyboard=keyboard)
            await state.finish()
        else:
            await call.message.delete()
            await state.finish()
    except Exception as e:
        logging.exception("Xabarni yuborishda xatolik: %s", e)
        return


@dp.message_handler(state=SendPhoto.waiting_for_button_name_2, content_types=ContentType.TEXT)
async def photo_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["btname_2"] = message.text
    await message.answer("Iltimos, ikkinchi tugma uchun URL manzilini kiriting.")
    await SendPhoto.waiting_for_button_url_2.set()


@dp.message_handler(state=SendPhoto.waiting_for_button_url_2, content_types=ContentType.TEXT)
async def photo_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['url_2'] = message.text
    await message.answer("Ikkinchi tugma uchun URL manzili qabul qilindi.", reply_markup=button_3)
    await SendPhoto.next_call_3.set()


@dp.callback_query_handler(state=SendPhoto.next_call_3, chat_id=ADMINS[0])
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'button_3':
            await call.message.answer('Iltimos, uchunchi tugma nomini kiriting.')
            await SendPhoto.waiting_for_button_name_3.set()
        elif call.data == 'send_message':
            async with state.proxy() as data:
                photo_file = data["photo_file"]
                caption = data['caption']
                keyboard = InlineKeyboardMarkup(row_width=1, resize_keyboard=True).add(
                    InlineKeyboardButton(text=data["btname_1"], url=data['url_1']),
                    InlineKeyboardButton(text=data["btname_2"], url=data['url_2']))
            await bot.send_photo(chat_id=ADMINS[0], photo=photo_file, caption=caption, reply_markup=keyboard)
            await bot.send_message(chat_id=ADMINS[0],
                                   text="<b>Siz yubormoqchi bo'lgan xabar\nxuddi shu ko'rinishda bo'ladi!\n\n"
                                        "✅ Tastiqlash   |   🗑 Bekor qilish</b>", reply_markup=tasdiqlash)
            await SendPhoto.send_all_2.set()
        else:
            await call.message.delete()
            await state.finish()
    except Exception as e:
        logging.exception("Xabarni yuborishda xatolik: %s", e)
        return


@dp.callback_query_handler(state=SendPhoto.send_all_2, chat_id=ADMINS[0])
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'send_message':
            async with state.proxy() as data:
                photo_file = data["photo_file"]
                caption = data['caption']
                keyboard = InlineKeyboardMarkup(row_width=1, resize_keyboard=True).add(
                    InlineKeyboardButton(text=data["btname_1"], url=data['url_1']),
                    InlineKeyboardButton(text=data["btname_2"], url=data['url_2']))
            await admin_send_message_all(photo=photo_file, caption=caption, keyboard=keyboard)
            await state.finish()
        else:
            await call.message.delete()
            await state.finish()
    except Exception as e:
        logging.exception("Xabarni yuborishda xatolik: %s", e)
        return


@dp.message_handler(state=SendPhoto.waiting_for_button_name_3, content_types=ContentType.TEXT)
async def photo_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["btname_3"] = message.text
    await message.answer("Iltimos, uchunchi tugma uchun URL manzilini kiriting.")
    await SendPhoto.waiting_for_button_url_3.set()


@dp.message_handler(state=SendPhoto.waiting_for_button_url_3, content_types=ContentType.TEXT)
async def photo_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['url_3'] = message.text
    await message.answer("Uchunchi tugma uchun URL manzili qabul qilindi.", reply_markup=button_4)
    await SendPhoto.next_call_4.set()


@dp.callback_query_handler(state=SendPhoto.next_call_4, chat_id=ADMINS[0])
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'button_4':
            await call.message.answer("Iltimos, to'rtinchi tugma nomini kiriting.")
            await SendPhoto.waiting_for_button_name_4.set()
        elif call.data == 'send_message':
            async with state.proxy() as data:
                photo_file = data["photo_file"]
                caption = data['caption']
                keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True).add(
                    InlineKeyboardButton(text=data["btname_1"], url=data['url_1']),
                    InlineKeyboardButton(text=data["btname_2"], url=data['url_2']),
                    InlineKeyboardButton(text=data["btname_3"], url=data['url_3']))
            await bot.send_photo(chat_id=ADMINS[0], photo=photo_file, caption=caption, reply_markup=keyboard)
            await bot.send_message(chat_id=ADMINS[0],
                                   text="<b>Siz yubormoqchi bo'lgan xabar\nxuddi shu ko'rinishda bo'ladi!\n\n"
                                        "✅ Tastiqlash   |   🗑 Bekor qilish</b>", reply_markup=tasdiqlash)
            await SendPhoto.send_all_3.set()
        else:
            await call.message.delete()
            await state.finish()
    except Exception as e:
        logging.exception("Xabarni yuborishda xatolik: %s", e)
        return


@dp.callback_query_handler(state=SendPhoto.send_all_3, chat_id=ADMINS[0])
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'send_message':
            async with state.proxy() as data:
                photo_file = data["photo_file"]
                caption = data['caption']
                keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True).add(
                    InlineKeyboardButton(text=data["btname_1"], url=data['url_1']),
                    InlineKeyboardButton(text=data["btname_2"], url=data['url_2']),
                    InlineKeyboardButton(text=data["btname_3"], url=data['url_3']))
            await admin_send_message_all(photo=photo_file, caption=caption, keyboard=keyboard)
            await state.finish()
        else:
            await call.message.delete()
            await state.finish()
    except Exception as e:
        logging.exception("Xabarni yuborishda xatolik: %s", e)
        return


@dp.message_handler(state=SendPhoto.waiting_for_button_name_4, content_types=ContentType.TEXT)
async def photo_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["btname_4"] = message.text
    await message.answer("Iltimos, uchunchi tugma uchun URL manzilini kiriting.")
    await SendPhoto.waiting_for_button_url_4.set()


@dp.message_handler(state=SendPhoto.waiting_for_button_url_4, content_types=ContentType.TEXT)
async def photo_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['url_4'] = message.text
    await message.answer("To'rtinchi tugma uchun URL manzili qabul qilindi.", reply_markup=button_5)
    await SendPhoto.next_call_5.set()


@dp.callback_query_handler(state=SendPhoto.next_call_5, chat_id=ADMINS[0])
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
    if call.data == 'send_message':
        async with state.proxy() as data:
            photo_file = data["photo_file"]
            caption = data['caption']
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True).add(
                InlineKeyboardButton(text=data["btname_1"], url=data['url_1']),
                InlineKeyboardButton(text=data["btname_2"], url=data['url_2']),
                InlineKeyboardButton(text=data["btname_3"], url=data['url_3']),
                InlineKeyboardButton(text=data["btname_4"], url=data['url_4']))
        await bot.send_photo(chat_id=ADMINS[0], photo=photo_file, caption=caption, reply_markup=keyboard)
        await bot.send_message(chat_id=ADMINS[0],
                               text="<b>Siz yubormoqchi bo'lgan xabar\nxuddi shu ko'rinishda bo'ladi!\n\n"
                                    "✅ Tastiqlash   |   🗑 Bekor qilish</b>", reply_markup=tasdiqlash)
        await SendPhoto.send_all_4.set()
    else:
        await call.message.delete()
        await state.finish()


@dp.callback_query_handler(state=SendPhoto.send_all_4, chat_id=ADMINS[0])
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
    if call.data == 'send_message':
        async with state.proxy() as data:
            photo_file = data["photo_file"]
            caption = data['caption']
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True).add(
                InlineKeyboardButton(text=data["btname_1"], url=data['url_1']),
                InlineKeyboardButton(text=data["btname_2"], url=data['url_2']),
                InlineKeyboardButton(text=data["btname_3"], url=data['url_3']),
                InlineKeyboardButton(text=data["btname_4"], url=data['url_4']))
        await admin_send_message_all(photo=photo_file, caption=caption, keyboard=keyboard)
        await state.finish()
    else:
        await call.message.delete()
        await state.finish()


## =============================== SEND A VIDEO ===================================


@dp.callback_query_handler(text="video", chat_id=ADMINS[0])
async def send_video_to_all(call: types.CallbackQuery):
    chat_id = call.from_user.id
    callback_id = call.message.message_id
    await bot.edit_message_text(chat_id=chat_id, message_id=callback_id, text="🎥 SEND A VIDEO")
    await SendVideo.video.set()


@dp.message_handler(state=SendVideo.video, content_types=ContentType.VIDEO)
async def send_video_to_all(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["video_file"] = message.video.file_id
    await message.answer("Iltimos, video uchun ma'lumotlarni kiriting.")
    await SendVideo.waiting_for_caption.set()


@dp.message_handler(state=SendVideo.waiting_for_caption, content_types=ContentType.TEXT)
async def video_caption(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['caption'] = await replace_text_with_links(message.text)
    await message.answer("Xabar uchun tugma yaratishni hohlaysizmi?", reply_markup=add_btn)
    await SendVideo.waiting_for_new_btn.set()


@dp.callback_query_handler(state=SendVideo.waiting_for_new_btn, chat_id=ADMINS[0])
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
    if call.data == 'add_btn':
        await call.message.answer('Iltimos, birinchi tugma nomini kiriting.')
        await SendVideo.waiting_for_button_name_1.set()
    elif call.data == 'send_message':
        async with state.proxy() as data:
            video_file = data["video_file"]
            caption = data['caption']
        await bot.send_video(chat_id=ADMINS[0], video=video_file, caption=f"<b>{caption}</b>")
        await bot.send_message(chat_id=ADMINS[0],
                               text="<b>Siz yubormoqchi bo'lgan xabar\nxuddi shu ko'rinishda bo'ladi!\n\n"
                                    "✅ Tastiqlash   |   🗑 Bekor qilish</b>", reply_markup=tasdiqlash)
        await SendPhoto.waiting_for_is_not_btn.set()
    else:
        await call.message.delete()
        await state.finish()


@dp.callback_query_handler(state=SendPhoto.waiting_for_is_not_btn, chat_id=ADMINS[0])
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
    if call.data == 'send_message':
        async with state.proxy() as data:
            video_file = data["video_file"]
            caption = data['caption']
        await admin_send_message_all(video=video_file, caption=caption)
        await state.finish()
    else:
        await call.message.delete()
        await state.finish()


@dp.message_handler(state=SendVideo.waiting_for_button_name_1, content_types=ContentType.TEXT)
async def video_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["btname_1"] = message.text
    await message.answer("Iltimos, birinchi tugma uchun URL manzilini kiriting.")
    await SendVideo.waiting_for_button_url_1.set()


@dp.message_handler(state=SendVideo.waiting_for_button_url_1, content_types=ContentType.TEXT)
async def video_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['url_1'] = message.text
    await message.answer("Birinchi tugma uchun URL manzili qabul qilindi.", reply_markup=button_2)
    await SendVideo.next_call_2.set()


@dp.callback_query_handler(state=SendVideo.next_call_2, chat_id=ADMINS[0])
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
    if call.data == 'button_2':
        await call.message.answer('Iltimos, ikkinchi tugma nomini kiriting.')
        await SendVideo.waiting_for_button_name_2.set()
    elif call.data == 'send_message':
        async with state.proxy() as data:
            video_file = data["video_file"]
            caption = data['caption']
            keyboard = InlineKeyboardMarkup(row_width=1, resize_keyboard=True).add(
                InlineKeyboardButton(text=data["btname_1"], url=data['url_1']))
        await bot.send_video(chat_id=ADMINS[0], video=video_file, caption=caption,
                             reply_markup=keyboard)
        await bot.send_message(chat_id=ADMINS[0],
                               text="<b>Siz yubormoqchi bo'lgan xabar\nxuddi shu ko'rinishda bo'ladi!\n\n"
                                    "✅ Tastiqlash   |   🗑 Bekor qilish</b>", reply_markup=tasdiqlash)
        await SendVideo.send_all_1.set()
    else:
        await call.message.delete()
        await state.finish()


@dp.callback_query_handler(state=SendVideo.send_all_1, chat_id=ADMINS[0])
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
    if call.data == 'send_message':
        async with state.proxy() as data:
            video_file = data["video_file"]
            caption = data['caption']
            keyboard = InlineKeyboardMarkup(row_width=1, resize_keyboard=True).add(
                InlineKeyboardButton(text=data["btname_1"], url=data['url_1']))
        await admin_send_message_all(video=video_file, caption=caption, keyboard=keyboard)
        await state.finish()
    else:
        await call.message.delete()
        await state.finish()


@dp.message_handler(state=SendVideo.waiting_for_button_name_2, content_types=ContentType.TEXT)
async def video_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["btname_2"] = message.text
    await message.answer("Iltimos, ikkinchi tugma uchun URL manzilini kiriting.")
    await SendVideo.waiting_for_button_url_2.set()


@dp.message_handler(state=SendVideo.waiting_for_button_url_2, content_types=ContentType.TEXT)
async def video_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['url_2'] = message.text
    await message.answer("Ikkinchi tugma uchun URL manzili qabul qilindi.", reply_markup=button_3)
    await SendVideo.next_call_3.set()


@dp.callback_query_handler(state=SendVideo.next_call_3, chat_id=ADMINS[0])
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
    if call.data == 'button_3':
        await call.message.answer('Iltimos, uchunchi tugma nomini kiriting.')
        await SendVideo.waiting_for_button_name_3.set()
    elif call.data == 'send_message':
        async with state.proxy() as data:
            video_file = data["video_file"]
            caption = data['caption']
            keyboard = InlineKeyboardMarkup(row_width=1, resize_keyboard=True).add(
                InlineKeyboardButton(text=data["btname_1"], url=data['url_1']),
                InlineKeyboardButton(text=data["btname_2"], url=data['url_2']))
        await bot.send_video(chat_id=ADMINS[0], video=video_file, caption=caption, reply_markup=keyboard)
        await bot.send_message(chat_id=ADMINS[0],
                               text="<b>Siz yubormoqchi bo'lgan xabar\nxuddi shu ko'rinishda bo'ladi!\n\n"
                                    "✅ Tastiqlash   |   🗑 Bekor qilish</b>", reply_markup=tasdiqlash)
        await SendVideo.send_all_2.set()
    else:
        await call.message.delete()
        await state.finish()


@dp.callback_query_handler(state=SendVideo.send_all_2, chat_id=ADMINS[0])
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
    if call.data == 'send_message':
        async with state.proxy() as data:
            video_file = data["video_file"]
            caption = data['caption']
            keyboard = InlineKeyboardMarkup(row_width=1, resize_keyboard=True).add(
                InlineKeyboardButton(text=data["btname_1"], url=data['url_1']),
                InlineKeyboardButton(text=data["btname_2"], url=data['url_2']))
        await admin_send_message_all(video=video_file, caption=caption, keyboard=keyboard)
        await state.finish()
    else:
        await call.message.delete()
        await state.finish()


@dp.message_handler(state=SendVideo.waiting_for_button_name_3, content_types=ContentType.TEXT)
async def video_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["btname_3"] = message.text
    await message.answer("Iltimos, uchunchi tugma uchun URL manzilini kiriting.")
    await SendVideo.waiting_for_button_url_3.set()


@dp.message_handler(state=SendVideo.waiting_for_button_url_3, content_types=ContentType.TEXT)
async def video_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['url_3'] = message.text
    await message.answer("Uchunchi tugma uchun URL manzili qabul qilindi.", reply_markup=button_4)
    await SendVideo.next_call_4.set()


@dp.callback_query_handler(state=SendVideo.next_call_4, chat_id=ADMINS[0])
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
    if call.data == 'button_4':
        await call.message.answer("Iltimos, to'rtinchi tugma nomini kiriting.")
        await SendVideo.waiting_for_button_name_4.set()
    elif call.data == 'send_message':
        async with state.proxy() as data:
            video_file = data["video_file"]
            caption = data['caption']
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True).add(
                InlineKeyboardButton(text=data["btname_1"], url=data['url_1']),
                InlineKeyboardButton(text=data["btname_2"], url=data['url_2']),
                InlineKeyboardButton(text=data["btname_3"], url=data['url_3']))
        await bot.send_video(chat_id=ADMINS[0], video=video_file, caption=caption, reply_markup=keyboard)
        await bot.send_message(chat_id=ADMINS[0],
                               text="<b>Siz yubormoqchi bo'lgan xabar\nxuddi shu ko'rinishda bo'ladi!\n\n"
                                    "✅ Tastiqlash   |   🗑 Bekor qilish</b>", reply_markup=tasdiqlash)
        await SendVideo.send_all_3.set()
    else:
        await call.message.answer('❌Xabar yuborish bekor qilindi.')
        return await state.finish()


@dp.callback_query_handler(state=SendVideo.send_all_3, chat_id=ADMINS[0])
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
    if call.data == 'send_message':
        async with state.proxy() as data:
            video_file = data["video_file"]
            caption = data['caption']
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True).add(
                InlineKeyboardButton(text=data["btname_1"], url=data['url_1']),
                InlineKeyboardButton(text=data["btname_2"], url=data['url_2']),
                InlineKeyboardButton(text=data["btname_3"], url=data['url_3']))
        await admin_send_message_all(video=video_file, caption=caption, keyboard=keyboard)
        await state.finish()
    else:
        await call.message.delete()
        await state.finish()


@dp.message_handler(state=SendVideo.waiting_for_button_name_4, content_types=ContentType.TEXT)
async def video_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["btname_4"] = message.text
    await message.answer("Iltimos, uchunchi tugma uchun URL manzilini kiriting.")
    await SendVideo.waiting_for_button_url_4.set()


@dp.message_handler(state=SendVideo.waiting_for_button_url_4, content_types=ContentType.TEXT)
async def video_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['url_4'] = message.text
    await message.answer("To'rtinchi tugma uchun URL manzili qabul qilindi.", reply_markup=button_5)
    await SendVideo.next_call_5.set()


@dp.callback_query_handler(state=SendVideo.next_call_5, chat_id=ADMINS[0])
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
    if call.data == 'send_message':
        async with state.proxy() as data:
            video_file = data["video_file"]
            caption = data['caption']
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True).add(
                InlineKeyboardButton(text=data["btname_1"], url=data['url_1']),
                InlineKeyboardButton(text=data["btname_2"], url=data['url_2']),
                InlineKeyboardButton(text=data["btname_3"], url=data['url_3']),
                InlineKeyboardButton(text=data["btname_4"], url=data['url_4']))
        await bot.send_video(chat_id=ADMINS[0], video=video_file, caption=caption, reply_markup=keyboard)
        await bot.send_message(chat_id=ADMINS[0],
                               text="<b>Siz yubormoqchi bo'lgan xabar\nxuddi shu ko'rinishda bo'ladi!\n\n"
                                    "✅ Tastiqlash   |   🗑 Bekor qilish</b>", reply_markup=tasdiqlash)
        await SendVideo.send_all_4.set()
    else:
        await call.message.delete()
        await state.finish()


@dp.callback_query_handler(state=SendVideo.send_all_4, chat_id=ADMINS[0])
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
    if call.data == 'send_message':
        async with state.proxy() as data:
            video_file = data["video_file"]
            caption = data['caption']
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True).add(
                InlineKeyboardButton(text=data["btname_1"], url=data['url_1']),
                InlineKeyboardButton(text=data["btname_2"], url=data['url_2']),
                InlineKeyboardButton(text=data["btname_3"], url=data['url_3']),
                InlineKeyboardButton(text=data["btname_4"], url=data['url_4']))
        await admin_send_message_all(video=video_file, caption=caption, keyboard=keyboard)
        await state.finish()
    else:
        await call.message.delete()
        await state.finish()


'''
📹 Instagramdan istalgan turdagi kontentni tez va oson yuklab beradigan bot!

🤖 /start tugmasini bosing va shaxsiy (Robotingizdan)[https://t.me/LikeeinBot] foydalanishni boshlang 

📹 Бот, который быстро и легко загружает любой тип контента из Инстаграм!

🤖 Нажмите кнопку /start и начните использовать своего личного (Pобота)[https://t.me/LikeeinBot]


📹 A bot that downloads any type of content from Instagram quickly and easily!

🤖 Press the /start button and start using your personal (Robot)[https://t.me/LikeeinBot]

'''
