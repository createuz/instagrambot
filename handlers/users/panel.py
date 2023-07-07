from databasedb.models import *
from keyboards import *
from states import *
from loader import *


@dp.message_handler(commands=['break'], chat_id=ADMINS)
async def add_admin_handler(message: types.Message, state: FSMContext):
    try:
        await message.answer("⚙ Xabar yuborish toxtatildi")
        await state.finish()
    except Exception as e:
        await state.finish()
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")


def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


# @dp.message_handler(commands=['cleardb'], chat_id=ADMINS)
# async def clear_db_handler(message: types.Message):
#     try:
#         user_input = message.text.split(' ')[1] if len(message.text.split(' ')) > 1 else None
#         if not user_input:
#             await message.answer("❌ Parolni kiriting: /cleardb <parol>")
#             return
#         if check_password(user_input, ADMIN_PASSWORD_HASH):
#             async with engine.begin() as conn:
#                 await conn.execute(InstagramMediaDB.__table__.delete())
#             await engine.dispose()
#             await message.answer("✅ Ma'lumotlar tozalandi.")
#         else:
#             await message.answer("❌ Xato parol! To'g'ri parolni kiriting.")
#     except Exception as e:
#         await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")


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


@dp.message_handler(commands=['add_admin'], chat_id=ADMINS)
async def add_admin_handler(message: types.Message):
    await message.answer("Yangi adminning chat ID sini kiriting:")
    await AddAdmin.waiting_for_chat_id.set()


@dp.message_handler(state=AddAdmin.waiting_for_chat_id, content_types=ContentType.TEXT)
async def add_admin_save_handler(message: types.Message, state: FSMContext):
    chat_id = message.text
    try:
        user = await bot.get_chat(chat_id)
    except:
        await message.answer(f"Chat ID {chat_id} haqiqiy bir foydalanuvchi emas.")
        await state.finish()
        return
    # Add admin to databasedb
    try:
        await Admin.create_admin(chat_id, user.username, user.first_name)
        await message.answer(f"{user.full_name} adminlar ro'yxatiga qo'shildi.")
        await state.finish()
    except:
        await message.answer(f"Chat ID: {chat_id} haqiqiy bir foydalanuvchi emas.")
        await state.finish()
        return


@dp.message_handler(commands=['admin'], chat_id=ADMINS)
async def bot_echo(message: types.Message):
    await message.answer("⚙ SIZ ADMIN PANELDASIZ", reply_markup=menu_kb)


@dp.callback_query_handler(text="stat")
async def Admin_send(call: types.CallbackQuery):
    statiska_user = await User.count_users()
    statiska_group = await Group.count_users()
    await call.message.answer(f"Bot User foidalanuvchilari <b>{statiska_user} nafar</b>")
    await call.message.answer(f"Bot Guruhlari soni <b>{statiska_group} nafar</b>")


@dp.callback_query_handler(text="send", chat_id=ADMINS)
async def admin_send_message(call: types.CallbackQuery):
    chat_id = call.from_user.id
    callback_id = call.message.message_id
    await bot.edit_message_text(chat_id=chat_id, message_id=callback_id, text="Xabar turini Tanlang 👇🏻",
                                reply_markup=admin_kb)


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
        await call.message.answer('Xabar yuborish bekor qilindi.')
        await state.finish()
        return


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
        await call.message.answer('❌Xabar yuborish bekor qilindi.')
        await state.finish()
        return


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

            # Create the first button
            button_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            # Create the inline keyboard markup with both buttons
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(button_1)

            # Create the message with the photo, caption, and keyboard
        await bot.send_message(chat_id=ADMINS, text=f"<b>{caption}</b>", reply_markup=keyboard,
                               disable_web_page_preview=True)
        await bot.send_message(chat_id=ADMINS, text="Siz yubormoqchi bo'lgan xabar xuddi shunday kurinishda boladi."
                                                    "Haqiqatdan ham shu xabarni barcha foydalanuvchilarga yuborishni istaysizmi?\n"
                                                    "✅ Tastiqlash yoki ❌ Bekor qilish tugmasini bosing.",
                               reply_markup=tasdiqlash)
        await SendText.send_all_1.set()
    else:
        await call.message.answer('Xabar yuborish bekor qilindi.')
        await state.finish()
        return


