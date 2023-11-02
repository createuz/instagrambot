from collections import Counter

from databasedb.models import *
from keyboards import *
from states import *
from loader import *


@dp.message_handler(commands=['admin'])
async def bot_echo(message: types.Message):
    if message.chat.id in ADMINS:
        await message.delete()
        await message.answer("<b>⚙ Welcome to Admin Panel</b>", reply_markup=menu_kb)
    return


@dp.callback_query_handler(text="menu_kb")
async def add_admin_handler(call: types.CallbackQuery):
    if call.message.chat.id in ADMINS:
        chat_id = call.from_user.id
        callback_id = call.message.message_id
        await bot.edit_message_text(chat_id=chat_id, message_id=callback_id, text="<b>⚙ Welcome to Admin Panel</b>",
                                    reply_markup=menu_kb)
    return


@dp.callback_query_handler(text="admin_menu")
async def add_admin_handler(call: types.CallbackQuery):
    if call.message.chat.id in ADMINS:
        chat_id = call.from_user.id
        callback_id = call.message.message_id
        await bot.edit_message_text(chat_id=chat_id, message_id=callback_id, text="<b>🅰 Admin menu</b>",
                                    reply_markup=admin_menu)
    return



@dp.callback_query_handler(text="admins_data")
async def admin_send_message(call: types.CallbackQuery):
    if call.message.chat.id in ADMINS:
        try:
            callback_id = call.message.message_id
            data = await Admin.get_admins_data()
            if data:
                admin_data = '\n'.join([
                    f'''┃ ID: <code>{user.chat_id}</code>  ┃  <a href='{f'tg://user?id={user.chat_id}'}'>{user.first_name}</a>'''
                    for user in data])
                data_msg = f'''
┏━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 🅰  Admin Statistic
┣━━━━━━━━━━━━━━━━━━━━━━━━━
{admin_data}
┗━━━━━━━━━━━━━━━━━━━━━━━━━'''
                return await bot.edit_message_text(chat_id=call.message.chat.id, message_id=callback_id,
                                                   text=f'<b>{data_msg}</b>')
            return await bot.edit_message_text(chat_id=call.message.chat.id, message_id=callback_id,
                                               text=f'<b>🛑 Hozirda Admin malumotlari muvjud emas</b>')
        except Exception as e:
            logger.exception("Xatolik: %s", e)
            return await bot.send_message(chat_id=call.message.chat.id,
                                          text=f'<b>🛑 Hozirda Admin malumotlari muvjud emas</b>')
    return



@dp.callback_query_handler(text="add_admin")
async def add_admin_handler(call: types.CallbackQuery):
    if call.message.chat.id in ADMINS:
        chat_id = call.from_user.id
        callback_id = call.message.message_id
        await bot.edit_message_text(chat_id=chat_id, message_id=callback_id,
                                    text="Yangi adminning chat ID sini kiriting")
        await AddAdmin.waiting_for_add_chat_id.set()
    return


@dp.message_handler(state=AddAdmin.waiting_for_add_chat_id, content_types=ContentType.TEXT)
async def add_admin_save_handler(message: types.Message, state: FSMContext):
    if message.chat.id in ADMINS:
        try:
            chat_id, username, first_name = await User.get_user(message.text)
            await Admin.create_admin(chat_id, username, first_name)
            await bot.send_message(message.chat.id, f"<b>{first_name}</b> Adminlar ro'yxatiga qo'shildi ✅",
                                   reply_markup=admin_menu)
            await state.finish()
        except Exception as e:
            await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")
    return


@dp.callback_query_handler(text="del_admin")
async def add_admin_handler(call: types.CallbackQuery):
    if call.message.chat.id in ADMINS:
        chat_id = call.from_user.id
        callback_id = call.message.message_id
        await bot.edit_message_text(chat_id=chat_id, message_id=callback_id,
                                    text="O'chirmoqchi bo'lgan adminning Chat ID sini kiriting!")
        await AddAdmin.waiting_for_del_chat_id.set()
    return


