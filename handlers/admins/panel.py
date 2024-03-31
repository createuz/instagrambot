from collections import Counter
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType
from db.models import *
from keyboards import *
from data import *

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


@dp.message_handler(commands=['admins'])
async def bot_echo(message: types.Message):
    if message.chat.id in ADMINS:
        await message.delete()
        await message.answer("<b>⚙ Welcome to Admin Panel</b>", reply_markup=menu_kb)
    return


@dp.callback_query_handler(text="chat_ids_doc")
async def add_admin_handler(call: types.CallbackQuery):
    try:
        if call.message.chat.id in ADMINS:
            await bot.answer_callback_query(callback_query_id=call.id)
            users_chat_id = await User.get_all_chat_ids()
            groups_chat_id = await Group.get_all_chat_ids()
            file_path = 'chat_ids.txt'
            all_chat_ids = users_chat_id + groups_chat_id
            count_users = len(users_chat_id)
            count_groups = len(groups_chat_id)
            with open(file_path, 'w') as file:
                for chat_id in all_chat_ids:
                    file.write(f"{chat_id}\n")
            msg = f"<b>• All users count:  {count_users}\n• All groups count:  {count_groups}</b>"
            with open(file_path, 'rb') as doc_file:
                await bot.send_document(chat_id=call.message.chat.id, document=types.InputFile(doc_file), caption=msg)
            os.remove(file_path)
        return None
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        return None


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
            await Admin.create_admin(chat_id=chat_id, username=username, first_name=first_name)
            await bot.send_message(
                chat_id=message.chat.id,
                text=f"<b>{first_name}</b> Adminlar ro'yxatiga qo'shildi ✅",
                reply_markup=admin_menu
            )
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
    try:
        chat_id = call.message.chat.id
        callback_id = call.message.message_id
        await bot.delete_message(chat_id, callback_id)
        await bot.answer_callback_query(callback_query_id=call.id)
    except Exception as e:
        logger.exception("Xatolik: %s", e)


@dp.callback_query_handler(text="send_all_msg")
async def admin_send_message(call: types.CallbackQuery):
    chat_id = call.from_user.id
    callback_id = call.message.message_id
    await bot.edit_message_text(chat_id=chat_id, message_id=callback_id, text="<b>💬 Xabar turini Tanlang</b>",
                                reply_markup=send_message_kb)


@dp.message_handler(commands=['break'], state='*')
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
            media_count = await Statistics.get_media_count()
            msj = f'''
┏━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📊 Media Statistic
┣━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📥 Total Media Count:  {media_count}
┗━━━━━━━━━━━━━━━━━━━━━━━━━'''
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=f"<b>{msj}</b>", reply_markup=back_media_statistic)
        except Exception as e:
            logger.exception("Xatolik: %s", e)
    return


@dp.callback_query_handler(text="all_statistics")
async def total_user_statistics(call: types.CallbackQuery):
    if call.message.chat.id in ADMINS:
        try:
            async with db() as session:
                users = await session.execute(select(User.language))
                groups = await session.execute(select(Group.language))
                group_members = await session.execute(select(Group.group_members))
                media_count = await session.scalar(select(Statistics.get_media_count))
            lang_count_user = Counter([language for language, in users])
            total_users = sum(lang_count_user.values())
            lang_count_group = Counter([language for language, in groups])
            total_members = sum(row[0] for row in group_members)
            total_groups = sum(lang_count_group.values())
            statists = f'''
┏━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📊 All Statistics
┣━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 👤 Users count :   {total_users}
┣━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 👤 Groups count :   {total_groups}
┣━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 👥 Groups members:  {total_members}
┣━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📥 Media Count:  {media_count}
┗━━━━━━━━━━━━━━━━━━━━━━━━━'''
            await bot.answer_callback_query(callback_query_id=call.id, text="📊 All Statistics")
            await bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f'<b>{statists}</b>',
                reply_markup=update_user_statistic
            )
        except Exception as e:
            logger.exception("Xatolik: %s", e)
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
        month = await User.joined_last_month()
        today = await User.joined_last_24_hours()
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
