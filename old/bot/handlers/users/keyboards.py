from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

cancel = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="🔻", callback_data="cancel")]]
)


def get_language_keyboard():
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang:uz"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
            ],
            [
                InlineKeyboardButton(text="🇹🇷 Türkçe", callback_data="lang:tr"),
                InlineKeyboardButton(text="🇰🇿 Қазақ", callback_data="lang:kz"),
                InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang:uk"),
            ],
            [
                InlineKeyboardButton(text="🇦🇿 Azərbaycan", callback_data="lang:az"),
                InlineKeyboardButton(text="🇪🇸 Español", callback_data="lang:es"),
                InlineKeyboardButton(text="🇫🇷 Français", callback_data="lang:fr"),
            ],
            [
                InlineKeyboardButton(text="🇩🇪 Deutsch", callback_data="lang:de"),
                InlineKeyboardButton(text="🇵🇹 Português", callback_data="lang:pt"),
                InlineKeyboardButton(text="🇵🇱 Polski", callback_data="lang:pl"),
            ],
            [
                InlineKeyboardButton(text="🇸🇦 العربية", callback_data="lang:ar"),
                InlineKeyboardButton(text="🇮🇷 فارسی", callback_data="lang:fa"),
                InlineKeyboardButton(text="🇨🇳 中文", callback_data="lang:cn"),
            ],
            [InlineKeyboardButton(text="🔻", callback_data="cancel")],
        ]
    )
    return kb


def get_language_keyboard_code():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 UZ", callback_data="uz"),
                InlineKeyboardButton(text="🇷🇺 RU", callback_data="ru"),
                InlineKeyboardButton(text="🇬🇧 EN", callback_data="en"),
                InlineKeyboardButton(text="🇹🇷 TR", callback_data="tr"),
            ],
            [
                InlineKeyboardButton(text="🇰🇿 KZ", callback_data="kz"),
                InlineKeyboardButton(text="🇺🇦 UA", callback_data="uk"),
                InlineKeyboardButton(text="🇦🇿 AZ", callback_data="az"),
                InlineKeyboardButton(text="🇪🇸 ES", callback_data="es"),
            ],
            [
                InlineKeyboardButton(text="🇫🇷 FR", callback_data="fr"),
                InlineKeyboardButton(text="🇩🇪 DE", callback_data="de"),
                InlineKeyboardButton(text="🇵🇹 PT", callback_data="pt"),
                InlineKeyboardButton(text="🇵🇱 PL", callback_data="pl"),
            ],
            [
                InlineKeyboardButton(text="🇸🇦 AR", callback_data="ar"),
                InlineKeyboardButton(text="🇮🇷 FA", callback_data="fa"),
                InlineKeyboardButton(text="🇨🇳 CN", callback_data="cn"),
            ],
            [InlineKeyboardButton(text="🔻", callback_data="cancel")],
        ]
    )


def get_add_to_group(language: str):
    data = {
        "uz": InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(
                        text="Guruhga Qushish",
                        url="https://t.me/instavsbot?startgroup=true",
                    ),
                ],
            ]
        ),
        "en": InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(
                        text="Add to Group",
                        url="https://t.me/instavsbot?startgroup=true",
                    ),
                ],
            ]
        ),
        "ru": InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(
                        text="Добавить в группу",
                        url="https://t.me/instavsbot?startgroup=true",
                    ),
                ],
            ]
        ),
        "tr": InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(
                        text="Gruba Ekle", url="https://t.me/instavsbot?startgroup=true"
                    ),
                ],
            ]
        ),
        "kz": InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(
                        text="Топқа қосу", url="https://t.me/instavsbot?startgroup=true"
                    ),
                ],
            ]
        ),
        "uk": InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(
                        text="Додати в групу",
                        url="https://t.me/instavsbot?startgroup=true",
                    ),
                ],
            ]
        ),
        "az": InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(
                        text="Qrupa əlavə et",
                        url="https://t.me/instavsbot?startgroup=true",
                    ),
                ],
            ]
        ),
        "es": InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(
                        text="Agregar al grupo",
                        url="https://t.me/instavsbot?startgroup=true",
                    ),
                ],
            ]
        ),
        "fr": InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(
                        text="Ajouter au groupe",
                        url="https://t.me/instavsbot?startgroup=true",
                    ),
                ],
            ]
        ),
        "de": InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(
                        text="Zur Gruppe hinzufügen",
                        url="https://t.me/instavsbot?startgroup=true",
                    ),
                ],
            ]
        ),
        "pt": InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(
                        text="Adicionar ao grupo",
                        url="https://t.me/instavsbot?startgroup=true",
                    ),
                ],
            ]
        ),
        "pl": InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(
                        text="Dodaj do grupy",
                        url="https://t.me/instavsbot?startgroup=true",
                    ),
                ],
            ]
        ),
        "cn": InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(
                        text="添加到群组", url="https://t.me/instavsbot?startgroup=true"
                    ),
                ],
            ]
        ),
        "ar": InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(
                        text="إضافة إلى المجموعة",
                        url="https://t.me/instavsbot?startgroup=true",
                    ),
                ],
            ]
        ),
        "fa": InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔻", callback_data="cancel"),
                    InlineKeyboardButton(
                        text="گروه اضافه کن",
                        url="https://t.me/instavsbot?startgroup=true",
                    ),
                ],
            ]
        ),
    }
    return data.get(language, "")
