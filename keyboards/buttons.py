from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.config import BOT_URL

language_keyboard = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="uz"),
    InlineKeyboardButton(text="🇷🇺 Русский", callback_data="ru"),
    InlineKeyboardButton(text="🇬🇧 English", callback_data="en"),
    InlineKeyboardButton(text="🇹🇷 Türkçe", callback_data="tr"),
    InlineKeyboardButton(text="🇺🇦 Український", callback_data="uk"),
    InlineKeyboardButton(text="🇰🇿 Қазақ", callback_data="qz"),
    InlineKeyboardButton(text="🇩🇪 Deutsch", callback_data="nm"),
    InlineKeyboardButton(text="🇫🇷 Français", callback_data="fr"),
    InlineKeyboardButton(text="🇪🇸 Español", callback_data="es"),
    InlineKeyboardButton(text="🇮🇹 Italiano", callback_data="it"),
    InlineKeyboardButton(text="🇦🇿 Azərbaycanca", callback_data="az"),
    InlineKeyboardButton(text="العربية 🇸🇦", callback_data="ar")
)

add_group = {
    'Uzbek': InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Guruhga Qushish', url=BOT_URL)),
    'Russian': InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Добавить в группу', url=BOT_URL)),
    'Arabic': InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text="إضافة إلى المجموعة ➕", url=BOT_URL)),
    'Turkey': InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Gruba ekle', url=BOT_URL)),
    'Germany': InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Zur Gruppe hinzufügen', url=BOT_URL)),
    'France': InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Ajouter au groupe', url=BOT_URL)),
    'Spain': InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Añadir al grupo', url=BOT_URL)),
    'Italy': InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Aggiungi al gruppo', url=BOT_URL)),
    'English': InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Add to group', url=BOT_URL)),
    "Kazakh": InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Топқа қосу', url=BOT_URL)),
    "Ukraine": InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Додати до групи', url=BOT_URL)),
    "Azerbaijan": InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Qrupa əlavə edin', url=BOT_URL))
}

bekor_qilish_kb = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("🗑 Cancel", callback_data="bekor_qilish"))
del_help = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='🔻', callback_data=f"bekor_qilish"))
back_media_statistic = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("⬅ Back", callback_data="statistic"))

menu_kb = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("💬 Send Message", callback_data="send_all_msg"),
    InlineKeyboardButton("📊 Statistic", callback_data="statistic"),
    InlineKeyboardButton("🅰 Admins", callback_data="admin_menu"),
    InlineKeyboardButton("🏠 Home", callback_data="bekor_qilish"))

admin_menu = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("📄 Admins Data", callback_data="admins_data"),
    InlineKeyboardButton("➕ Add Admin", callback_data="add_admin"),
    InlineKeyboardButton("🗑 Delete Admin", callback_data="del_admin"),
    InlineKeyboardButton("⬅ Back", callback_data="menu_kb"))

chose_statistic_kb = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("👤 User Statistic", callback_data="user_statistic"),
    InlineKeyboardButton("👥 Group Statistic", callback_data="group_statistic"),
    InlineKeyboardButton("📹 Media Statistic", callback_data="media_statistic"),
    InlineKeyboardButton("📄 Chat Ids", callback_data="chat_ids_doc"),
    InlineKeyboardButton("⬅ Back", callback_data="menu_kb"))

update_user_statistic = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("🔄 Update", callback_data="update_user_statistic"),
    InlineKeyboardButton("⬅ Back", callback_data="statistic"))

update_user_statistic_2x = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("🔄 Update", callback_data="user_statistic"),
    InlineKeyboardButton("⬅ Back", callback_data="statistic"))

update_group_statistic = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("🔄 Update", callback_data="update_group_statistic"),
    InlineKeyboardButton("⬅ Back", callback_data="statistic"))

update_group_statistic_2x = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("🔄 Update", callback_data="group_statistic"),
    InlineKeyboardButton("⬅ Back", callback_data="statistic"))

send_message_kb = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("📝 Send Message", callback_data="text"),
    InlineKeyboardButton("🖼 Send Photo", callback_data="photo"),
    InlineKeyboardButton("📹 Send Video", callback_data="video"),
    InlineKeyboardButton("🗑 Cancel", callback_data="bekor_qilish"),
    InlineKeyboardButton("⬅ Back", callback_data="menu_kb"))

button_2 = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("📍2-Tugmani kiritish", callback_data="button_2"),
    InlineKeyboardButton("✅ Xabarni yuborish", callback_data="send_message"),
    InlineKeyboardButton("🗑 Bekor qilish", callback_data="cancel"))

button_3 = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("📍3-Tugmani kiritish", callback_data="button_3"),
    InlineKeyboardButton("✅ Xabarni yuborish", callback_data="send_message"),
    InlineKeyboardButton("🗑 Bekor qilish", callback_data="cancel"))

button_4 = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("📍4-Tugmani kiritish", callback_data="button_4"),
    InlineKeyboardButton("✅ Xabarni yuborish", callback_data="send_message"),
    InlineKeyboardButton("🗑 Bekor qilish", callback_data="cancel"))

button_5 = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("✅ Tasdiqlash", callback_data="send_message"),
    InlineKeyboardButton("🗑 Bekor qilish ", callback_data="cancel"))

tasdiqlash = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("✅ Tasdiqlash", callback_data="send_message"),
    InlineKeyboardButton("🗑 Bekor qilish ", callback_data="cancel"))

add_btn = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("📍Tugma yaratish", callback_data="add_btn"),
    InlineKeyboardButton("✅ Xabarni yuborish", callback_data="send_message"),
    InlineKeyboardButton("🗑 Bekor qilish ", callback_data="cancel"))
