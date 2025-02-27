from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

cancel = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔻", callback_data="cancel")]
    ]
)
def get_language_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="uz"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="ru"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="en")
            ],
            [
                InlineKeyboardButton(text="🇹🇷 Türkçe", callback_data="tr"),
                InlineKeyboardButton(text="🇰🇿 Қазақ", callback_data="kz"),
                InlineKeyboardButton(text="🇺🇦 Українська", callback_data="uk")
            ],
            [
                InlineKeyboardButton(text="🇦🇿 Azərbaycan", callback_data="az"),
                InlineKeyboardButton(text="🇪🇸 Español", callback_data="es"),
                InlineKeyboardButton(text="🇫🇷 Français", callback_data="fr")
            ],
            [
                InlineKeyboardButton(text="🇩🇪 Deutsch", callback_data="de"),
                InlineKeyboardButton(text="🇵🇹 Português", callback_data="pt"),
                InlineKeyboardButton(text="🇵🇱 Polski", callback_data="pl")
            ],
            [
                InlineKeyboardButton(text="🇸🇦 عربي", callback_data="ar"),
                InlineKeyboardButton(text="🇮🇷 فارسی", callback_data="ir"),
                InlineKeyboardButton(text="🇨🇳 中文", callback_data="cn"),
            ]
            ,
            [
                InlineKeyboardButton(text="🔻", callback_data="cancel")
            ]
        ]
    )


def get_language_keyboard_code():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 UZ", callback_data="uz"),
                InlineKeyboardButton(text="🇷🇺 RU", callback_data="ru"),
                InlineKeyboardButton(text="🇬🇧 EN", callback_data="en"),
                InlineKeyboardButton(text="🇹🇷 TR", callback_data="tr")
            ],
            [
                InlineKeyboardButton(text="🇰🇿 KZ", callback_data="kz"),
                InlineKeyboardButton(text="🇺🇦 UA", callback_data="uk"),
                InlineKeyboardButton(text="🇦🇿 AZ", callback_data="az"),
                InlineKeyboardButton(text="🇪🇸 ES", callback_data="es")
            ],
            [
                InlineKeyboardButton(text="🇫🇷 FR", callback_data="fr"),
                InlineKeyboardButton(text="🇩🇪 DE", callback_data="de"),
                InlineKeyboardButton(text="🇵🇹 PT", callback_data="pt"),
                InlineKeyboardButton(text="🇵🇱 PL", callback_data="pl")
            ],
            [
                InlineKeyboardButton(text="🇸🇦 AR", callback_data="ar"),
                InlineKeyboardButton(text="🇮🇷 FA", callback_data="ir"),
                InlineKeyboardButton(text="🇨🇳 CN", callback_data="cn")
            ],
            [
                InlineKeyboardButton(text="🔻", callback_data="cancel")
            ]
        ]
    )


def get_add_to_group():
    return {
        'Uzbek': InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(text="Guruhga Qushish", url='https://t.me/instavsbot?startgroup=true')

                ],
            ]
        ),
        'English': InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(text="Add to Group", url='https://t.me/instavsbot?startgroup=true')
                ],
            ]
        ),
        'Russian': InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(text="Добавить в группу", url='https://t.me/instavsbot?startgroup=true')
                ],
            ]
        ),
        'Turkish': InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(text="Gruba Ekle", url='https://t.me/instavsbot?startgroup=true')
                ],
            ]
        ),
        'Kazakh': InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(text="Топқа қосу", url='https://t.me/instavsbot?startgroup=true')
                ],
            ]
        ),
        'Ukrainian': InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(text="Додати в групу", url='https://t.me/instavsbot?startgroup=true')
                ],
            ]
        ),
        'Azerbaijani': InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(text="Qrupa əlavə et", url='https://t.me/instavsbot?startgroup=true')
                ],
            ]
        ),
        'Spanish': InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(text="Agregar al grupo", url='https://t.me/instavsbot?startgroup=true')
                ],
            ]
        ),
        'French': InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(text="Ajouter au groupe", url='https://t.me/instavsbot?startgroup=true')
                ],
            ]
        ),
        'German': InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(text="Zur Gruppe hinzufügen",
                                         url='https://t.me/instavsbot?startgroup=true')
                ],
            ]
        ),
        'Portuguese': InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(text="Adicionar ao grupo", url='https://t.me/instavsbot?startgroup=true')
                ],
            ]
        ),
        'Polish': InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(text="Dodaj do grupy", url='https://t.me/instavsbot?startgroup=true')
                ],
            ]
        ),
        'Chinese': InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(text="添加到群组", url='https://t.me/instavsbot?startgroup=true')
                ],
            ]
        ),
        'Arabic': InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(text="إضافة إلى المجموعة", url='https://t.me/instavsbot?startgroup=true')
                ],
            ]
        ),
        'Persian': InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(text="گروه اضافه کن", url='https://t.me/instavsbot?startgroup=true')
                ],
            ]
        ),
    }