@dp.callback_query_handler(state=SendText.send_all_1, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'send_message':
        async with state.proxy() as data:
            caption = data['caption']
            button_name_1 = data["button_name_1"]
            button_url_1 = data['button_url_1']

            # Create the first button
            button_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)

            # Create the inline keyboard markup with both buttons
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(button_1)

            # Create the message with the photo, caption, and keyboard
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
        await call.message.answer('❌Xabar yuborish bekor qilindi.')
        await state.finish()
        return


@dp.message_handler(state=SendText.waiting_for_button_name_2, content_types=ContentType.TEXT)
async def photo_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["button_name_2"] = message.text

    # Ask the user to provide the URL for the first button
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

            # Create the first button
            button_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            button_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            # Create the inline keyboard markup with both buttons
            keyboard = InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
            keyboard.add(button_1, button_2)

            # Create the message with the photo, caption, and keyboard

        await bot.send_message(chat_id=ADMINS, text=f"<b>{caption}</b>", reply_markup=keyboard,
                               disable_web_page_preview=True)
        await bot.send_message(chat_id=ADMINS, text="Siz yubormoqchi bo'lgan xabar xuddi shunday kurinishda boladi."
                                                    "Haqiqatdan ham shu xabarni barcha foydalanuvchilarga yuborishni istaysizmi?\n"
                                                    "✅ Tastiqlash yoki ❌ Bekor qilish tugmasini bosing.",
                               reply_markup=tasdiqlash)
        await SendText.send_all_2.set()


    else:
        await call.message.answer('❌Xabar yuborish bekor qilindi.')
        await state.finish()
        return