@dp.message_handler(state=AddAdmin.waiting_for_del_chat_id, content_types=ContentType.TEXT)
async def add_admin_save_handler(message: types.Message, state: FSMContext):
    if message.chat.id in ADMINS:
        try:
            await Admin.delete_admin(message.text)
            await bot.send_message(message.chat.id,
                                   f"Chat ID: <b>{message.text}</b>  Adminlar ro'yxatidan chiqarildi ✅",
                                   reply_markup=admin_menu)
            await state.finish()
        except Exception as e:
            await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")
    return


@dp.callback_query_handler(text="bekor_qilish")
async def admin_send_message_delete(call: types.CallbackQuery):
    if call.message.chat.id in ADMINS:
        try:
            chat_id = call.message.chat.id
            callback_id = call.message.message_id
            await bot.delete_message(chat_id, callback_id)
            await bot.answer_callback_query(callback_query_id=call.id)
        except Exception as e:
            logger.exception("Xatolik: %s", e)
    return


@dp.callback_query_handler(text="send_all_msg")
async def admin_send_message(call: types.CallbackQuery):
    chat_id = call.from_user.id
    callback_id = call.message.message_id
    await bot.edit_message_text(chat_id=chat_id, message_id=callback_id, text="<b>💬 Xabar turini Tanlang</b>",
                                reply_markup=send_message_kb)


def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


@dp.message_handler(commands=['cleardb'])
async def clear_db_handler(message: types.Message):
    if message.chat.id in ADMINS:
        try:
            user_input = message.text.split(' ')[1] if len(message.text.split(' ')) > 1 else None
            if not user_input:
                await message.answer("❌ Parolni kiriting: /cleardb <parol>")
                return
            if check_password(user_input, ADMIN_PASSWORD_HASH):
                async with db() as session:
                    await session.execute(InstagramMediaDB.__table__.delete())
                    await session.commit()
                await message.answer("✅ Ma'lumotlar tozalandi.")
            else:
                await message.answer("❌ Xato parol! To'g'ri parolni kiriting.")
        except Exception as e:
            await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")
    return


@dp.message_handler(commands=['break'])
async def add_admin_handler(message: types.Message, state: FSMContext):
    if message.chat.id in ADMINS:
        try:
            await message.answer("⚙ Xabar yuborish toxtatildi")
            await state.finish()
        except Exception as e:
            await state.finish()
            await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")
    return


@dp.callback_query_handler(text="statistic")
async def chose_statistics(call: types.CallbackQuery):
    if call.message.chat.id in ADMINS:
        try:
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text='<b>📊 Chose Statistic</b>', reply_markup=chose_statistic_kb)
        except Exception as e:
            logger.exception("Xatolik: %s", e)
    return


@dp.callback_query_handler(text="media_statistic")
async def chose_statistics(call: types.CallbackQuery):
    if call.message.chat.id in ADMINS:
        try:
            stat = await InstagramMediaDB.count_media()
            msj = f'''
┏━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📊 Media Statistic
┣━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📥 Total Media Count:  {stat}
┗━━━━━━━━━━━━━━━━━━━━━━━━━'''
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=f"<b>{msj}</b>", reply_markup=back_media_statistic)
        except Exception as e:
            logger.exception("Xatolik: %s", e)
    return


@dp.message_handler(commands=['update_media'])
async def chose_statistics(message: types.Message):
    if message.chat.id in ADMINS:
        await message.delete()
        await bot.send_message(chat_id=message.chat.id, text='<b>Miqdorni kiriting max: 1000 ta</b>')
        await AddAdmin.waiting_for_miqdor.set()
    return


@dp.message_handler(state=AddAdmin.waiting_for_miqdor, content_types=ContentType.TEXT)
async def add_admin_save_handler(message: types.Message, state: FSMContext):
    if message.chat.id in ADMINS:
        try:
            await StatisticDB.update_media_count(int(message.text))
            await bot.send_message(message.chat.id, f"Total media count oshirildi ✅")
            await state.finish()
        except Exception as e:
            await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")
    return


