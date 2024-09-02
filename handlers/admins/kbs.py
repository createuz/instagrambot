from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_inline_button(text, callback_data):
    return InlineKeyboardButton(text=text, callback_data=callback_data)


bekor_qilish_kb = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text="🔻", callback_data="bekor_qilish"))
del_help = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='🔻', callback_data=f"bekor_qilish"))
back_media_statistic = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton(text="⬅ Back", callback_data="statistic"))

menu_kb = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton(text="💬 Send Message", callback_data="send_all_msg"),
    InlineKeyboardButton(text="📊 Statistic", callback_data="statistic"),
    InlineKeyboardButton(text="🅰 Admins", callback_data="admin_menu"),
    InlineKeyboardButton(text="🏠 Home", callback_data="bekor_qilish"))

admin_menu = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton(text="📄 Admins Data", callback_data="admins_data"),
    InlineKeyboardButton(text="➕ Add Admin", callback_data="add_admin"),
    InlineKeyboardButton(text="🗑 Delete Admin", callback_data="del_admin"),
    InlineKeyboardButton(text="⬅ Back", callback_data="menu_kb"))

chose_statistic_kb = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton(text="👤 User Statistic", callback_data="user_statistic"),
    InlineKeyboardButton(text="👥 Group Statistic", callback_data="group_statistic"),
    InlineKeyboardButton(text="📄 Chat Ids", callback_data="chat_ids_doc"),
    InlineKeyboardButton(text="⬅ Back", callback_data="menu_kb"))

update_user_statistic = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton(text="🔄 Update", callback_data="update_user_statistic"),
    InlineKeyboardButton(text="⬅ Back", callback_data="statistic"))

update_user_statistic_2x = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton(text="🔄 Update", callback_data="user_statistic"),
    InlineKeyboardButton(text="⬅ Back", callback_data="statistic"))

update_group_statistic = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton(text="🔄 Update", callback_data="update_group_statistic"),
    InlineKeyboardButton(text="⬅ Back", callback_data="statistic"))

update_group_statistic_2x = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton(text="🔄 Update", callback_data="group_statistic"),
    InlineKeyboardButton(text="⬅ Back", callback_data="statistic"))

send_message_kb = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton(text="📝 Send Message", callback_data="text"),
    InlineKeyboardButton(text="🖼 Send Photo", callback_data="photo"),
    InlineKeyboardButton(text="📹 Send Video", callback_data="video"),
    InlineKeyboardButton(text="🗑 Cancel", callback_data="bekor_qilish"),
    InlineKeyboardButton(text="⬅ Back", callback_data="menu_kb"))

kb_2 = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton(text="📍2-Tugmani kiritish", callback_data="kb_2"),
    InlineKeyboardButton(text="✅ Xabarni yuborish", callback_data="send_message"),
    InlineKeyboardButton(text="🗑 Bekor qilish", callback_data="cancel"))

kb_3 = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton(text="📍3-Tugmani kiritish", callback_data="kb_3"),
    InlineKeyboardButton(text="✅ Xabarni yuborish", callback_data="send_message"),
    InlineKeyboardButton(text="🗑 Bekor qilish", callback_data="cancel"))

kb_4 = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton(text="📍4-Tugmani kiritish", callback_data="kb_4"),
    InlineKeyboardButton(text="✅ Xabarni yuborish", callback_data="send_message"),
    InlineKeyboardButton(text="🗑 Bekor qilish", callback_data="cancel"))

kb_5 = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="send_message"),
    InlineKeyboardButton(text="🗑 Bekor qilish ", callback_data="cancel"))

tasdiqlash = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="send_message"),
    InlineKeyboardButton(text="🗑 Bekor qilish ", callback_data="cancel"))

add_kb = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton(text="📍Tugma yaratish", callback_data="add_kb"),
    InlineKeyboardButton(text="✅ Xabarni yuborish", callback_data="send_message"),
    InlineKeyboardButton(text="🗑 Bekor qilish ", callback_data="cancel"))
