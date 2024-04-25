from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.config import BOT_URL

language_keyboard = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="uz"),
    InlineKeyboardButton(text="🇷🇺 Русский", callback_data="ru"),
    InlineKeyboardButton(text="🇬🇧 English", callback_data="en"),
    InlineKeyboardButton(text="🇹🇷 Türkçe", callback_data="tr"),
    InlineKeyboardButton(text="🇺🇦 Український", callback_data="uk"),
    InlineKeyboardButton(text="🇰🇿 Қазақ", callback_data="kz"),
    InlineKeyboardButton(text="🇩🇪 Deutsch", callback_data="de"),
    InlineKeyboardButton(text="🇫🇷 Français", callback_data="fr"),
    InlineKeyboardButton(text="🇪🇸 Español", callback_data="es"),
    InlineKeyboardButton(text="🇮🇹 Italiano", callback_data="it"),
    InlineKeyboardButton(text="🇦🇿 Azərbaycanca", callback_data="az"),
    InlineKeyboardButton(text="عربي 🇸🇦", callback_data="ar")
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

del_help = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='🔻', callback_data=f"bekor_qilish"))