async def user_language_statistics():
    try:
        async with db() as session:
            users = await session.execute(select(User.language))
        lang_count_user = Counter([language for language, in users])
        total_users = sum(lang_count_user.values())
        user_data = '\n'.join(
            f"┃ {language_name}:    {lang_count_user.get(language_code, 0)}"
            for language_code, language_name in statistic_lang.items()
        )
        month = await User.count_users_registered_last_month()
        today = await User.count_users_registered_last_24_hours()
        user_statist = f'''
┏━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📊 User Statistic
┣━━━━━━━━━━━━━━━━━━━━━━━━━
┃ ➕ Joined today :   {today}
┣━━━━━━━━━━━━━━━━━━━━━━━━━
┃ ➕ Joined this month :   {month}
┣━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 👤 All users count :   {total_users}
┣━━━━━━━━━━━━━━━━━━━━━━━━━
{user_data}
┗━━━━━━━━━━━━━━━━━━━━━━━━━'''
        return user_statist
    except Exception as e:
        logger.exception("Xatolik: %s", e)
        return None


async def group_language_statistics():
    try:
        async with db() as session:
            groups = await session.execute(select(Group.language))
            group_members = await session.execute(select(Group.group_members))
        lang_count_group = Counter([language for language, in groups])
        total_members = sum(row[0] for row in group_members)
        total_groups = sum(lang_count_group.values())
        group_data = '\n'.join(
            f"┃ {language_name}:    {lang_count_group.get(language_code, 0)}"
            for language_code, language_name in statistic_lang.items()
        )
        group_statist = f'''
┏━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📊 Group Statistic
┣━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 👥 Groups count:  {total_groups}
┣━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 👥 Group members:  {total_members}
┣━━━━━━━━━━━━━━━━━━━━━━━━━
{group_data}
┗━━━━━━━━━━━━━━━━━━━━━━━━━'''
        return group_statist
    except Exception as e:
        logger.exception("Xatolik: %s", e)
        return None


@dp.callback_query_handler(text="user_statistic")
async def total_user_statistics(call: types.CallbackQuery):
    if call.message.chat.id in ADMINS:
        try:
            user = await user_language_statistics()
            chat_id = call.from_user.id
            callback_id = call.message.message_id
            await bot.answer_callback_query(callback_query_id=call.id, text="Updating statistics...")
            await bot.edit_message_text(chat_id=chat_id, message_id=callback_id, text=f'<b>{user}</b>',
                                        reply_markup=update_user_statistic)
        except Exception as e:
            logger.exception("Xatolik: %s", e)
    return


@dp.callback_query_handler(text="update_user_statistic")
async def update_total_user_statistics(call: types.CallbackQuery):
    if call.message.chat.id in ADMINS:
        try:
            user = await user_language_statistics()
            chat_id = call.from_user.id
            callback_id = call.message.message_id
            await bot.answer_callback_query(callback_query_id=call.id, text="Updating statistics...")
            await bot.edit_message_text(chat_id=chat_id, message_id=callback_id, text=f'<b>{user}</b>',
                                        reply_markup=update_user_statistic_2x)
        except Exception as e:
            logger.exception("Xatolik: %s", e)
    return


@dp.callback_query_handler(text="group_statistic")
async def total_group_statistics(call: types.CallbackQuery):
    if call.message.chat.id in ADMINS:
        try:
            group = await group_language_statistics()
            chat_id = call.from_user.id
            callback_id = call.message.message_id
            await bot.answer_callback_query(callback_query_id=call.id, text="Updating statistics...")
            await bot.edit_message_text(chat_id=chat_id, message_id=callback_id, text=f'<b>{group}</b>',
                                        reply_markup=update_group_statistic)
        except Exception as e:
            logger.exception("Xatolik: %s", e)
    return


@dp.callback_query_handler(text="update_group_statistic")
async def update_total_group_statistics(call: types.CallbackQuery):
    if call.message.chat.id in ADMINS:
        try:
            group = await group_language_statistics()
            chat_id = call.from_user.id
            callback_id = call.message.message_id
            await bot.answer_callback_query(callback_query_id=call.id, text="Updating statistics...")
            await bot.edit_message_text(chat_id=chat_id, message_id=callback_id, text=f'<b>{group}</b>',
                                        reply_markup=update_group_statistic_2x)
        except Exception as e:
            logger.exception("Xatolik: %s", e)
    return
