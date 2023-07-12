from databasedb.models import *
from keyboards import *
from states import *
from loader import *


async def replace_text_with_links(text: str) -> any:
    try:
        parts = []
        while True:
            start = text.find("[")
            end = text.find("]")
            if start == -1 or end == -1:
                parts.append(text)
                break
            start += 1
            link_start_index = text.find("(", end)
            link_end_index = text.find(")", link_start_index)
            if link_start_index == -1 or link_end_index == -1:
                break
            link = text[link_start_index + 1:link_end_index].strip("()")
            text_part = text[start:end].strip()
            parts.append(text[:start - 1])
            parts.append(f"<a href='{link}'>{text_part}</a>")
            text = text[link_end_index + 1:]
        if not parts:
            return None
        return ''.join(parts)
    except:
        await bot.send_message(ADMINS, "❌ Havolani aniqlashda xatolik yuz berdi!")
        return None


## =============================== SEND A TEXT ===================================


@dp.callback_query_handler(text="text", chat_id=ADMINS)
async def send_voice_to_all(call: types.CallbackQuery):
    chat_id = call.from_user.id
    callback_id = call.message.message_id
    await bot.edit_message_text(chat_id=chat_id, message_id=callback_id, text="🎙 SEND A TEXT")
    await SendText.text.set()