@dp.callback_query_handler(state=SendText.send_all_2, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'send_message':
        async with state.proxy() as data:
            caption = data['caption']
            button_name_1 = data["button_name_1"]
            button_name_2 = data["button_name_2"]
            button_url_1 = data['button_url_1']
            button_url_2 = data['button_url_2']

            # Create the first button
            button_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            button_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            # Create the inline keyboard markup with both buttons
            keyboard = InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
            keyboard.add(button_1, button_2)

            # Create the message with the photo, caption, and keyboard

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
        await call.message.answer('❌Xabar yuborish bekor qilindi.')
        await state.finish()
        return


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
    # Ask the user to provide the URL for the first button
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
        await call.message.answer('Xabar yuborish bekor qilindi.')
        await state.finish()
        return


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
        await call.message.answer('❌Xabar yuborish bekor qilindi.')
        await state.finish()
        return


@dp.message_handler(state=SendPhoto.waiting_for_button_name_1, content_types=ContentType.TEXT)
async def photo_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["button_name_1"] = message.text

    # Ask the user to provide the URL for the first button
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

            # Create the first button
            button_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            # Create the inline keyboard markup with both buttons
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(button_1)

            # Create the message with the photo, caption, and keyboard
        await bot.send_photo(chat_id=ADMINS, photo=photo_file, caption=caption, reply_markup=keyboard)
        await bot.send_message(chat_id=ADMINS, text="Siz yubormoqchi bo'lgan xabar xuddi shunday kurinishda boladi."
                                                    "Haqiqatdan ham shu xabarni barcha foydalanuvchilarga yuborishni istaysizmi?\n"
                                                    "✅ Tastiqlash yoki ❌ Bekor qilish tugmasini bosing.",
                               reply_markup=tasdiqlash)
        await SendPhoto.send_all_1.set()
    else:
        await call.message.answer('Xabar yuborish bekor qilindi.')
        await state.finish()
        return


@dp.callback_query_handler(state=SendPhoto.send_all_1, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'send_message':
        async with state.proxy() as data:
            photo_file = data["photo_file"]
            caption = data['caption']
            button_name_1 = data["button_name_1"]
            button_url_1 = data['button_url_1']
            # Create the first button
            button_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)

            # Create the inline keyboard markup with both buttons
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(button_1)

            # Create the message with the photo, caption, and keyboard
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
        await call.message.answer('❌Xabar yuborish bekor qilindi.')
        await state.finish()
        return


@dp.message_handler(state=SendPhoto.waiting_for_button_name_2, content_types=ContentType.TEXT)
async def photo_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["button_name_2"] = message.text

    # Ask the user to provide the URL for the first button
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

            # Create the first button
            button_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            button_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            # Create the inline keyboard markup with both buttons
            keyboard = InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
            keyboard.add(button_1, button_2)

            # Create the message with the photo, caption, and keyboard

        await bot.send_photo(chat_id=ADMINS, photo=photo_file, caption=caption, reply_markup=keyboard)
        await bot.send_message(chat_id=ADMINS, text="Siz yubormoqchi bo'lgan xabar xuddi shunday kurinishda boladi."
                                                    "Haqiqatdan ham shu xabarni barcha foydalanuvchilarga yuborishni istaysizmi?\n"
                                                    "✅ Tastiqlash yoki ❌ Bekor qilish tugmasini bosing.",
                               reply_markup=tasdiqlash)
        await SendPhoto.send_all_2.set()
    else:
        await call.message.answer('❌Xabar yuborish bekor qilindi.')
        await state.finish()
        return


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

            # Create the first button
            button_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            button_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            # Create the inline keyboard markup with both buttons
            keyboard = InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
            keyboard.add(button_1, button_2)

            # Create the message with the photo, caption, and keyboard

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
        await call.message.answer('❌Xabar yuborish bekor qilindi.')
        await state.finish()
        return


@dp.message_handler(state=SendPhoto.waiting_for_button_name_3, content_types=ContentType.TEXT)
async def photo_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["button_name_3"] = message.text

    # Ask the user to provide the URL for the first button
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

            # Create the first button
            btn_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            btn_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            btn_3 = InlineKeyboardButton(text=button_name_3, url=button_url_3)
            # Create the inline keyboard markup with both buttons
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(btn_1, btn_2, btn_3)

            # Create the message with the photo, caption, and keyboard
            await bot.send_photo(chat_id=ADMINS, photo=photo_file, caption=caption, reply_markup=keyboard)
            await bot.send_message(chat_id=ADMINS, text="Siz yubormoqchi bo'lgan xabar xuddi shunday kurinishda boladi."
                                                        "Haqiqatdan ham shu xabarni barcha foydalanuvchilarga yuborishni istaysizmi?\n"
                                                        "✅ Tastiqlash yoki ❌ Bekor qilish tugmasini bosing.",
                                   reply_markup=tasdiqlash)
            await SendPhoto.send_all_3.set()
    else:
        await call.message.answer('❌Xabar yuborish bekor qilindi.')
        await state.finish()
        return


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

            # Create the first button
            btn_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            btn_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            btn_3 = InlineKeyboardButton(text=button_name_3, url=button_url_3)
            # Create the inline keyboard markup with both buttons
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(btn_1, btn_2, btn_3)

            # Create the message with the photo, caption, and keyboard

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
        await call.message.answer('❌Xabar yuborish bekor qilindi.')
        await state.finish()
        return


@dp.message_handler(state=SendPhoto.waiting_for_button_name_4, content_types=ContentType.TEXT)
async def photo_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["button_name_4"] = message.text

    # Ask the user to provide the URL for the first button
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

            # Create the first button
            btn_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            btn_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            btn_3 = InlineKeyboardButton(text=button_name_3, url=button_url_3)
            btn_4 = InlineKeyboardButton(text=button_name_4, url=button_url_4)
            # Create the inline keyboard markup with both buttons
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(btn_1, btn_2, btn_3, btn_4)

            # Create the message with the photo, caption, and keyboard
            await bot.send_photo(chat_id=ADMINS, photo=photo_file, caption=caption, reply_markup=keyboard)
            await bot.send_message(chat_id=ADMINS, text="Siz yubormoqchi bo'lgan xabar xuddi shunday kurinishda boladi."
                                                        "Haqiqatdan ham shu xabarni barcha foydalanuvchilarga yuborishni istaysizmi?\n"
                                                        "✅ Tastiqlash yoki ❌ Bekor qilish tugmasini bosing.",
                                   reply_markup=tasdiqlash)
            await SendPhoto.send_all_4.set()
    else:
        await call.message.answer('❌Xabar yuborish bekor qilindi.')
        await state.finish()
        return


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

            # Create the first button
            btn_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            btn_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            btn_3 = InlineKeyboardButton(text=button_name_3, url=button_url_3)
            btn_4 = InlineKeyboardButton(text=button_name_4, url=button_url_4)
            # Create the inline keyboard markup with both buttons
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(btn_1, btn_2, btn_3, btn_4)
            # Create the message with the photo, caption, and keyboard

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
        await call.message.answer('❌Xabar yuborish bekor qilindi.')
        await state.finish()
        return


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

    # Ask the user to provide the URL for the first button
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
        await call.message.answer('Xabar yuborish bekor qilindi.')
        await state.finish()
        return


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
        await call.message.answer('❌Xabar yuborish bekor qilindi.')
        await state.finish()
        return


@dp.message_handler(state=SendVideo.waiting_for_button_name_1, content_types=ContentType.TEXT)
async def video_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["button_name_1"] = message.text

    # Ask the user to provide the URL for the first button
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

            # Create the first button
            button_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            # Create the inline keyboard markup with both buttons
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(button_1)

            # Create the message with the video, caption, and keyboard
        await bot.send_video(chat_id=ADMINS, video=video_file, caption=caption, reply_markup=keyboard)
        await bot.send_message(chat_id=ADMINS, text="Siz yubormoqchi bo'lgan xabar xuddi shunday kurinishda boladi."
                                                    "Haqiqatdan ham shu xabarni barcha foydalanuvchilarga yuborishni istaysizmi?\n"
                                                    "✅ Tastiqlash yoki ❌ Bekor qilish tugmasini bosing.",
                               reply_markup=tasdiqlash)
        await SendVideo.send_all_1.set()
    else:
        await call.message.answer('Xabar yuborish bekor qilindi.')
        await state.finish()
        return


@dp.callback_query_handler(state=SendVideo.send_all_1, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'send_message':
        async with state.proxy() as data:
            video_file = data["video_file"]
            caption = data['caption']
            button_name_1 = data["button_name_1"]
            button_url_1 = data['button_url_1']

            # Create the first button
            button_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)

            # Create the inline keyboard markup with both buttons
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(button_1)

            # Create the message with the video, caption, and keyboard
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
        await call.message.answer('❌Xabar yuborish bekor qilindi.')
        await state.finish()
        return


@dp.message_handler(state=SendVideo.waiting_for_button_name_2, content_types=ContentType.TEXT)
async def video_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["button_name_2"] = message.text

    # Ask the user to provide the URL for the first button
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

            # Create the first button
            button_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            button_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            # Create the inline keyboard markup with both buttons
            keyboard = InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
            keyboard.add(button_1, button_2)

            # Create the message with the video, caption, and keyboard

        await bot.send_video(chat_id=ADMINS, video=video_file, caption=caption, reply_markup=keyboard)
        await bot.send_message(chat_id=ADMINS, text="Siz yubormoqchi bo'lgan xabar xuddi shunday kurinishda boladi."
                                                    "Haqiqatdan ham shu xabarni barcha foydalanuvchilarga yuborishni istaysizmi?\n"
                                                    "✅ Tastiqlash yoki ❌ Bekor qilish tugmasini bosing.",
                               reply_markup=tasdiqlash)
        await SendVideo.send_all_2.set()


    else:
        await call.message.answer('❌Xabar yuborish bekor qilindi.')
        await state.finish()
        return


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

            # Create the first button
            button_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            button_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            # Create the inline keyboard markup with both buttons
            keyboard = InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
            keyboard.add(button_1, button_2)

            # Create the message with the video, caption, and keyboard

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
        await call.message.answer('❌Xabar yuborish bekor qilindi.')
        await state.finish()
        return


@dp.message_handler(state=SendVideo.waiting_for_button_name_3, content_types=ContentType.TEXT)
async def video_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["button_name_3"] = message.text

    # Ask the user to provide the URL for the first button
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

            # Create the first button
            btn_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            btn_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            btn_3 = InlineKeyboardButton(text=button_name_3, url=button_url_3)
            # Create the inline keyboard markup with both buttons
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(btn_1, btn_2, btn_3)

            # Create the message with the video, caption, and keyboard
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

            # Create the first button
            btn_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            btn_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            btn_3 = InlineKeyboardButton(text=button_name_3, url=button_url_3)
            # Create the inline keyboard markup with both buttons
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(btn_1, btn_2, btn_3)

            # Create the message with the video, caption, and keyboard

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
        await call.message.answer('❌Xabar yuborish bekor qilindi.')
        await state.finish()
        return


@dp.message_handler(state=SendVideo.waiting_for_button_name_4, content_types=ContentType.TEXT)
async def video_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["button_name_4"] = message.text

    # Ask the user to provide the URL for the first button
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

            # Create the first button
            btn_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            btn_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            btn_3 = InlineKeyboardButton(text=button_name_3, url=button_url_3)
            btn_4 = InlineKeyboardButton(text=button_name_4, url=button_url_4)
            # Create the inline keyboard markup with both buttons
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(btn_1, btn_2, btn_3, btn_4)

            # Create the message with the video, caption, and keyboard
            await bot.send_video(chat_id=ADMINS, video=video_file, caption=caption, reply_markup=keyboard)
            await bot.send_message(chat_id=ADMINS, text="Siz yubormoqchi bo'lgan xabar xuddi shunday kurinishda boladi."
                                                        "Haqiqatdan ham shu xabarni barcha foydalanuvchilarga yuborishni istaysizmi?\n"
                                                        "✅ Tastiqlash yoki ❌ Bekor qilish tugmasini bosing.",
                                   reply_markup=tasdiqlash)
            await SendVideo.send_all_4.set()
    else:
        await call.message.answer('❌Xabar yuborish bekor qilindi.')
        await state.finish()
        return


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

            # Create the first button
            btn_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            btn_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            btn_3 = InlineKeyboardButton(text=button_name_3, url=button_url_3)
            btn_4 = InlineKeyboardButton(text=button_name_4, url=button_url_4)
            # Create the inline keyboard markup with both buttons
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(btn_1, btn_2, btn_3, btn_4)
            # Create the message with the video, caption, and keyboard

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
        await call.message.answer('❌Xabar yuborish bekor qilindi.')
        await state.finish()
        return


# ============================================================ SEND A VOICE ===============================================================


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
    await message.answer("Xabar uchun tugma yaratishni hohlaysizmi?")
    await SendText.waiting_for_button_name_1.set()

    await message.answer("Iltimos, birinchi tugma nomini kiriting.")
    await SendText.waiting_for_button_name_1.set()


@dp.message_handler(state=SendText.waiting_for_button_name_1, content_types=ContentType.TEXT)
async def bot_echo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["button_name_1"] = message.text

    await message.answer("Iltimos, birinchi tugma uchun URL manzilini kiriting.")
    await SendText.waiting_for_button_url_1.set()


@dp.message_handler(state=SendText.waiting_for_button_url_1, content_types=ContentType.TEXT)
async def video_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['button_url_1'] = message.text

    await message.answer("Birinchi tugma uchun URL manzili qabul qilindi.", reply_markup=button_2)
    await SendText.next_call_2.set()


'6,6118934522,qkam01a,its.komosh,Uzbek,2023-05-22 20:32:20'


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

            # Create the first button
            button_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            # Create the inline keyboard markup with both buttons
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(button_1)

            # Create the message with the video, caption, and keyboard
        await bot.send_message(chat_id=ADMINS, text=caption, reply_markup=keyboard, disable_web_page_preview=True)
        await bot.send_message(chat_id=ADMINS, text="Siz yubormoqchi bo'lgan xabar xuddi shunday kurinishda boladi."
                                                    "Haqiqatdan ham shu xabarni barcha foydalanuvchilarga yuborishni istaysizmi?\n"
                                                    "✅ Tastiqlash yoki ❌ Bekor qilish tugmasini bosing.",
                               reply_markup=tasdiqlash)
        await SendText.send_all_1.set()
    else:
        await call.message.answer('Xabar yuborish bekor qilindi.')
        await state.finish()
        return


@dp.callback_query_handler(state=SendText.send_all_1, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'send_message':
        async with state.proxy() as data:
            caption = data['caption']
            button_name_1 = data["button_name_1"]
            button_url_1 = data['button_url_1']

            # Create the first button
            button_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)

            # Create the inline keyboard markup with both buttons
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(button_1)

            # Create the message with the video, caption, and keyboard
            all_user_id = await User.get_all_user()
            all_group_id = await Group.get_all_group()
            count_user = 0
            count_group = 0
            try:
                for user_id in all_user_id:
                    if await bot.send_message(chat_id=user_id, text=caption, reply_markup=keyboard,
                                              disable_web_page_preview=True):
                        count_user += 1
                    await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
                await bot.send_message(ADMINS,
                                       f"Sizning xabaringiz barcha <b>{count_user} ta</b> foydalanuvchiga muvaffaqiyatli yuborildi.")

                for group_id in all_group_id:
                    if await bot.send_message(chat_id=group_id, text=caption, reply_markup=keyboard,
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
        await call.message.answer('❌Xabar yuborish bekor qilindi.')
        await state.finish()
        return


@dp.message_handler(state=SendText.waiting_for_button_name_2, content_types=ContentType.TEXT)
async def video_button_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["button_name_2"] = message.text

    # Ask the user to provide the URL for the first button
    await message.answer("Iltimos, ikkinchi tugma uchun URL manzilini kiriting.")
    await SendText.waiting_for_button_url_2.set()


@dp.message_handler(state=SendText.waiting_for_button_url_2, content_types=ContentType.TEXT)
async def video_button_url(message: types.Message, state: FSMContext):
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

            # Create the first button
            button_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            button_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            # Create the inline keyboard markup with both buttons
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(button_1, button_2)

            # Create the message with the video, caption, and keyboard

        await bot.send_message(chat_id=ADMINS, text=caption, reply_markup=keyboard)
        await bot.send_message(chat_id=ADMINS, text="Siz yubormoqchi bo'lgan xabar xuddi shunday kurinishda boladi."
                                                    "Haqiqatdan ham shu xabarni barcha foydalanuvchilarga yuborishni istaysizmi?\n"
                                                    "✅ Tastiqlash yoki ❌ Bekor qilish tugmasini bosing.",
                               reply_markup=tasdiqlash)
        await SendText.send_all_2.set()


    else:
        await call.message.answer('❌Xabar yuborish bekor qilindi.')
        await state.finish()
        return


@dp.callback_query_handler(state=SendText.send_all_2, chat_id=ADMINS)
async def send_rek(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'send_message':
        async with state.proxy() as data:
            caption = data['caption']
            button_name_1 = data["button_name_1"]
            button_name_2 = data["button_name_2"]
            button_url_1 = data['button_url_1']
            button_url_2 = data['button_url_2']

            # Create the first button
            button_1 = InlineKeyboardButton(text=button_name_1, url=button_url_1)
            button_2 = InlineKeyboardButton(text=button_name_2, url=button_url_2)
            # Create the inline keyboard markup with both buttons
            keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(button_1, button_2)

            # Create the message with the video, caption, and keyboard

            all_user_id = await User.get_all_user()
            all_group_id = await Group.get_all_group()
        count_user = 0
        count_group = 0
        try:
            for user_id in all_user_id:
                if await bot.send_message(chat_id=user_id, text=caption, reply_markup=keyboard,
                                          disable_web_page_preview=True):
                    count_user += 1
                await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
            await bot.send_message(ADMINS,
                                   f"Sizning xabaringiz barcha <b>{count_user} ta</b> foydalanuvchiga muvaffaqiyatli yuborildi.")

            for group_id in all_group_id:
                if await bot.send_message(chat_id=group_id, text=caption, reply_markup=keyboard,
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
        await call.message.answer('❌Xabar yuborish bekor qilindi.')
        await state.finish()
        return
