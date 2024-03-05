choose_button = "🌐 Choose language"

languages = {
    "uz": "Uzbek",
    "en": "English",
    "ru": "Russian",
    "ar": "Arabic",
    "tr": "Turkey",
    "qz": "Kazakh",
    "nm": "Germany",
    "fr": "France",
    "es": "Spain",
    "it": "Italy",
    "uk": "Ukraine",
    "az": "Azerbaijan",
}
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
    'Ukraine': "🇺🇦 Ukraine ",
    'Azerbaijan': "🇦🇿 Azerbaijan ",
}
start_uz = """
    Salom! Ushbu bot yordamida siz Instagram'dan Photo, Reels, Stories va IGTV-larni tez va sifatli formatda yuklab olishingiz mumkin.\n\n
    Yuklab olmoqchi bo'lgan video havolasini ushbu botga yuboring!\n\n
    Bot to‘g‘ridan-to‘g‘ri chatlarda ham ishlaydi!\n
    Botni guruhga qo‘shing va xabar yuborish uchun ruxsat bering,\n
    so'ngra video havolasini yuboring va bot videoni chatga yuboradi.
"""

help_uz = """
    Botdan foydalanish ko'rsatmalari bilan tanishish uchun quyidagi buyruqlardan foydalanishingiz mumkin:\n\n
    /start - Botni ishga tushirish uchun ushbu buyruqdan foydalaning.\n\n
    /help - Botdan foydalanish ko'rsatmalari va buyruqlari haqida ma'lumot olish uchun ushbu buyruqdan foydalaning.\n\n
    /lang - Botning tilini o'zgartirish uchun ushbu buyruqdan foydalaning.\n\n
    O'zingiz xohlagan media bilan bog'liq havolani yuborish orqali bot avtomatik ravishda uni siz uchun yuklab olishni amalga oshiradi. 
    Botda to‘g‘ridan-to‘g‘ri chatlarda ham ishlash imkoniyati mavjud.\n\n
    Iltimos, agar bot bilan bog'liq biror xato va kamchilikga duch kelsangiz yoki qo‘shimcha fikr va takliflaringiz bo‘lsa, 
    quyidagi manzillar orqali biz bilan bog‘laning @Tmcode\n
    Sizning fikringiz biz uchun muhim.
"""

langs_text = {
    'Uzbek': {
        'start': start_uz,
        'help': help_uz,
        'waiting': 'Yuklanmoqda, biroz kuting...',
        'saved': 'yuklab olindi',
        'error': "🛑 <b>Yuklab olishda xato!</b>\n\n<a href='{}'><b>Ushbu media faylni </b></a> yuklab olib bo'lmadi.\nIltimos keyinroq qayta urinib ko'ring."

    },
    'Russian': {
        'start': 'start_ru',
        'help': 'help_ru',
        'waiting': 'Загрузка, пожалуйста подождите...',
        'saved': 'загружен',
        'error': "🛑 <b>Ошибка при загрузке!</b>\n\n<a href='{}'><b>Этот медиа файл </b></a> не может быть загружен. \nПожалуйста, попробуйте позже."

    },
    'English': {
        'start': 'start_en',
        'help': 'help_en',
        'waiting': 'Loading, please wait...',
        'saved': 'downloaded',
        'error': "🛑 <b>Download error!</b>\n\n<a href='{}'><b>This media file </b></a> couldn't be downloaded. \nPlease try again later."

    },
    'Turkey': {
        'start': 'start_tr',
        'help': 'help_tr',
        'waiting': 'Yükleniyor lütfen bekleyin...',
        'saved': 'İndirildi',
        'error': "🛑 <b>İndirme hatası!</b>\n\n<a href='{}'><b>Bu medya dosyası </b></a> indirilemiyor. \nLütfen daha sonra tekrar deneyin."
    },
    'Ukraine': {
        'start': 'start_uk',
        'help': 'help_uk',
        'waiting': 'Завантаження, будь ласка, зачекайте...',
        'saved': 'завантажено',
        'error': "🛑 <b>Помилка завантаження!</b>\n\n<a href='{}'><b>Цей медіа файл </b></a> не може бути завантажено. \nБудь ласка, спробуйте пізніше."
    },
    'Kazakh': {
        'start': 'start_kz',
        'help': 'help_kz',
        'waiting': 'Жүктелуде, күте тұрыңыз...',
        'saved': 'жүктелді',
        'error': "🛑 <b>Жүктеу кезінде қате!</b>\n\n<a href='{}'><b>Бұл медиа файл </b></a> жүктелмейді. \nКейінірек көріңіз."
    },
    'Germany': {
        'start': 'start_nm',
        'help': 'help_nm',
        'waiting': 'Laden, bitte warten...',
        'saved': 'heruntergeladen',
        'error': "🛑 <b>Fehler beim Herunterladen!</b>\n\n<a href='{}'><b>Diese Mediendatei </b></a> kann nicht heruntergeladen werden. \nBitte versuchen Sie es später erneut."
    },
    'France': {
        'start': 'start_fr',
        'help': 'help_fr',
        'waiting': 'Chargement, veuillez patienter...',
        'saved': 'téléchargé',
        'error': "🛑 <b>Erreur de téléchargement!</b>\n\n<a href='{}'><b>Ce fichier multimédia </b></a> ne peut pas être téléchargé. \nVeuillez réessayer plus tard."
    },
    'Spain': {
        'start': 'start_es',
        'help': 'help_es',
        'waiting': 'Cargando por favor espere...',
        'saved': 'descargado',
        'error': "🛑 <b>Error al descargar!</b>\n\n<a href='{}'><b>Este archivo multimedia </b></a> no se puede descargar. \nPor favor, inténtelo más tarde."
    },
    'Italy': {
        'start': 'start_it',
        'help': 'help_it',
        'waiting': 'Attendere il caricamento prego...',
        'saved': 'scaricato',
        'error': "🛑 <b>Errore durante il download!</b>\n\n<a href='{}'><b>Questa file multimediale </b></a> non può essere scaricata. \nRiprova più tardi."
    },
    'Azerbaijan': {
        'start': 'start_az',
        'help': 'help_az',
        'waiting': 'Yüklənir Zəhmət olmasa gözləyin...',
        'saved': 'endirilib',
        'error': "🛑 <b>Yükləmə xətası!</b>\n\n<a href='{}'><b>Bu media faylı </b></a> yüklənə bilmir. \nXahiş edirəm daha sonra cəhd edin."
    },
    'Arabic': {
        'start': 'start_ar',
        'help': 'help_ar',
        'waiting': 'جاري التحميل الرجاءالانتظار...',
        'saved': 'تم تنزيله',
        'error': "🛑 <b>خطأ أثناء التحميل!</b>\n\n<a href='{}'><b>هذا الملف الإعلامي </b></a> لا يمكن تحميله. \nالرجاء المحاولة لاحقًا."
    }
}
