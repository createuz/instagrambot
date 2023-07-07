from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.config import BOT_URL

language_keyboard = InlineKeyboardMarkup(row_width=2)
uz = InlineKeyboardButton(text="🇺🇿O'zbekcha", callback_data="uz")
en = InlineKeyboardButton(text="🇬🇧English", callback_data="en")
ru = InlineKeyboardButton(text="🇷🇺Русский", callback_data="ru")
ar = InlineKeyboardButton(text="العربية🇸🇦", callback_data="ar")
tr = InlineKeyboardButton(text="🇹🇷Türkçe", callback_data="tr")
nm = InlineKeyboardButton(text="🇩🇪Deutsch", callback_data="nm")
fr = InlineKeyboardButton(text="🇫🇷Français", callback_data="fr")
es = InlineKeyboardButton(text="🇪🇸Español", callback_data="es")
it = InlineKeyboardButton(text="🇮🇹Italiano", callback_data="it")
qz = InlineKeyboardButton(text="🇰🇿Қазақ", callback_data="qz")
hn = InlineKeyboardButton(text="🇮🇳भारतीय", callback_data="hn")
uk = InlineKeyboardButton(text="🇺🇦Український", callback_data="uk")
az = InlineKeyboardButton(text="🇦🇿Azərbaycanca", callback_data="az")

language_keyboard.add(uz)
language_keyboard.add(en, ru, tr, uk, qz, az, nm, fr, es, it, ar, hn)

keyboard_uz = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Guruhga Qushish', url=BOT_URL))
keyboard_en = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Add to group', url=BOT_URL))
keyboard_ru = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Добавить в группу', url=BOT_URL))
keyboard_ar = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text="إضافة إلى المجموعة ➕", url=BOT_URL))
keyboard_tr = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Gruba ekle', url=BOT_URL))
keyboard_nm = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Zur Gruppe hinzufügen', url=BOT_URL))
keyboard_fr = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Ajouter au groupe', url=BOT_URL))
keyboard_es = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Añadir al grupo', url=BOT_URL))
keyboard_it = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Aggiungi al gruppo', url=BOT_URL))
keyboard_hn = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ समूह में जोड़ें', url=BOT_URL))
keyboard_uk = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Додати до групи', url=BOT_URL))
keyboard_az = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Qrupa əlavə edin', url=BOT_URL))
keyboard_qz = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='➕ Топқа қосу', url=BOT_URL))

keyboard_group = {
    'Uzbek': keyboard_uz,
    'Russian': keyboard_ru,
    'Arabic': keyboard_ar,
    'Turkey': keyboard_tr,
    'Germany': keyboard_nm,
    'France': keyboard_fr,
    'Spain': keyboard_es,
    'Italy': keyboard_it,
    'English': keyboard_en,
    "Kazakh": keyboard_qz,
    "Ukraine": keyboard_uk,
    "Azerbaijan": keyboard_az,
    "Indian": keyboard_hn
}

menu = InlineKeyboardMarkup(row_width=1)
send = InlineKeyboardButton("♻️ Xabar Yuborish", callback_data="send")
stat = InlineKeyboardButton("📊 Statiska", callback_data="stat")
menu_kb = menu.add(send, stat)

menu = InlineKeyboardMarkup(row_width=1)
text = InlineKeyboardButton("📝 Text xabar yuborish", callback_data="text")
photo = InlineKeyboardButton("🖼 Photo xabar yuborish", callback_data="photo")
video = InlineKeyboardButton("🎥 Videos xabar yuborish", callback_data="video")
cancel = InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel")
admin_kb = menu.add(text, photo, video, cancel)

rek_kb2 = InlineKeyboardMarkup(row_width=1)
rek_kb3 = InlineKeyboardMarkup(row_width=1)
rek_kb4 = InlineKeyboardMarkup(row_width=1)
rek_kb5 = InlineKeyboardMarkup(row_width=1)
button_2 = rek_kb2.add(InlineKeyboardButton("📍2-Tugmani kiritish", callback_data="button_2"),
                       InlineKeyboardButton("✅ Xabarni yuborish", callback_data="send_message"),
                       InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel"))

button_3 = rek_kb3.add(InlineKeyboardButton("📍3-Tugmani kiritish", callback_data="button_3"),
                       InlineKeyboardButton("✅ Xabarni yuborish", callback_data="send_message"),
                       InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel"))

button_4 = rek_kb4.add(InlineKeyboardButton("📍4-Tugmani kiritish", callback_data="button_4"),
                       InlineKeyboardButton("✅ Xabarni yuborish", callback_data="send_message"),
                       InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel"))

button_5 = rek_kb5.add(InlineKeyboardButton("✅ Xabarni yuborish", callback_data="send_message"),
                       InlineKeyboardButton("❌ Bekor qilish ", callback_data="cancel"))

send_all = InlineKeyboardMarkup(row_width=1)
tasdiqlash = send_all.add(InlineKeyboardButton("✅ Xabarni yuborish", callback_data="send_message"),
                          InlineKeyboardButton("❌ Bekor qilish ", callback_data="cancel"))

add_new_btn = InlineKeyboardMarkup(row_width=1)
add_btn = add_new_btn.add(InlineKeyboardButton("📍Tugma yaratish", callback_data="add_btn"),
                          InlineKeyboardButton("✅ Xabarni yuborish", callback_data="send_message"),
                          InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel"))
