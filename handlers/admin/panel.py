from collections import Counter
from databasedb.models import *
from keyboards import *
from states import *
from loader import *

statistic_lang = {
    'Uzbek': "🇺🇿 Uzbek ",
    'English': "🇬🇧 English ",
    'Russian': "🇷🇺 Russian ",
    'Arabic': "🇸🇦 Arabic ",
    'Turkey': "🇹🇷 Turkey ",
    'Germany': "🇩🇪 Germany ",
    'France': "🇫🇷 France ",
    'Spain': "🇪🇸 Spain ",
    'Italy': "🇮🇹 Italy ",
    'Kazakh': "🇰🇿 Kazakh ",
    'Indian': "🇮🇳 Indian ",
    'Ukraine': "🇺🇦 Ukraine ",
    'Azerbaijan': "🇦🇿 Azerbaijan ",
}


async def count_users_by_language():
    async with db() as session:
        users = await session.execute(select(User.language))
        groups = await session.execute(select(Group.language))
        group_members = await session.execute(select(Group.group_members))
        lang_count_user = Counter([language for language, in users])
        lang_count_group = Counter([language for language, in groups])
        return lang_count_user, lang_count_group, group_members


async def print_language_statistics():
    lang_count_user, lang_count_group, total_group_members = await count_users_by_language()
    total_members = sum(row[0] for row in total_group_members)
    total_users = sum(lang_count_user.values())
    total_groups = sum(lang_count_group.values())
    user_data = '\n'.join(
        f"┃ {language_name}:    {lang_count_user.get(language_code, 0)}"
        for language_code, language_name in statistic_lang.items()
    )
    group_data = '\n'.join(
        f"┃ {language_name}:    {lang_count_group.get(language_code, 0)}"
        for language_code, language_name in statistic_lang.items()
    )
    user_statist = f'''
┏━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📊 User Statistika
┣━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 👤 Users count:  {total_users}
┣━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 🌐 Language used count
┣━━━━━━━━━━━━━━━━━━━━━━━━━
{user_data}
┗━━━━━━━━━━━━━━━━━━━━━━━━━
'''
    group_statist = f'''
┏━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📊 Group Statistika
┣━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 👥 Groups count:  {total_groups}
┣━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 👥 Group members:  {total_members}
┣━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 🌐 Language used count
┣━━━━━━━━━━━━━━━━━━━━━━━━━
{group_data}
┗━━━━━━━━━━━━━━━━━━━━━━━━━
'''
    return user_statist, group_statist


@dp.message_handler(commands=['admin'], chat_id=ADMINS)
async def bot_echo(message: types.Message):
    await message.answer("⚙ SIZ ADMIN PANELDASIZ", reply_markup=menu_kb)


@dp.callback_query_handler(text="bekor_qilish", chat_id=ADMINS)
async def admin_send_message(call: types.CallbackQuery):
    chat_id = call.from_user.id
    callback_id = call.message.message_id
    await bot.delete_message(chat_id=chat_id, message_id=callback_id)


@dp.callback_query_handler(text="statistic")
async def Admin_send(call: types.CallbackQuery):
    user, group = await print_language_statistics()
    chat_id = call.from_user.id
    callback_id = call.message.message_id
    await bot.edit_message_text(chat_id=chat_id, message_id=callback_id, text=f'<b>{user}</b>')
    await bot.send_message(chat_id=chat_id, text=f'<b>{group}</b>')


@dp.callback_query_handler(text="send", chat_id=ADMINS)
async def admin_send_message(call: types.CallbackQuery):
    chat_id = call.from_user.id
    callback_id = call.message.message_id
    await bot.edit_message_text(chat_id=chat_id, message_id=callback_id, text="Xabar turini Tanlang 👇🏻",
                                reply_markup=admin_kb)


def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


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
    try:
        await Admin.create_admin(chat_id, user.username, user.first_name)
        await message.answer(f"{user.full_name} adminlar ro'yxatiga qo'shildi.")
        await state.finish()
    except:
        await message.answer(f"Chat ID: {chat_id} haqiqiy bir foydalanuvchi emas.")
        await state.finish()
        return


@dp.message_handler(commands=['cleardb'], chat_id=ADMINS)
async def clear_db_handler(message: types.Message):
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



@dp.message_handler(commands=['break'], chat_id=ADMINS)
async def add_admin_handler(message: types.Message, state: FSMContext):
    try:
        await message.answer("⚙ Xabar yuborish toxtatildi")
        await state.finish()
    except Exception as e:
        await state.finish()
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")