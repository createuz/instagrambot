from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from settings.configration import config

START_GROUP = config.START_GROUP

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
    'Uzbek': InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Guruhga Qushish', url=START_GROUP)),
    'Russian': InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Добавить в группу', url=START_GROUP)),
    'Arabic': InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text="إضافة إلى المجموعة ➕", url=START_GROUP)),
    'Turkey': InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Gruba ekle', url=START_GROUP)),
    'Germany': InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text='➕ Zur Gruppe hinzufügen', url=START_GROUP)),
    'France': InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Ajouter au groupe', url=START_GROUP)),
    'Spain': InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Añadir al grupo', url=START_GROUP)),
    'Italy': InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Aggiungi al gruppo', url=START_GROUP)),
    'English': InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Add to group', url=START_GROUP)),
    "Kazakh": InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Топқа қосу', url=START_GROUP)),
    "Ukraine": InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Додати до групи', url=START_GROUP)),
    "Azerbaijan": InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text='➕ Qrupa əlavə edin', url=START_GROUP))
}

del_help = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='🔻', callback_data=f"bekor_qilish"))
