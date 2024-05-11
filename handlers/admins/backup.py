import aiofiles
import aiohttp
from aiogram.types import ContentType
from aiogram.utils.exceptions import BadRequest
from db.models import *
from data import *


@dp.message_handler(commands=['backup'])
async def bot_echo(message: types.Message):
    if message.chat.id in ADMINS:
        await message.delete()
        await bot.send_message(
            chat_id=message.chat.id,
            text="<b>📄 TXT faylni yuboring.</b>"
        )
        await Backup.wait_txt_file.set()


async def download_file(file_id, doc_path):
    try:
        file = await bot.get_file(file_id)
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}') as response:
                response.raise_for_status()
                async with aiofiles.open(doc_path, "wb") as new_file:
                    await new_file.write(await response.read())
    except (aiohttp.ClientError, Exception) as e:
        logger.exception(e)


async def handle_get_chat_ids(message: types.Message):
    doc_path = f"C:/Users/creat/Desktop/Bot/InstagramBot/backup/{message.document.file_id}"
    try:
        await download_file(message.document.file_id, doc_path)
        if os.path.exists(doc_path):
            async with aiofiles.open(doc_path, 'r') as doc_file:
                chat_ids = await doc_file.read()
            return chat_ids.strip().split('\n')
        return None
    except (BadRequest, Exception) as e:
        logger.exception(e)
        return None
    finally:
        if os.path.exists(doc_path):
            os.remove(doc_path)


async def process_chat_id(chat_id):
    try:
        chat_id = int(chat_id)
        success = None
        if chat_id > 0:
            user = await bot.get_chat(chat_id=chat_id)
            if user:
                success = await User.create_user(
                    chat_id=chat_id,
                    username=user.username,
                    first_name=user.first_name,
                    language='None',
                    added_by='true'
                )
        else:
            group = await bot.get_chat(chat_id=chat_id)
            if group:
                members = await bot.get_chat_members_count(chat_id=chat_id)
                success = await Group.create_group(
                    chat_id=chat_id,
                    name=group.title,
                    username=group.username,
                    members=members,
                    language='None'
                )
        return success
    except Exception as e:
        logger.exception(f"Error processing chat ID {chat_id}: {e}")


async def process_chat_ids(chat_ids: list):
    success_chats = []
    failed_chats = []
    for chat_id in chat_ids:
        success = await process_chat_id(chat_id)
        if success:
            success_chats.append(chat_id)
        else:
            failed_chats.append(chat_id)
    return success_chats, failed_chats


@dp.message_handler(content_types=ContentType.DOCUMENT, state=Backup.wait_txt_file)
async def handle_media(message: types.Message):
    chat_ids = await handle_get_chat_ids(message=message)
    if chat_ids is None:
        return await bot.send_message(message.chat.id, "Faylni olishda xatolik yuz berdi.")
    success_chats, failed_chats = await process_chat_ids(chat_ids)
    await bot.send_message(
        chat_id=message.chat.id,
        text=f"<b>✅  {len(success_chats)} ta chat muvaffaqiyatli qo'shildi.\n\n"
             f"🔴  {len(failed_chats)} ta chat qo'shilmadi.</b>"
    )
