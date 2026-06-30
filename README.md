# uzbekistan-regions-districts-all

tumanlar.json faylida O'zbekistonning barcha viloyatlari va 29.06.2026 holatiga ko'ra barcha tumanlari keltirilgan. Har bir viloyat va tuman uchun mos ravishda koordinatalar (latitude, longitude) ham ko'rsatilgan. Ma'lumotlar ochiq manbalar, maxsus skriptlar va AI vositalari yordamida yig'ilgan va tahlil qilingan holda tuzilgan (avtomatlashtirilgan tizimlar yordamida tekshirilgan), shu sababli koordinatalar haqiqiy joylashuvdan biroz farq qilishi mumkin.

# 1 - tekshiruv usuli.

python3 check_coords.py tumanlar.json # => Bu komanda orqali terminalda turib joylashuvlar haqiqiyligini tekshirishingiz mumkin, ammo ba'zi viloyat tuman nomlarini python kutubxonasi noto'g'ri talqin qilgani bois xato joylashuv deyishi mumkin, bunday holatda 2 - tekshiruv usuli qo'llanilishi keladi.

2 - tekshiruv usuli.

xarita_tekshiruv.html # => Shu faylni editorial ishga tushirish yoki brauzer yordamida ochish orqali keltirilgan nuqtalarni koʻz bilan ko'rishingiz, hamda, xato joylarni bayroqchalar (flags) bilan belgilab, oxirida .csv fayliga saqlab olishingiz mumkin.
