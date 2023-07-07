from aiogram.dispatcher.filters.state import State, StatesGroup


class InstaUserData(StatesGroup):
    waiting_user_data = State()


class LanguageSelection(StatesGroup):
    select_language = State()


class LanguageChange(StatesGroup):
    select_language = State()


class AddAdmin(StatesGroup):
    waiting_for_chat_id = State()


class Channelstate(StatesGroup):
    send_all_1 = State()
    send_all_2 = State()
    send_all_3 = State()
    send_all_4 = State()


class SendText(StatesGroup):
    text = State()
    tasdiqlash = State()
    send_all_1 = State()
    send_all_2 = State()
    send_all_3 = State()
    send_all_4 = State()
    next_call_2 = State()
    next_call_3 = State()
    next_call_4 = State()
    next_call_5 = State()

    waiting_for_is_not_btn = State()
    waiting_for_new_btn = State()
    waiting_for_caption = State()
    waiting_for_button_name_1 = State()
    waiting_for_button_name_2 = State()
    waiting_for_button_name_3 = State()
    waiting_for_button_name_4 = State()
    waiting_for_button_url_1 = State()
    waiting_for_button_url_2 = State()
    waiting_for_button_url_3 = State()
    waiting_for_button_url_4 = State()


class SendPhoto(StatesGroup):
    photo = State()
    tasdiqlash = State()
    send_all_1 = State()
    send_all_2 = State()
    send_all_3 = State()
    send_all_4 = State()
    next_call_2 = State()
    next_call_3 = State()
    next_call_4 = State()
    next_call_5 = State()

    waiting_for_is_not_btn = State()
    waiting_for_new_btn = State()
    waiting_for_caption = State()
    waiting_for_button_name_1 = State()
    waiting_for_button_name_2 = State()
    waiting_for_button_name_3 = State()
    waiting_for_button_name_4 = State()
    waiting_for_button_url_1 = State()
    waiting_for_button_url_2 = State()
    waiting_for_button_url_3 = State()
    waiting_for_button_url_4 = State()


class SendVideo(StatesGroup):
    video = State()
    tasdiqlash = State()
    send_all_1 = State()
    send_all_2 = State()
    send_all_3 = State()
    send_all_4 = State()
    next_call_2 = State()
    next_call_3 = State()
    next_call_4 = State()
    next_call_5 = State()

    waiting_for_is_not_btn = State()
    waiting_for_new_btn = State()
    waiting_for_caption = State()
    waiting_for_button_name_1 = State()
    waiting_for_button_name_2 = State()
    waiting_for_button_name_3 = State()
    waiting_for_button_name_4 = State()
    waiting_for_button_url_1 = State()
    waiting_for_button_url_2 = State()
    waiting_for_button_url_3 = State()
    waiting_for_button_url_4 = State()
