from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType
from keyboards import *
from .send_all import *
from .send_admin import *


# =========================================📄 SEND TEXT =============================================


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
    try:
        async with state.proxy() as data:
            data['text'] = await replace_text_to_links(text=message.text)
        await bot.send_message(
            chat_id=message.chat.id,
            text="<b>Xabar uchun tugma yaratishni hohlaysizmi?</b>",
            reply_markup=add_kb
        )
        await SendText.waiting_for_new_btn.set()
    except Exception as e:
        return await state.finish()


@dp.callback_query_handler(state=SendText.waiting_for_new_btn, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'add_kb':
            await bot.send_message(chat_id=call.message.chat.id, text='<b>Iltimos, 1 - tugma nomini kiriting!</b>')
            await SendText.waiting_for_button_name_1.set()
        elif call.data == 'send_message':
            async with state.proxy() as data:
                text = data.get('text')
            await send_message_admin(text=text)
            await SendText.waiting_for_is_not_btn.set()
        else:
            await call.message.delete()
            return await state.finish()
    except Exception as e:
        return await state.finish()


@dp.callback_query_handler(state=SendText.waiting_for_is_not_btn, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'send_message':
            async with state.proxy() as data:
                text = data.get('text')
            await admin_send_message_all(text=text)
            return await state.finish()
        else:
            await call.message.delete()
            return await state.finish()
    except Exception as e:
        return await state.finish()


@dp.message_handler(state=SendText.waiting_for_button_name_1, content_types=ContentType.TEXT)
async def bot_echo(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data["kb_1"] = message.text
        await bot.send_message(chat_id=message.chat.id, text="Iltimos, 1 - tugma uchun URL manzilini kiriting.")
        await SendText.waiting_for_button_url_1.set()
    except Exception as e:
        return await state.finish()


@dp.message_handler(state=SendText.waiting_for_button_url_1, content_types=ContentType.TEXT)
async def photo_button_url(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['url_1'] = message.text
        await bot.send_message(
            chat_id=message.chat.id,
            text="1 - tugma uchun URL manzili qabul qilindi.",
            reply_markup=kb_2
        )
        await SendText.next_call_2.set()
    except Exception as e:
        return await state.finish()


@dp.callback_query_handler(state=SendText.next_call_2, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'kb_2':
            await bot.send_message(chat_id=call.message.chat.id, text='Iltimos, 2 - tugma nomini kiriting.')
            await SendText.waiting_for_button_name_2.set()
        elif call.data == 'send_message':
            async with state.proxy() as data:
                text = data.get('text')
            keyboard = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text=data["kb_1"], url=data['url_1']))
            await send_message_admin(text=text, keyboard=keyboard)
            await SendText.send_all_1.set()
        else:
            await call.message.delete()
            return await state.finish()
    except Exception as e:
        return await state.finish()


@dp.callback_query_handler(state=SendText.send_all_1, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'send_message':
            async with state.proxy() as data:
                text = data.get('text')
            keyboard = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text=data["kb_1"], url=data['url_1']))
            await admin_send_message_all(text=text, keyboard=keyboard)
            return await state.finish()
        else:
            await call.message.delete()
            return await state.finish()
    except Exception as e:
        return await state.finish()


@dp.message_handler(state=SendText.waiting_for_button_name_2, content_types=ContentType.TEXT)
async def photo_button_name(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data["kb_2"] = message.text
        await bot.send_message(chat_id=message.chat.id, text="Iltimos, 2 - tugma uchun URL manzilini kiriting.")
        await SendText.waiting_for_button_url_2.set()
    except Exception as e:
        return await state.finish()


@dp.message_handler(state=SendText.waiting_for_button_url_2, content_types=ContentType.TEXT)
async def photo_button_url(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['url_2'] = message.text
        await bot.send_message(
            chat_id=message.chat.id,
            text="2 - tugma uchun URL manzili qabul qilindi.",
            reply_markup=kb_5
        )
        await SendText.next_call_3.set()
    except Exception as e:
        return await state.finish()


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
            await send_message_admin(text=text, keyboard=keyboard)
            await SendText.send_all_2.set()
        else:
            await call.message.delete()
            return await state.finish()
    except Exception as e:
        return await state.finish()


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
            return await state.finish()
        else:
            await call.message.delete()
            return await state.finish()
    except Exception as e:
        return await state.finish()


## =============================== SEND A PHOTO ===================================


@dp.callback_query_handler(text="photo", chat_id=ADMINS[0])
async def send_photo_to_all(call: types.CallbackQuery):
    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text="🖼 SEND PHOTO")
    await SendPhoto.photo.set()


@dp.message_handler(state=SendPhoto.photo, content_types=ContentType.PHOTO)
async def send_photo_to_all(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data["photo"] = message.photo[-1].file_id
        await bot.send_message(chat_id=message.chat.id, text="Iltimos, photo uchun ma'lumotlarni kiriting.")
        await SendPhoto.waiting_for_caption.set()
    except Exception as e:
        return await state.finish()


@dp.message_handler(state=SendPhoto.waiting_for_caption, content_types=ContentType.TEXT)
async def video_caption(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['caption'] = await replace_text_to_links(text=message.text)
        await bot.send_message(
            chat_id=message.chat.id,
            text="Xabar uchun tugma yaratishni hohlaysizmi?",
            reply_markup=add_kb
        )
        await SendPhoto.waiting_for_new_btn.set()
    except Exception as e:
        return await state.finish()


@dp.callback_query_handler(state=SendPhoto.waiting_for_new_btn, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'add_kb':
            await bot.send_message(chat_id=call.message.chat.id, text='Iltimos, 1 - tugma nomini kiriting.')
            await SendPhoto.waiting_for_button_name_1.set()
        elif call.data == 'send_message':
            async with state.proxy() as data:
                photo = data["photo"]
                caption = data['caption']
            await send_message_admin(photo=photo, caption=caption)
            await SendPhoto.waiting_for_is_not_btn.set()
        else:
            await call.message.delete()
            return await state.finish()
    except Exception as e:
        return await state.finish()


@dp.callback_query_handler(state=SendPhoto.waiting_for_is_not_btn, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'send_message':
            async with state.proxy() as data:
                photo = data["photo"]
                caption = data['caption']
            await admin_send_message_all(photo=photo, caption=caption)
            return await state.finish()
        else:
            await call.message.delete()
            return await state.finish()
    except Exception as e:
        return await state.finish()


@dp.message_handler(state=SendPhoto.waiting_for_button_name_1, content_types=ContentType.TEXT)
async def photo_button_name(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data["kb_1"] = message.text
        await bot.send_message(chat_id=message.chat.id, text="Iltimos, 1 - tugma uchun URL manzilini kiriting.")
        await SendPhoto.waiting_for_button_url_1.set()
    except Exception as e:
        return await state.finish()


@dp.message_handler(state=SendPhoto.waiting_for_button_url_1, content_types=ContentType.TEXT)
async def photo_button_url(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['url_1'] = message.text
        await bot.send_message(
            chat_id=message.chat.id,
            text="1 - tugma uchun URL manzili qabul qilindi.",
            reply_markup=kb_2
        )
        await SendPhoto.next_call_2.set()
    except Exception as e:
        return await state.finish()


@dp.callback_query_handler(state=SendPhoto.next_call_2, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'kb_2':
            await bot.send_message(chat_id=call.message.chat.id, text='Iltimos, 2 - tugma nomini kiriting.')
            await SendPhoto.waiting_for_button_name_2.set()
        elif call.data == 'send_message':
            async with state.proxy() as data:
                photo = data["photo"]
                caption = data['caption']
            keyboard = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text=data["kb_1"], url=data['url_1']))
            await send_message_admin(photo=photo, caption=caption, keyboard=keyboard)
            await SendPhoto.send_all_1.set()
        else:
            await call.message.delete()
            return await state.finish()
    except Exception as e:
        return await state.finish()


@dp.callback_query_handler(state=SendPhoto.send_all_1, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'send_message':
            async with state.proxy() as data:
                photo = data["photo"]
                caption = data['caption']
            keyboard = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text=data["kb_1"], url=data['url_1']))
            await admin_send_message_all(photo=photo, caption=caption, keyboard=keyboard)
            return await state.finish()
        else:
            await call.message.delete()
            return await state.finish()
    except Exception as e:
        return await state.finish()


@dp.message_handler(state=SendPhoto.waiting_for_button_name_2, content_types=ContentType.TEXT)
async def photo_button_name(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data["kb_2"] = message.text
        await bot.send_message(hat_id=message.chat.id, text="Iltimos, 2 - tugma uchun URL manzilini kiriting.")
        await SendPhoto.waiting_for_button_url_2.set()
    except Exception as e:
        return await state.finish()


@dp.message_handler(state=SendPhoto.waiting_for_button_url_2, content_types=ContentType.TEXT)
async def photo_button_url(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['url_2'] = message.text
        await bot.send_message(
            chat_id=message.chat.id,
            text="2 - tugma uchun URL manzili qabul qilindi.",
            reply_markup=kb_3
        )
        await SendPhoto.next_call_3.set()
    except Exception as e:
        return await state.finish()


@dp.callback_query_handler(state=SendPhoto.next_call_3, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'kb_3':
            await bot.send_message(chat_id=call.message.chat.id, text='Iltimos, 3 - tugma nomini kiriting.')
            await SendPhoto.waiting_for_button_name_3.set()
        elif call.data == 'send_message':
            async with state.proxy() as data:
                photo = data["photo"]
                caption = data['caption']
            keyboard = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(text=data["kb_1"], url=data['url_1']),
                InlineKeyboardButton(text=data["kb_2"], url=data['url_2']))
            await send_message_admin(photo=photo, caption=caption, keyboard=keyboard)
            await SendPhoto.send_all_2.set()
        else:
            await call.message.delete()
            return await state.finish()
    except Exception as e:
        return await state.finish()


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
            return await state.finish()
        else:
            await call.message.delete()
            return await state.finish()
    except Exception as e:
        return await state.finish()


@dp.message_handler(state=SendPhoto.waiting_for_button_name_3, content_types=ContentType.TEXT)
async def photo_button_name(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data["kb_3"] = message.text
        await bot.send_message(chat_id=message.chat.id, text="Iltimos, 3 - tugma uchun URL manzilini kiriting.")
        await SendPhoto.waiting_for_button_url_3.set()
    except Exception as e:
        return await state.finish()


@dp.message_handler(state=SendPhoto.waiting_for_button_url_3, content_types=ContentType.TEXT)
async def photo_button_url(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['url_3'] = message.text
        await bot.send_message(
            chat_id=message.chat.id,
            text="3 - tugma uchun URL manzili qabul qilindi.",
            reply_markup=kb_4
        )
        await SendPhoto.next_call_4.set()
    except Exception as e:
        return await state.finish()


@dp.callback_query_handler(state=SendPhoto.next_call_4, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'kb_4':
            await bot.send_message(
                chat_id=call.message.chat.id,
                text="Iltimos, 4 - tugma nomini kiriting."
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
            await send_message_admin(photo=photo, caption=caption, keyboard=keyboard)
            await SendPhoto.send_all_3.set()
        else:
            await call.message.delete()
            return await state.finish()
    except Exception as e:
        return await state.finish()


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
            return await state.finish()
        else:
            await call.message.delete()
            return await state.finish()
    except Exception as e:
        return await state.finish()


@dp.message_handler(state=SendPhoto.waiting_for_button_name_4, content_types=ContentType.TEXT)
async def photo_button_name(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data["kb_4"] = message.text
        await bot.send_message(chat_id=message.chat.id, text="Iltimos, 3 - tugma uchun URL manzilini kiriting.")
        await SendPhoto.waiting_for_button_url_4.set()
    except Exception as e:
        return await state.finish()


@dp.message_handler(state=SendPhoto.waiting_for_button_url_4, content_types=ContentType.TEXT)
async def photo_button_url(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['url_4'] = message.text
        await bot.send_message(
            chat_id=message.chat.id,
            text="4 - tugma uchun URL manzili qabul qilindi.",
            reply_markup=kb_5
        )
        await SendPhoto.next_call_5.set()
    except Exception as e:
        return await state.finish()


@dp.callback_query_handler(state=SendPhoto.next_call_5, chat_id=ADMINS[0])
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
                InlineKeyboardButton(text=data["kb_3"], url=data['url_3']),
                InlineKeyboardButton(text=data["kb_4"], url=data['url_4']))
            await send_message_admin(photo=photo, caption=caption, keyboard=keyboard)
            await SendPhoto.send_all_4.set()
        else:
            await call.message.delete()
            return await state.finish()
    except Exception as e:
        return await state.finish()


@dp.callback_query_handler(state=SendPhoto.send_all_4, chat_id=ADMINS[0])
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
                InlineKeyboardButton(text=data["kb_3"], url=data['url_3']),
                InlineKeyboardButton(text=data["kb_4"], url=data['url_4']))
            await admin_send_message_all(photo=photo, caption=caption, keyboard=keyboard)
            return await state.finish()
        else:
            await call.message.delete()
            return await state.finish()
    except Exception as e:
        return await state.finish()


## =============================== SEND A VIDEO ===================================


@dp.callback_query_handler(text="video", chat_id=ADMINS[0])
async def send_video_to_all(call: types.CallbackQuery):
    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text="📽️ SEND VIDEO")
    await SendVideo.video.set()


@dp.message_handler(state=SendVideo.video, content_types=ContentType.VIDEO)
async def send_video_to_all(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data["video"] = message.video.file_id
        await bot.send_message(chat_id=message.chat.id, text="Iltimos, video uchun ma'lumotlarni kiriting.")
        await SendVideo.waiting_for_caption.set()
    except Exception as e:
        return await state.finish()


@dp.message_handler(state=SendVideo.waiting_for_caption, content_types=ContentType.TEXT)
async def video_caption(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['caption'] = await replace_text_to_links(text=message.text)
        await bot.send_message(
            chat_id=message.chat.id,
            text="Xabar uchun tugma yaratishni hohlaysizmi?",
            reply_markup=add_kb
        )
        await SendVideo.waiting_for_new_btn.set()
    except Exception as e:
        return await state.finish()


@dp.callback_query_handler(state=SendVideo.waiting_for_new_btn, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'add_kb':
            await bot.send_message(chat_id=call.message.chat.id, text='Iltimos, 1 - tugma nomini kiriting.')
            await SendVideo.waiting_for_button_name_1.set()
        elif call.data == 'send_message':
            async with state.proxy() as data:
                video = data["video"]
                caption = data['caption']
            await send_message_admin(video=video, caption=caption)
            await SendPhoto.waiting_for_is_not_btn.set()
        else:
            await call.message.delete()
            return await state.finish()
    except Exception as e:
        return await state.finish()


@dp.callback_query_handler(state=SendPhoto.waiting_for_is_not_btn, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'send_message':
            async with state.proxy() as data:
                video = data["video"]
                caption = data['caption']
            await admin_send_message_all(video=video, caption=caption)
            return await state.finish()
        else:
            await call.message.delete()
            return await state.finish()
    except Exception as e:
        return await state.finish()


@dp.message_handler(state=SendVideo.waiting_for_button_name_1, content_types=ContentType.TEXT)
async def video_button_name(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data["kb_1"] = message.text
        await bot.send_message(chat_id=message.chat.id, text="Iltimos, 1 - tugma uchun URL manzilini kiriting.")
        await SendVideo.waiting_for_button_url_1.set()
    except Exception as e:
        return await state.finish()


@dp.message_handler(state=SendVideo.waiting_for_button_url_1, content_types=ContentType.TEXT)
async def video_button_url(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['url_1'] = message.text
        await bot.send_message(
            chat_id=message.chat.id,
            text="1 - tugma uchun URL manzili qabul qilindi.",
            reply_markup=kb_2
        )
        await SendVideo.next_call_2.set()
    except Exception as e:
        return await state.finish()


@dp.callback_query_handler(state=SendVideo.next_call_2, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'kb_2':
            await bot.send_message(chat_id=call.message.chat.id, text='Iltimos, 2 - tugma nomini kiriting.')
            await SendVideo.waiting_for_button_name_2.set()
        elif call.data == 'send_message':
            async with state.proxy() as data:
                video = data["video"]
                caption = data['caption']
            keyboard = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text=data["kb_1"], url=data['url_1']))
            await send_message_admin(video=video, caption=caption, keyboard=keyboard)
            await SendVideo.send_all_1.set()
        else:
            await call.message.delete()
            return await state.finish()
    except Exception as e:
        return await state.finish()


@dp.callback_query_handler(state=SendVideo.send_all_1, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'send_message':
            async with state.proxy() as data:
                video = data["video"]
                caption = data['caption']
            keyboard = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text=data["kb_1"], url=data['url_1']))
            await admin_send_message_all(video=video, caption=caption, keyboard=keyboard)
            return await state.finish()
        else:
            await call.message.delete()
            return await state.finish()
    except Exception as e:
        return await state.finish()


@dp.message_handler(state=SendVideo.waiting_for_button_name_2, content_types=ContentType.TEXT)
async def video_button_name(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data["kb_2"] = message.text
        await bot.send_message(chat_id=message.chat.id, text="Iltimos, 2 - tugma uchun URL manzilini kiriting.")
        await SendVideo.waiting_for_button_url_2.set()
    except Exception as e:
        return await state.finish()


@dp.message_handler(state=SendVideo.waiting_for_button_url_2, content_types=ContentType.TEXT)
async def video_button_url(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['url_2'] = message.text
        await bot.send_message(
            chat_id=message.chat.id,
            text="2 - tugma uchun URL manzili qabul qilindi.",
            reply_markup=kb_3
        )
        await SendVideo.next_call_3.set()
    except Exception as e:
        return await state.finish()


@dp.callback_query_handler(state=SendVideo.next_call_3, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'kb_3':
            await bot.send_message(chat_id=call.message.chat.id, text='Iltimos, 3 - tugma nomini kiriting.')
            await SendVideo.waiting_for_button_name_3.set()
        elif call.data == 'send_message':
            async with state.proxy() as data:
                video = data["video"]
                caption = data['caption']
            keyboard = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(text=data["kb_1"], url=data['url_1']),
                InlineKeyboardButton(text=data["kb_2"], url=data['url_2']))
            await send_message_admin(video=video, caption=caption, keyboard=keyboard)
            await SendVideo.send_all_2.set()
        else:
            await call.message.delete()
            return await state.finish()
    except Exception as e:
        return await state.finish()


@dp.callback_query_handler(state=SendVideo.send_all_2, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'send_message':
            async with state.proxy() as data:
                video = data["video"]
                caption = data['caption']
            keyboard = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(text=data["kb_1"], url=data['url_1']),
                InlineKeyboardButton(text=data["kb_2"], url=data['url_2']))
            await admin_send_message_all(video=video, caption=caption, keyboard=keyboard)
            return await state.finish()
        else:
            await call.message.delete()
            return await state.finish()
    except Exception as e:
        return await state.finish()


@dp.message_handler(state=SendVideo.waiting_for_button_name_3, content_types=ContentType.TEXT)
async def video_button_name(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data["kb_3"] = message.text
        await bot.send_message(chat_id=message.chat.id, text="Iltimos, 3 - tugma uchun URL manzilini kiriting.")
        await SendVideo.waiting_for_button_url_3.set()
    except Exception as e:
        return await state.finish()


@dp.message_handler(state=SendVideo.waiting_for_button_url_3, content_types=ContentType.TEXT)
async def video_button_url(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['url_3'] = message.text
        await bot.send_message(
            chat_id=message.chat.id,
            text="3 - tugma uchun URL manzili qabul qilindi.",
            reply_markup=kb_4
        )
        await SendVideo.next_call_4.set()
    except Exception as e:
        return await state.finish()


@dp.callback_query_handler(state=SendVideo.next_call_4, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == 'kb_4':
            await bot.send_message(chat_id=call.message.chat.id, text="Iltimos, 4 - tugma nomini kiriting.")
            await SendVideo.waiting_for_button_name_4.set()
        elif call.data == 'send_message':
            async with state.proxy() as data:
                video = data["video"]
                caption = data['caption']
            keyboard = InlineKeyboardMarkup(row_width=2).add(
                InlineKeyboardButton(text=data["kb_1"], url=data['url_1']),
                InlineKeyboardButton(text=data["kb_2"], url=data['url_2']),
                InlineKeyboardButton(text=data["kb_3"], url=data['url_3']))
            await send_message_admin(video=video, caption=caption, keyboard=keyboard)
            await SendVideo.send_all_3.set()
        else:
            await call.message.delete()
            return await state.finish()
    except Exception as e:
        return await state.finish()


@dp.callback_query_handler(state=SendVideo.send_all_3, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
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
            return await state.finish()
        else:
            await call.message.delete()
            return await state.finish()
    except Exception as e:
        return await state.finish()


@dp.message_handler(state=SendVideo.waiting_for_button_name_4, content_types=ContentType.TEXT)
async def video_button_name(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data["kb_4"] = message.text
        await bot.send_message(chat_id=message.chat.id, text="Iltimos, 3 - tugma uchun URL manzil kiriting.")
        await SendVideo.waiting_for_button_url_4.set()
    except Exception as e:
        return await state.finish()


@dp.message_handler(state=SendVideo.waiting_for_button_url_4, content_types=ContentType.TEXT)
async def video_button_url(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['url_4'] = message.text
        await bot.send_message(
            chat_id=message.chat.id,
            text="4 - tugma uchun URL manzili qabul qilindi.",
            reply_markup=kb_5
        )
        await SendVideo.next_call_5.set()
    except Exception as e:
        return await state.finish()


@dp.callback_query_handler(state=SendVideo.next_call_5, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
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
            await send_message_admin(video=video, caption=caption, keyboard=keyboard)
            await SendVideo.send_all_4.set()
        else:
            await call.message.delete()
            return await state.finish()
    except Exception as e:
        return await state.finish()


@dp.callback_query_handler(state=SendVideo.send_all_4, chat_id=ADMINS[0])
async def send_ads(call: types.CallbackQuery, state: FSMContext):
    try:
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
            return await state.finish()
        else:
            await call.message.delete()
            return await state.finish()
    except Exception as e:
        return await state.finish()