@dp.message_handler(state=SendText.text, content_types=ContentType.TEXT)
async def video_caption(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['caption'] = await replace_text_with_links(message.text)
    await message.answer("Xabar uchun tugma yaratishni hohlaysizmi?", reply_markup=add_btn)
    await SendText.waiting_for_new_btn.set()


@dp.callback_query_handler(state=SendText.waiting_for_new_btn, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'add_btn':
        await call.message.answer('Iltimos, birinchi tugma nomini kiriting.')
        await SendText.waiting_for_button_name_1.set()
    elif call.data == 'send_message':
        async with state.proxy() as data:
            caption = data['caption']
        await bot.send_message(chat_id=ADMINS, text=f"<b>{caption}</b>", disable_web_page_preview=True)
        await bot.send_message(chat_id=ADMINS, text="Siz yubormoqchi bo'lgan xabar xuddi shunday kurinishda boladi."
                                                    "Haqiqatdan ham shu xabarni barcha foydalanuvchilarga yuborishni istaysizmi?\n"
                                                    "✅ Tastiqlash yoki ❌ Bekor qilish tugmasini bosing.",
                               reply_markup=tasdiqlash)
        await SendText.waiting_for_is_not_btn.set()
    else:
        await call.message.delete()
        await state.finish()


@dp.callback_query_handler(state=SendText.waiting_for_is_not_btn, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'send_message':
        async with state.proxy() as data:
            caption = data['caption']
            all_user_id = await User.get_all_user()
            all_group_id = await Group.get_all_group()
            count_user = 0
            count_group = 0
            try:
                for user_id in all_user_id:
                    if await bot.send_message(chat_id=user_id, text=f"<b>{caption}</b>", disable_web_page_preview=True):
                        count_user += 1
                    await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
                await bot.send_message(ADMINS,
                                       f"Sizning xabaringiz barcha <b>{count_user} ta</b> foydalanuvchiga muvaffaqiyatli yuborildi.")

                for group_id in all_group_id:
                    if await bot.send_message(chat_id=group_id, text=f"<b>{caption}</b>",
                                              disable_web_page_preview=True):
                        count_group += 1
                    await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
                await bot.send_message(ADMINS,
                                       f"Sizning xabaringiz barcha <b>{count_group} ta</b> Guruhga muvaffaqiyatli yuborildi.")
                await state.finish()
            except Exception as e:
                logger.exception("Xabarni yuborishda xatolik: %s", e)
                await bot.send_message(ADMINS, 'Xabarni yuborishda xatolik yuz berdi.')
                await state.finish()
    else:
        await call.message.delete()
        await state.finish()


@dp.message_handler(state=SendText.waiting_for_button_name_1, content_types=ContentType.TEXT)
async def bot_echo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["button_name_1"] = message.text

    await message.answer("Iltimos, birinchi tugma uchun URL manzilini kiriting.")
    await SendText.waiting_for_button_url_1.set()


@dp.message_handler(state=SendText.waiting_for_button_url_1, content_types=ContentType.TEXT)
async def photo_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['button_url_1'] = message.text

    await message.answer("Birinchi tugma uchun URL manzili qabul qilindi.", reply_markup=button_2)
    await SendText.next_call_2.set()


@dp.callback_query_handler(state=SendText.next_call_2, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'button_2':
        await call.message.answer('Iltimos, ikkinchi tugma nomini kiriting.')
        await SendText.waiting_for_button_name_2.set()
    elif call.data == 'send_message':
        async with state.proxy() as data:
            caption = data['caption']
            button_name_1 = data["button_name_1"]
            button_url_1 = data['button_url_1']

            button_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(button_1)

        await bot.send_message(chat_id=ADMINS, text=f"<b>{caption}</b>", reply_markup=keyboard,
                               disable_web_page_preview=True)
        await bot.send_message(chat_id=ADMINS, text="Siz yubormoqchi bo'lgan xabar xuddi shunday kurinishda boladi."
                                                    "Haqiqatdan ham shu xabarni barcha foydalanuvchilarga yuborishni istaysizmi?\n"
                                                    "✅ Tastiqlash yoki ❌ Bekor qilish tugmasini bosing.",
                               reply_markup=tasdiqlash)
        await SendText.send_all_1.set()
    else:
        await call.message.delete()
        await state.finish()


@dp.callback_query_handler(state=SendText.send_all_1, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'send_message':
        async with state.proxy() as data:
            caption = data['caption']
            button_name_1 = data["button_name_1"]
            button_url_1 = data['button_url_1']

            button_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)

            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(button_1)

            all_user_id = await User.get_all_user()
            all_group_id = await Group.get_all_group()
            count_user = 0
            count_group = 0
            try:
                for user_id in all_user_id:
                    if await bot.send_message(chat_id=user_id, text=f"<b>{caption}</b>", reply_markup=keyboard,
                                              disable_web_page_preview=True):
                        count_user += 1
                    await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
                await bot.send_message(ADMINS,
                                       f"Sizning xabaringiz barcha <b>{count_user} ta</b> foydalanuvchiga muvaffaqiyatli yuborildi.")

                for group_id in all_group_id:
                    if await bot.send_message(chat_id=group_id, text=f"<b>{caption}</b>", reply_markup=keyboard,
                                              disable_web_page_preview=True):
                        count_group += 1
                    await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
                await bot.send_message(ADMINS,
                                       f"Sizning xabaringiz barcha <b>{count_group} ta</b> Guruhga muvaffaqiyatli yuborildi.")
                await state.finish()
            except Exception as e:
                logger.exception("Xabarni yuborishda xatolik: %s", e)
                await bot.send_message(ADMINS, 'Xabarni yuborishda xatolik yuz berdi.')
                await state.finish()
    else:
        await call.message.delete()
        await state.finish()


@dp.message_handler(state=SendText.waiting_for_button_name_2, content_types=ContentType.TEXT)
async def photo_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["button_name_2"] = message.text

    await message.answer("Iltimos, ikkinchi tugma uchun URL manzilini kiriting.")
    await SendText.waiting_for_button_url_2.set()


@dp.message_handler(state=SendText.waiting_for_button_url_2, content_types=ContentType.TEXT)
async def photo_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['button_url_2'] = message.text

    await message.answer("Ikkinchi tugma uchun URL manzili qabul qilindi.", reply_markup=button_5)
    await SendText.next_call_3.set()


@dp.callback_query_handler(state=SendText.next_call_3, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'send_message':
        async with state.proxy() as data:
            caption = data['caption']
            button_name_1 = data["button_name_1"]
            button_name_2 = data["button_name_2"]
            button_url_1 = data['button_url_1']
            button_url_2 = data['button_url_2']

            button_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            button_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            keyboard = InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
            keyboard.add(button_1, button_2)
        await bot.send_message(chat_id=ADMINS, text=f"<b>{caption}</b>", reply_markup=keyboard,
                               disable_web_page_preview=True)
        await bot.send_message(chat_id=ADMINS, text="Siz yubormoqchi bo'lgan xabar xuddi shunday kurinishda boladi."
                                                    "Haqiqatdan ham shu xabarni barcha foydalanuvchilarga yuborishni istaysizmi?\n"
                                                    "✅ Tastiqlash yoki ❌ Bekor qilish tugmasini bosing.",
                               reply_markup=tasdiqlash)
        await SendText.send_all_2.set()
    else:
        await call.message.delete()
        await state.finish()


@dp.callback_query_handler(state=SendText.send_all_2, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'send_message':
        async with state.proxy() as data:
            caption = data['caption']
            button_name_1 = data["button_name_1"]
            button_name_2 = data["button_name_2"]
            button_url_1 = data['button_url_1']
            button_url_2 = data['button_url_2']

            button_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            button_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            keyboard = InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
            keyboard.add(button_1, button_2)
            all_user_id = await User.get_all_user()
            all_group_id = await Group.get_all_group()
        count_user = 0
        count_group = 0
        try:
            for user_id in all_user_id:
                if await bot.send_message(chat_id=user_id, text=f"<b>{caption}</b>", reply_markup=keyboard,
                                          disable_web_page_preview=True):
                    count_user += 1
                await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
            await bot.send_message(ADMINS,
                                   f"Sizning xabaringiz barcha <b>{count_user} ta</b> foydalanuvchiga muvaffaqiyatli yuborildi.")

            for group_id in all_group_id:
                if await bot.send_message(chat_id=group_id, text=f"<b>{caption}</b>", reply_markup=keyboard,
                                          disable_web_page_preview=True):
                    count_group += 1
                await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
            await bot.send_message(ADMINS,
                                   f"Sizning xabaringiz barcha <b>{count_group} ta</b> Guruhga muvaffaqiyatli yuborildi.")
            await state.finish()
        except Exception as e:
            logger.exception("Xabarni yuborishda xatolik: %s", e)
            await bot.send_message(ADMINS, 'Xabarni yuborishda xatolik yuz berdi.')
            await state.finish()

    else:
        await call.message.delete()
        await state.finish()


## =============================== SEND A PHOTO ===================================


@dp.callback_query_handler(text="photo", chat_id=ADMINS)
async def send_photo_to_all(call: types.CallbackQuery):
    chat_id = call.from_user.id
    callback_id = call.message.message_id
    await bot.edit_message_text(chat_id=chat_id, message_id=callback_id, text="🖼 SEND A PHOTO")
    await SendPhoto.photo.set()


@dp.message_handler(state=SendPhoto.photo, content_types=ContentType.PHOTO)
async def send_photo_to_all(message: types.Message, state: FSMContext):
    # Save the file id to the user's session
    async with state.proxy() as data:
        data["photo_file"] = message.photo[-1].file_id

        # Ask the user to provide information for the video
    await message.answer("Iltimos, photo uchun ma'lumotlarni kiriting.")
    await SendPhoto.waiting_for_caption.set()


@dp.message_handler(state=SendPhoto.waiting_for_caption, content_types=ContentType.TEXT)
async def video_caption(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['caption'] = await replace_text_with_links(message.text)
    await message.answer("Xabar uchun tugma yaratishni hohlaysizmi?", reply_markup=add_btn)
    await SendPhoto.waiting_for_new_btn.set()


@dp.callback_query_handler(state=SendPhoto.waiting_for_new_btn, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'add_btn':
        await call.message.answer('Iltimos, birinchi tugma nomini kiriting.')
        await SendPhoto.waiting_for_button_name_1.set()
    elif call.data == 'send_message':
        async with state.proxy() as data:
            photo_file = data["photo_file"]
            caption = data['caption']

        await bot.send_photo(chat_id=ADMINS, photo=photo_file, caption=f"<b>{caption}</b>")
        await bot.send_message(chat_id=ADMINS, text="Siz yubormoqchi bo'lgan xabar xuddi shunday kurinishda boladi."
                                                    "Haqiqatdan ham shu xabarni barcha foydalanuvchilarga yuborishni istaysizmi?\n"
                                                    "✅ Tastiqlash yoki ❌ Bekor qilish tugmasini bosing.",
                               reply_markup=tasdiqlash)
        await SendPhoto.waiting_for_is_not_btn.set()
    else:
        await call.message.delete()
        await state.finish()


@dp.callback_query_handler(state=SendPhoto.waiting_for_is_not_btn, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'send_message':
        async with state.proxy() as data:
            photo_file = data["photo_file"]
            caption = data['caption']
            all_user_id = await User.get_all_user()
            all_group_id = await Group.get_all_group()
            count_user = 0
            count_group = 0
            try:
                for user_id in all_user_id:
                    if await bot.send_photo(chat_id=user_id, photo=photo_file, caption=f"<b>{caption}</b>"):
                        count_user += 1
                    await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
                await bot.send_message(ADMINS,
                                       f"Sizning xabaringiz barcha  <b>{count_user} ta</b>  Foydalanuvchiga muvaffaqiyatli yuborildi.")
                for group_id in all_group_id:
                    if await bot.send_photo(chat_id=group_id, photo=photo_file, caption=f"<b>{caption}</b>"):
                        count_group += 1
                    await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
                await bot.send_message(ADMINS,
                                       f"Sizning xabaringiz barcha  <b>{count_user} ta</b>  Guruhga muvaffaqiyatli yuborildi.")
                await state.finish()
            except Exception as e:
                logger.exception("Xabarni yuborishda xatolik: %s", e)
                await bot.send_message(ADMINS, 'Xabarni yuborishda xatolik yuz berdi.')
                await state.finish()
    else:
        await call.message.delete()
        await state.finish()


@dp.message_handler(state=SendPhoto.waiting_for_button_name_1, content_types=ContentType.TEXT)
async def photo_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["button_name_1"] = message.text

    await message.answer("Iltimos, birinchi tugma uchun URL manzilini kiriting.")
    await SendPhoto.waiting_for_button_url_1.set()


@dp.message_handler(state=SendPhoto.waiting_for_button_url_1, content_types=ContentType.TEXT)
async def photo_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['button_url_1'] = message.text

    await message.answer("Birinchi tugma uchun URL manzili qabul qilindi.", reply_markup=button_2)
    await SendPhoto.next_call_2.set()


@dp.callback_query_handler(state=SendPhoto.next_call_2, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'button_2':
        await call.message.answer('Iltimos, ikkinchi tugma nomini kiriting.')
        await SendPhoto.waiting_for_button_name_2.set()
    elif call.data == 'send_message':
        async with state.proxy() as data:
            photo_file = data["photo_file"]
            caption = data['caption']
            button_name_1 = data["button_name_1"]
            button_url_1 = data['button_url_1']

            button_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(button_1)

        await bot.send_photo(chat_id=ADMINS, photo=photo_file, caption=caption, reply_markup=keyboard)
        await bot.send_message(chat_id=ADMINS, text="Siz yubormoqchi bo'lgan xabar xuddi shunday kurinishda boladi."
                                                    "Haqiqatdan ham shu xabarni barcha foydalanuvchilarga yuborishni istaysizmi?\n"
                                                    "✅ Tastiqlash yoki ❌ Bekor qilish tugmasini bosing.",
                               reply_markup=tasdiqlash)
        await SendPhoto.send_all_1.set()
    else:
        await call.message.delete()
        await state.finish()


@dp.callback_query_handler(state=SendPhoto.send_all_1, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'send_message':
        async with state.proxy() as data:
            photo_file = data["photo_file"]
            caption = data['caption']
            button_name_1 = data["button_name_1"]
            button_url_1 = data['button_url_1']
            button_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)

            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(button_1)

            all_user_id = await User.get_all_user()
            all_group_id = await Group.get_all_group()
            count_user = 0
            count_group = 0
            try:
                for user_id in all_user_id:
                    if await bot.send_photo(chat_id=user_id, photo=photo_file, caption=caption, reply_markup=keyboard):
                        count_user += 1
                    await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
                await bot.send_message(ADMINS,
                                       f"Sizning xabaringiz barcha  <b>{count_user} ta</b>  foydalanuvchiga muvaffaqiyatli yuborildi.")
                for group_id in all_group_id:
                    if await bot.send_photo(chat_id=group_id, photo=photo_file, caption=caption, reply_markup=keyboard):
                        count_group += 1
                    await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
                await bot.send_message(ADMINS,
                                       f"Sizning xabaringiz barcha  <b>{count_group} ta</b>  Guruhga muvaffaqiyatli yuborildi.")
                await state.finish()
            except Exception as e:
                logger.exception("Xabarni yuborishda xatolik: %s", e)
                await bot.send_message(ADMINS, 'Xabarni yuborishda xatolik yuz berdi.')
                await state.finish()
    else:
        await call.message.delete()
        await state.finish()


@dp.message_handler(state=SendPhoto.waiting_for_button_name_2, content_types=ContentType.TEXT)
async def photo_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["button_name_2"] = message.text

    await message.answer("Iltimos, ikkinchi tugma uchun URL manzilini kiriting.")
    await SendPhoto.waiting_for_button_url_2.set()


@dp.message_handler(state=SendPhoto.waiting_for_button_url_2, content_types=ContentType.TEXT)
async def photo_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['button_url_2'] = message.text

    await message.answer("Ikkinchi tugma uchun URL manzili qabul qilindi.", reply_markup=button_3)
    await SendPhoto.next_call_3.set()


@dp.callback_query_handler(state=SendPhoto.next_call_3, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'button_3':
        await call.message.answer('Iltimos, uchunchi tugma nomini kiriting.')
        await SendPhoto.waiting_for_button_name_3.set()
    elif call.data == 'send_message':
        async with state.proxy() as data:
            photo_file = data["photo_file"]
            caption = data['caption']
            button_name_1 = data["button_name_1"]
            button_name_2 = data["button_name_2"]
            button_url_1 = data['button_url_1']
            button_url_2 = data['button_url_2']

            button_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            button_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            keyboard = InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
            keyboard.add(button_1, button_2)

        await bot.send_photo(chat_id=ADMINS, photo=photo_file, caption=caption, reply_markup=keyboard)
        await bot.send_message(chat_id=ADMINS, text="Siz yubormoqchi bo'lgan xabar xuddi shunday kurinishda boladi."
                                                    "Haqiqatdan ham shu xabarni barcha foydalanuvchilarga yuborishni istaysizmi?\n"
                                                    "✅ Tastiqlash yoki ❌ Bekor qilish tugmasini bosing.",
                               reply_markup=tasdiqlash)
        await SendPhoto.send_all_2.set()
    else:
        await call.message.delete()
        await state.finish()


@dp.callback_query_handler(state=SendPhoto.send_all_2, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'send_message':
        async with state.proxy() as data:
            photo_file = data["photo_file"]
            caption = data['caption']
            button_name_1 = data["button_name_1"]
            button_name_2 = data["button_name_2"]
            button_url_1 = data['button_url_1']
            button_url_2 = data['button_url_2']

            button_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            button_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            keyboard = InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
            keyboard.add(button_1, button_2)

            all_user_id = await User.get_all_user()
            all_group_id = await Group.get_all_group()
        count_user = 0
        count_group = 0
        try:
            for user_id in all_user_id:
                if await bot.send_photo(chat_id=user_id, photo=photo_file, caption=caption, reply_markup=keyboard):
                    count_user += 1
                await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
            await bot.send_message(ADMINS,
                                   f"Sizning xabaringiz barcha  <b>{count_user} ta</b>  foydalanuvchiga muvaffaqiyatli yuborildi.")

            for group_id in all_group_id:
                if await bot.send_photo(chat_id=group_id, photo=photo_file, caption=caption, reply_markup=keyboard):
                    count_group += 1
                await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
            await bot.send_message(ADMINS,
                                   f"Sizning xabaringiz barcha  <b>{count_group} ta</b>  Guruhga muvaffaqiyatli yuborildi.")
            await state.finish()
        except Exception as e:
            logger.exception("Xabarni yuborishda xatolik: %s", e)
            await bot.send_message(ADMINS, 'Xabarni yuborishda xatolik yuz berdi.')
            await state.finish()

    else:
        await call.message.delete()
        await state.finish()


@dp.message_handler(state=SendPhoto.waiting_for_button_name_3, content_types=ContentType.TEXT)
async def photo_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["button_name_3"] = message.text

    await message.answer("Iltimos, uchunchi tugma uchun URL manzilini kiriting.")
    await SendPhoto.waiting_for_button_url_3.set()


@dp.message_handler(state=SendPhoto.waiting_for_button_url_3, content_types=ContentType.TEXT)
async def photo_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['button_url_3'] = message.text

    await message.answer("Uchunchi tugma uchun URL manzili qabul qilindi.", reply_markup=button_4)
    await SendPhoto.next_call_4.set()


@dp.callback_query_handler(state=SendPhoto.next_call_4, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'button_4':
        await call.message.answer("Iltimos, to'rtinchi tugma nomini kiriting.")
        await SendPhoto.waiting_for_button_name_4.set()
    elif call.data == 'send_message':
        async with state.proxy() as data:
            photo_file = data["photo_file"]
            caption = data['caption']
            button_name_1 = data["button_name_1"]
            button_name_2 = data["button_name_2"]
            button_name_3 = data["button_name_3"]
            button_url_1 = data['button_url_1']
            button_url_2 = data['button_url_2']
            button_url_3 = data['button_url_3']

            btn_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            btn_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            btn_3 = InlineKeyboardButton(text=button_name_3, url=button_url_3)
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(btn_1, btn_2, btn_3)

            await bot.send_photo(chat_id=ADMINS, photo=photo_file, caption=caption, reply_markup=keyboard)
            await bot.send_message(chat_id=ADMINS, text="Siz yubormoqchi bo'lgan xabar xuddi shunday kurinishda boladi."
                                                        "Haqiqatdan ham shu xabarni barcha foydalanuvchilarga yuborishni istaysizmi?\n"
                                                        "✅ Tastiqlash yoki ❌ Bekor qilish tugmasini bosing.",
                                   reply_markup=tasdiqlash)
            await SendPhoto.send_all_3.set()
    else:
        await call.message.delete()
        await state.finish()


@dp.callback_query_handler(state=SendPhoto.send_all_3, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'send_message':
        async with state.proxy() as data:
            photo_file = data["photo_file"]
            caption = data['caption']
            button_name_1 = data["button_name_1"]
            button_name_2 = data["button_name_2"]
            button_name_3 = data["button_name_3"]
            button_url_1 = data['button_url_1']
            button_url_2 = data['button_url_2']
            button_url_3 = data['button_url_3']

            btn_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            btn_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            btn_3 = InlineKeyboardButton(text=button_name_3, url=button_url_3)
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(btn_1, btn_2, btn_3)

        all_user_id = await User.get_all_user()
        all_group_id = await Group.get_all_group()
        count_user = 0
        count_group = 0
        try:
            for user_id in all_user_id:
                if await bot.send_photo(chat_id=user_id, photo=photo_file, caption=caption, reply_markup=keyboard):
                    count_user += 1
                await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
            await bot.send_message(ADMINS,
                                   f"Sizning xabaringiz barcha <b>{count_user} ta</b> foydalanuvchiga muvaffaqiyatli yuborildi.")

            for group_id in all_group_id:
                if await bot.send_photo(chat_id=group_id, photo=photo_file, caption=caption, reply_markup=keyboard):
                    count_group += 1
                await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
            await bot.send_message(ADMINS,
                                   f"Sizning xabaringiz barcha <b>{count_group} ta</b> Guruhga muvaffaqiyatli yuborildi.")
            await state.finish()
        except Exception as e:
            logger.exception("Xabarni yuborishda xatolik: %s", e)
            await bot.send_message(ADMINS, 'Xabarni yuborishda xatolik yuz berdi.')
            await state.finish()

    else:
        await call.message.delete()
        await state.finish()


@dp.message_handler(state=SendPhoto.waiting_for_button_name_4, content_types=ContentType.TEXT)
async def photo_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["button_name_4"] = message.text

    await message.answer("Iltimos, uchunchi tugma uchun URL manzilini kiriting.")
    await SendPhoto.waiting_for_button_url_4.set()


@dp.message_handler(state=SendPhoto.waiting_for_button_url_4, content_types=ContentType.TEXT)
async def photo_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['button_url_4'] = message.text

    await message.answer("To'rtinchi tugma uchun URL manzili qabul qilindi.", reply_markup=button_5)
    await SendPhoto.next_call_5.set()


@dp.callback_query_handler(state=SendPhoto.next_call_5, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'send_message':
        async with state.proxy() as data:
            photo_file = data["photo_file"]
            caption = data['caption']
            button_name_1 = data["button_name_1"]
            button_name_2 = data["button_name_2"]
            button_name_3 = data["button_name_3"]
            button_name_4 = data["button_name_4"]
            button_url_1 = data['button_url_1']
            button_url_2 = data['button_url_2']
            button_url_3 = data['button_url_3']
            button_url_4 = data['button_url_4']

            btn_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            btn_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            btn_3 = InlineKeyboardButton(text=button_name_3, url=button_url_3)
            btn_4 = InlineKeyboardButton(text=button_name_4, url=button_url_4)
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(btn_1, btn_2, btn_3, btn_4)

            await bot.send_photo(chat_id=ADMINS, photo=photo_file, caption=caption, reply_markup=keyboard)
            await bot.send_message(chat_id=ADMINS, text="Siz yubormoqchi bo'lgan xabar xuddi shunday kurinishda boladi."
                                                        "Haqiqatdan ham shu xabarni barcha foydalanuvchilarga yuborishni istaysizmi?\n"
                                                        "✅ Tastiqlash yoki ❌ Bekor qilish tugmasini bosing.",
                                   reply_markup=tasdiqlash)
            await SendPhoto.send_all_4.set()
    else:
        await call.message.delete()
        await state.finish()


@dp.callback_query_handler(state=SendPhoto.send_all_4, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'send_message':
        async with state.proxy() as data:
            photo_file = data["photo_file"]
            caption = data['caption']
            button_name_1 = data["button_name_1"]
            button_name_2 = data["button_name_2"]
            button_name_3 = data["button_name_3"]
            button_name_4 = data["button_name_4"]
            button_url_1 = data['button_url_1']
            button_url_2 = data['button_url_2']
            button_url_3 = data['button_url_3']
            button_url_4 = data['button_url_4']

            btn_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            btn_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            btn_3 = InlineKeyboardButton(text=button_name_3, url=button_url_3)
            btn_4 = InlineKeyboardButton(text=button_name_4, url=button_url_4)
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(btn_1, btn_2, btn_3, btn_4)

            all_user_id = await User.get_all_user()
            all_group_id = await Group.get_all_group()
        count_user = 0
        count_group = 0
        try:
            for user_id in all_user_id:
                if await bot.send_photo(chat_id=user_id, photo=photo_file, caption=caption, reply_markup=keyboard):
                    count_user += 1
                await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
            await bot.send_message(ADMINS,
                                   f"Sizning xabaringiz barcha <b>{count_user} ta</b> foydalanuvchiga muvaffaqiyatli yuborildi.")

            for group_id in all_group_id:
                if await bot.send_photo(chat_id=group_id, photo=photo_file, caption=caption, reply_markup=keyboard):
                    count_group += 1
                await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
            await bot.send_message(ADMINS,
                                   f"Sizning xabaringiz barcha <b>{count_group} ta</b> Guruhga muvaffaqiyatli yuborildi.")
            await state.finish()
        except Exception as e:
            logger.exception("Xabarni yuborishda xatolik: %s", e)
            await bot.send_message(ADMINS, 'Xabarni yuborishda xatolik yuz berdi.')
            await state.finish()
    else:
        await call.message.delete()
        await state.finish()


## =============================== SEND A VIDEO ===================================


@dp.callback_query_handler(text="video", chat_id=ADMINS)
async def send_video_to_all(call: types.CallbackQuery):
    chat_id = call.from_user.id
    callback_id = call.message.message_id
    await bot.edit_message_text(chat_id=chat_id, message_id=callback_id, text="🎥 SEND A VIDEO")
    await SendVideo.video.set()


@dp.message_handler(state=SendVideo.video, content_types=ContentType.VIDEO)
async def send_video_to_all(message: types.Message, state: FSMContext):
    # Save the file id to the user's session
    async with state.proxy() as data:
        data["video_file"] = message.video.file_id

        # Ask the user to provide information for the video
    await message.answer("Iltimos, video uchun ma'lumotlarni kiriting.")
    await SendVideo.waiting_for_caption.set()


@dp.message_handler(state=SendVideo.waiting_for_caption, content_types=ContentType.TEXT)
async def video_caption(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['caption'] = await replace_text_with_links(message.text)

    await message.answer("Iltimos, birinchi tugma nomini kiriting.")
    await SendVideo.waiting_for_new_btn.set()


@dp.callback_query_handler(state=SendVideo.waiting_for_new_btn, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'add_btn':
        await call.message.answer('Iltimos, birinchi tugma nomini kiriting.')
        await SendVideo.waiting_for_button_name_1.set()
    elif call.data == 'send_message':
        async with state.proxy() as data:
            video_file = data["video_file"]
            caption = data['caption']

        await bot.send_video(chat_id=ADMINS, video=video_file, caption=f"<b>{caption}</b>")
        await bot.send_message(chat_id=ADMINS, text="Siz yubormoqchi bo'lgan xabar xuddi shunday kurinishda boladi."
                                                    "Haqiqatdan ham shu xabarni barcha foydalanuvchilarga yuborishni istaysizmi?\n"
                                                    "✅ Tastiqlash yoki ❌ Bekor qilish tugmasini bosing.",
                               reply_markup=tasdiqlash)
        await SendPhoto.waiting_for_is_not_btn.set()
    else:
        await call.message.delete()
        await state.finish()


@dp.callback_query_handler(state=SendPhoto.waiting_for_is_not_btn, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'send_message':
        async with state.proxy() as data:
            video_file = data["video_file"]
            caption = data['caption']
            all_user_id = await User.get_all_user()
            all_group_id = await Group.get_all_group()
            count_user = 0
            count_group = 0
            try:
                for user_id in all_user_id:
                    if await bot.send_video(chat_id=user_id, video=video_file, caption=f"<b>{caption}</b>"):
                        count_user += 1
                    await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
                await bot.send_message(ADMINS,
                                       f"Sizning xabaringiz barcha <b>{count_user} ta</b> foydalanuvchiga muvaffaqiyatli yuborildi.")

                for group_id in all_group_id:
                    if await bot.send_video(chat_id=group_id, video=video_file, caption=f"<b>{caption}</b>"):
                        count_group += 1
                    await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
                await bot.send_message(ADMINS,
                                       f"Sizning xabaringiz barcha <b>{count_group} ta</b> Guruhga muvaffaqiyatli yuborildi..")
                await state.finish()
            except Exception as e:
                logger.exception("Xabarni yuborishda xatolik: %s", e)
                await bot.send_message(ADMINS, 'Xabarni yuborishda xatolik yuz berdi.')
                await state.finish()
    else:
        await call.message.delete()
        await state.finish()


@dp.message_handler(state=SendVideo.waiting_for_button_name_1, content_types=ContentType.TEXT)
async def video_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["button_name_1"] = message.text
    await message.answer("Iltimos, birinchi tugma uchun URL manzilini kiriting.")
    await SendVideo.waiting_for_button_url_1.set()


@dp.message_handler(state=SendVideo.waiting_for_button_url_1, content_types=ContentType.TEXT)
async def video_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['button_url_1'] = message.text
    await message.answer("Birinchi tugma uchun URL manzili qabul qilindi.", reply_markup=button_2)
    await SendVideo.next_call_2.set()


@dp.callback_query_handler(state=SendVideo.next_call_2, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'button_2':
        await call.message.answer('Iltimos, ikkinchi tugma nomini kiriting.')
        await SendVideo.waiting_for_button_name_2.set()
    elif call.data == 'send_message':
        async with state.proxy() as data:
            video_file = data["video_file"]
            caption = data['caption']
            button_name_1 = data["button_name_1"]
            button_url_1 = data['button_url_1']

            button_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(button_1)

        await bot.send_video(chat_id=ADMINS, video=video_file, caption=caption, reply_markup=keyboard)
        await bot.send_message(chat_id=ADMINS, text="Siz yubormoqchi bo'lgan xabar xuddi shunday kurinishda boladi."
                                                    "Haqiqatdan ham shu xabarni barcha foydalanuvchilarga yuborishni istaysizmi?\n"
                                                    "✅ Tastiqlash yoki ❌ Bekor qilish tugmasini bosing.",
                               reply_markup=tasdiqlash)
        await SendVideo.send_all_1.set()
    else:
        await call.message.delete()
        await state.finish()


@dp.callback_query_handler(state=SendVideo.send_all_1, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'send_message':
        async with state.proxy() as data:
            video_file = data["video_file"]
            caption = data['caption']
            button_name_1 = data["button_name_1"]
            button_url_1 = data['button_url_1']

            button_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)

            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(button_1)

            all_user_id = await User.get_all_user()
            all_group_id = await Group.get_all_group()
            count_user = 0
            count_group = 0
            try:
                for user_id in all_user_id:
                    if await bot.send_video(chat_id=user_id, video=video_file, caption=caption, reply_markup=keyboard):
                        count_user += 1
                    await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
                await bot.send_message(ADMINS,
                                       f"Sizning xabaringiz barcha <b>{count_user} ta</b> foydalanuvchiga muvaffaqiyatli yuborildi.")

                for group_id in all_group_id:
                    if await bot.send_video(chat_id=group_id, video=video_file, caption=caption, reply_markup=keyboard):
                        count_group += 1
                    await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
                await bot.send_message(ADMINS,
                                       f"Sizning xabaringiz barcha <b>{count_group} ta</b> Guruhga muvaffaqiyatli yuborildi.")
                await state.finish()
            except Exception as e:
                logger.exception("Xabarni yuborishda xatolik: %s", e)
                await bot.send_message(ADMINS, 'Xabarni yuborishda xatolik yuz berdi.')
                await state.finish()
    else:
        await call.message.delete()
        await state.finish()


@dp.message_handler(state=SendVideo.waiting_for_button_name_2, content_types=ContentType.TEXT)
async def video_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["button_name_2"] = message.text

    await message.answer("Iltimos, ikkinchi tugma uchun URL manzilini kiriting.")
    await SendVideo.waiting_for_button_url_2.set()


@dp.message_handler(state=SendVideo.waiting_for_button_url_2, content_types=ContentType.TEXT)
async def video_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['button_url_2'] = message.text

    await message.answer("Ikkinchi tugma uchun URL manzili qabul qilindi.", reply_markup=button_3)
    await SendVideo.next_call_3.set()


@dp.callback_query_handler(state=SendVideo.next_call_3, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'button_3':
        await call.message.answer('Iltimos, uchunchi tugma nomini kiriting.')
        await SendVideo.waiting_for_button_name_3.set()
    elif call.data == 'send_message':
        async with state.proxy() as data:
            video_file = data["video_file"]
            caption = data['caption']
            button_name_1 = data["button_name_1"]
            button_name_2 = data["button_name_2"]
            button_url_1 = data['button_url_1']
            button_url_2 = data['button_url_2']
            button_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            button_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            keyboard = InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
            keyboard.add(button_1, button_2)
        await bot.send_video(chat_id=ADMINS, video=video_file, caption=caption, reply_markup=keyboard)
        await bot.send_message(chat_id=ADMINS, text="Siz yubormoqchi bo'lgan xabar xuddi shunday kurinishda boladi."
                                                    "Haqiqatdan ham shu xabarni barcha foydalanuvchilarga yuborishni istaysizmi?\n"
                                                    "✅ Tastiqlash yoki ❌ Bekor qilish tugmasini bosing.",
                               reply_markup=tasdiqlash)
        await SendVideo.send_all_2.set()
    else:
        await call.message.delete()
        await state.finish()


@dp.callback_query_handler(state=SendVideo.send_all_2, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'send_message':
        async with state.proxy() as data:
            video_file = data["video_file"]
            caption = data['caption']
            button_name_1 = data["button_name_1"]
            button_name_2 = data["button_name_2"]
            button_url_1 = data['button_url_1']
            button_url_2 = data['button_url_2']
            button_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            button_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            keyboard = InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
            keyboard.add(button_1, button_2)
            all_user_id = await User.get_all_user()
            all_group_id = await Group.get_all_group()
        count_user = 0
        count_group = 0
        try:
            for user_id in all_user_id:
                if await bot.send_video(chat_id=user_id, video=video_file, caption=caption, reply_markup=keyboard):
                    count_user += 1
                await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
            await bot.send_message(ADMINS,
                                   f"Sizning xabaringiz barcha <b>{count_user} ta</b> foydalanuvchiga muvaffaqiyatli yuborildi.")

            for group_id in all_group_id:
                if await bot.send_video(chat_id=group_id, video=video_file, caption=caption, reply_markup=keyboard):
                    count_group += 1
                await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
            await bot.send_message(ADMINS,
                                   f"Sizning xabaringiz barcha <b>{count_group} ta</b> Guruhga muvaffaqiyatli yuborildi.")
            await state.finish()
        except Exception as e:
            logger.exception("Xabarni yuborishda xatolik: %s", e)
            await bot.send_message(ADMINS, 'Xabarni yuborishda xatolik yuz berdi.')
            await state.finish()
    else:
        await call.message.delete()
        await state.finish()


@dp.message_handler(state=SendVideo.waiting_for_button_name_3, content_types=ContentType.TEXT)
async def video_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["button_name_3"] = message.text

    await message.answer("Iltimos, uchunchi tugma uchun URL manzilini kiriting.")
    await SendVideo.waiting_for_button_url_3.set()


@dp.message_handler(state=SendVideo.waiting_for_button_url_3, content_types=ContentType.TEXT)
async def video_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['button_url_3'] = message.text
    await message.answer("Uchunchi tugma uchun URL manzili qabul qilindi.", reply_markup=button_4)
    await SendVideo.next_call_4.set()


@dp.callback_query_handler(state=SendVideo.next_call_4, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'button_4':
        await call.message.answer("Iltimos, to'rtinchi tugma nomini kiriting.")
        await SendVideo.waiting_for_button_name_4.set()
    elif call.data == 'send_message':
        async with state.proxy() as data:
            video_file = data["video_file"]
            caption = data['caption']
            button_name_1 = data["button_name_1"]
            button_name_2 = data["button_name_2"]
            button_name_3 = data["button_name_3"]
            button_url_1 = data['button_url_1']
            button_url_2 = data['button_url_2']
            button_url_3 = data['button_url_3']
            btn_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            btn_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            btn_3 = InlineKeyboardButton(text=button_name_3, url=button_url_3)
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(btn_1, btn_2, btn_3)
            await bot.send_video(chat_id=ADMINS, video=video_file, caption=caption, reply_markup=keyboard)
            await bot.send_message(chat_id=ADMINS, text="Siz yubormoqchi bo'lgan xabar xuddi shunday kurinishda boladi."
                                                        "Haqiqatdan ham shu xabarni barcha foydalanuvchilarga yuborishni istaysizmi?\n"
                                                        "✅ Tastiqlash yoki ❌ Bekor qilish tugmasini bosing.",
                                   reply_markup=tasdiqlash)
            await SendVideo.send_all_3.set()
    else:
        await call.message.answer('❌Xabar yuborish bekor qilindi.')
        return await state.finish()


@dp.callback_query_handler(state=SendVideo.send_all_3, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'send_message':
        async with state.proxy() as data:
            video_file = data["video_file"]
            caption = data['caption']
            button_name_1 = data["button_name_1"]
            button_name_2 = data["button_name_2"]
            button_name_3 = data["button_name_3"]
            button_url_1 = data['button_url_1']
            button_url_2 = data['button_url_2']
            button_url_3 = data['button_url_3']
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True).add(
                InlineKeyboardButton(text=button_name_1, url=button_url_1),
                InlineKeyboardButton(text=button_name_2, url=button_url_2),
                InlineKeyboardButton(text=button_name_3, url=button_url_3)
            )
            all_user_id = await User.get_all_user()
            all_group_id = await Group.get_all_group()
        count_user = 0
        count_group = 0
        try:
            for user_id in all_user_id:
                if await bot.send_video(chat_id=user_id, video=video_file, caption=caption, reply_markup=keyboard):
                    count_user += 1
                await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
            await bot.send_message(ADMINS,
                                   f"Sizning xabaringiz barcha <b>{count_user} ta</b> foydalanuvchiga muvaffaqiyatli yuborildi.")
            for group_id in all_group_id:
                if await bot.send_video(chat_id=group_id, video=video_file, caption=caption, reply_markup=keyboard):
                    count_group += 1
                await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
            await bot.send_message(ADMINS,
                                   f"Sizning xabaringiz barcha <b>{count_group} ta</b> Guruhga muvaffaqiyatli yuborildi.")
            await state.finish()
        except Exception as e:
            logger.exception("Xabarni yuborishda xatolik: %s", e)
            await bot.send_message(ADMINS, 'Xabarni yuborishda xatolik yuz berdi.')
            await state.finish()
    else:
        await call.message.delete()
        await state.finish()


@dp.message_handler(state=SendVideo.waiting_for_button_name_4, content_types=ContentType.TEXT)
async def video_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["button_name_4"] = message.text

    await message.answer("Iltimos, uchunchi tugma uchun URL manzilini kiriting.")
    await SendVideo.waiting_for_button_url_4.set()


@dp.message_handler(state=SendVideo.waiting_for_button_url_4, content_types=ContentType.TEXT)
async def video_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['button_url_4'] = message.text

    await message.answer("To'rtinchi tugma uchun URL manzili qabul qilindi.", reply_markup=button_5)
    await SendVideo.next_call_5.set()


@dp.callback_query_handler(state=SendVideo.next_call_5, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'send_message':
        async with state.proxy() as data:
            video_file = data["video_file"]
            caption = data['caption']
            button_name_1 = data["button_name_1"]
            button_name_2 = data["button_name_2"]
            button_name_3 = data["button_name_3"]
            button_name_4 = data["button_name_4"]
            button_url_1 = data['button_url_1']
            button_url_2 = data['button_url_2']
            button_url_3 = data['button_url_3']
            button_url_4 = data['button_url_4']
            btn_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            btn_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            btn_3 = InlineKeyboardButton(text=button_name_3, url=button_url_3)
            btn_4 = InlineKeyboardButton(text=button_name_4, url=button_url_4)
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(btn_1, btn_2, btn_3, btn_4)
            await bot.send_video(chat_id=ADMINS, video=video_file, caption=caption, reply_markup=keyboard)
            await bot.send_message(chat_id=ADMINS, text="Siz yubormoqchi bo'lgan xabar xuddi shunday kurinishda boladi."
                                                        "Haqiqatdan ham shu xabarni barcha foydalanuvchilarga yuborishni istaysizmi?\n"
                                                        "✅ Tastiqlash yoki ❌ Bekor qilish tugmasini bosing.",
                                   reply_markup=tasdiqlash)
            await SendVideo.send_all_4.set()
    else:
        await call.message.delete()
        await state.finish()


@dp.callback_query_handler(state=SendVideo.send_all_4, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'send_message':
        async with state.proxy() as data:
            video_file = data["video_file"]
            caption = data['caption']
            button_name_1 = data["button_name_1"]
            button_name_2 = data["button_name_2"]
            button_name_3 = data["button_name_3"]
            button_name_4 = data["button_name_4"]
            button_url_1 = data['button_url_1']
            button_url_2 = data['button_url_2']
            button_url_3 = data['button_url_3']
            button_url_4 = data['button_url_4']

            btn_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            btn_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            btn_3 = InlineKeyboardButton(text=button_name_3, url=button_url_3)
            btn_4 = InlineKeyboardButton(text=button_name_4, url=button_url_4)
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(btn_1, btn_2, btn_3, btn_4)

            all_user_id = await User.get_all_user()
            all_group_id = await Group.get_all_group()
        count_user = 0
        count_group = 0
        try:
            for user_id in all_user_id:
                if await bot.send_video(chat_id=user_id, video=video_file, caption=caption, reply_markup=keyboard):
                    count_user += 1
                await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
            await bot.send_message(ADMINS,
                                   f"Sizning xabaringiz barcha <b>{count_user} ta</b> foydalanuvchiga muvaffaqiyatli yuborildi.")

            for group_id in all_group_id:
                if await bot.send_video(chat_id=group_id, video=video_file, caption=caption, reply_markup=keyboard):
                    count_group += 1
                await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
            await bot.send_message(ADMINS,
                                   f"Sizning xabaringiz barcha <b>{count_group} ta</b> Guruhga muvaffaqiyatli yuborildi.")
            await state.finish()
        except Exception as e:
            logger.exception("Xabarni yuborishda xatolik: %s", e)
            await bot.send_message(ADMINS, 'Xabarni yuborishda xatolik yuz berdi.')
            await state.finish()

    else:
        await call.message.delete()
        await state.finish()
