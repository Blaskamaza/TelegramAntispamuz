# Samurai Bot - O'zbek tili (Uzbek Localization)
# Fluent format: https://projectfluent.org/

# ========== XATOLAR (ERRORS) ==========
error-no-reply = Bu buyruq javob sifatida yuborilishi kerak!
error-report-admin = Adminni shikoyat qilasizmi? Ay-ay-ay 😈
error-report-self = O'zingizni shikoyat qila olmaysiz 🤪
error-restrict-admin = Adminni cheklash mumkin emas.
error-wrong-time-format = Noto'g'ri vaqt formati. Raqam + h, m yoki d belgilaridan foydalaning. Masalan: 4h
error-message-too-short = Iltimos, ma'nosiz qisqa salomlashuvlardan saqlaning. Agar savolingiz yoki ma'lumotingiz bo'lsa, hammasini bitta xabarda yozing. Oldindan rahmat! 🤓
error-ban-admin = 😡 Bruh. Adminni ban qilish mumkin emas :/
error-checkperms-admin = ✅ Adminlarda hech qanday cheklov yo'q.
error-givemedia-admin = Adminlarga media yuborish ruxsat etilgan!
error-givestickers-admin = Adminlarga stiker yuborish ruxsat etilgan!

# ========== SHIKOYAT (REPORT) ==========
report-date-format = %d.%m.%Y soat %H:%M (server vaqti)
report-message = 🕗 Yuborildi { $date }
report-from = 
    
    👤 Shikoyat qilgan: { $reporter }
report-note = 
    
    💬 Izoh: { $note }

# ========== AMAL TUGMALARI (ACTION BUTTONS) ==========
action-go-to-message = 👀 Xabarga o'tish
action-del-msg = 🗑 Xabarni o'chirish
action-del-and-ban = 🗑 O'chirish + ❌ abadiy ban
action-del-and-readonly = 🗑 O'chirish + 🙊 kun davomida mute
action-del-and-readonly2 = 🗑 O'chirish + 🙊 hafta davomida mute
action-false-alarm = ❎ Qoidabuzarlik yo'q
action-false-alarm-2 = ❎ Qoidabuzarlik yo'q (🙊 shikoyatchini kun davomida mute)
action-false-alarm-3 = ❎ Qoidabuzarlik yo'q (🙊 shikoyatchini hafta davomida mute)
action-false-alarm-4 = ❎ Qoidabuzarlik yo'q (❌ shikoyatchini ban)

# ========== AMAL NATIJALARI (ACTION RESULTS) ==========
action-deleted = 

    🗑 <b>O'chirildi</b>
action-deleted-banned = 

    🗑❌ <b>O'chirildi, foydalanuvchi banlandi</b>
action-deleted-readonly = 

    🗑🙊 <b>O'chirildi, + kun davomida mute berildi.</b>
action-deleted-readonly2 = 

    🗑🙊 <b>O'chirildi, + hafta davomida mute berildi.</b>
action-false-alarm-done = 

    ✅ <b>Yolg'on signal qayd etildi</b>
action-false-alarm-2-done = 

    ✅ <b>Yolg'on signal qayd etildi, shikoyatchi kun davomida mutelandi</b>
action-false-alarm-3-done = 

    ✅ <b>Yolg'on signal qayd etildi, shikoyatchi hafta davomida mutelandi</b>
action-false-alarm-4-done = 

    ✅ <b>Yolg'on signal qayd etildi, shikoyatchi banlandi</b>

# ========== BAN/UNBAN ==========
ban-success = ❌ { $user } banlandi
unban-success = ✅ { $user } bandan chiqarildi
ban-reason = 
    💬 Sabab: { $reason }
ban-duration = 
    ⏰ Muddat: { $duration }
ban-forever = abadiy
ban-hours = { $hours } soat
ban-days = { $days } kun

# ========== MUT/UNMUTE ==========
readonly-success = 🙊 { $user } mutelandi
unreadonly-success = 🔊 { $user } mutdan chiqarildi
readonly-duration = 
    ⏰ Muddat: { $duration }

# ========== CHECKPERMS ==========
checkperms-title = 📋 Foydalanuvchi ruxsatlari
checkperms-send-messages = ✅ Xabar yuborish: ruxsat etilgan
checkperms-send-messages-no = ❌ Xabar yuborish: taqiqlangan
checkperms-send-media = ✅ Media yuborish: ruxsat etilgan
checkperms-send-media-no = ❌ Media yuborish: taqiqlangan
checkperms-send-stickers = ✅ Stiker yuborish: ruxsat etilgan
checkperms-send-stickers-no = ❌ Stiker yuborish: taqiqlangan

# ========== SPAM ==========
spam-detected = ⚠️ Spam aniqlandi!
spam-warning = Ogohlantirish { $count }/3
spam-first-warning = 
    
    ⚠️ <b>Spam ogohlantiruvi (1/3)</b>
    Keyingi spam xabari uchun siz avtomatik banlansiz.
spam-second-warning = 
    
    ⚠️⚠️ <b>Spam ogohlantiruvi (2/3)</b>
    Bu sizning oxirgi ogohlantirishingiz!
spam-final-warning = 
    
    ⚠️⚠️⚠️ <b>Spam ogohlantiruvi (3/3)</b>
    Navbatdagi spam xabari uchun ban olasiz.
spam-autoban = 
    
    ❌ <b>Avtomatik ban</b>
    Spam qoidabuzarliklari: { $violations }

# ========== NSFW ==========
nsfw-detected = 🔞 NSFW kontent aniqlandi
nsfw-warning = 
    
    ⚠️ <b>NSFW ogohlantirish</b>
    Iltimos, profil rasmingizni o'zgartiring.
nsfw-kick = 
    
    ❌ <b>NSFW qoidabuzarligi</b>
    Foydalanuvchi guruhdan chiqarildi.

# ========== PROFANITY ==========
profanity-detected = 🤬 So'kinish aniqlandi
profanity-warning = 
    
    ⚠️ Iltimos, odob-axloqqa rioya qiling.

# ========== FOYDALANUVCHI MA'LUMOTLARI (USER INFO) ==========
user-info = 📊 <b>Foydalanuvchi ma'lumotlari</b>

    👤 Ismi: { $name }
    🆔 ID: { $id }
    📊 Daraja: { $level }
    ⭐️ Reytingi: { $reputation }
    💬 Xabarlar soni: { $messages }
    ⚠️ Qoidabuzarliklar: { $violations }

user-info-member-since = 
    📅 A'zo bo'lgan sana: { $date }

# ========== REPUTATION ==========
reputation-increased = ⭐️ Reytingiz oshdi: +{ $points }
reputation-decreased = ⚠️ Reytingiz kamaydi: { $points }
reputation-reset = 🔄 Reyting qayta tiklandi

# ========== FORWARD VIOLATION ==========
forward-violation = 
    
    ⚠️ <b>Forward qoidabuzarligi</b>
    Siz forward yuborish uchun kam reytingga egasiz.
    Kerakli reyting: { $required }
    Sizning reytingingiz: { $current }
    
    Jarima: -{ $penalty } reyting

# ========== MEDIA RESTRICTION ==========
media-restricted = 
    
    ⚠️ <b>Media yuborish cheklangan</b>
    Siz media yuborish uchun kam reytingga egasiz.
    Kerakli reyting: { $required }
    Sizning reytingingiz: { $current }

# ========== BUYRUQLAR (COMMANDS) ==========
command-ping = 🏓 Pong! Bot ishlayapti
command-ping-detailed = 🏓 Pong!
    ⏱ Javob vaqti: { $latency }ms
    🤖 Bot versiyasi: { $version }
    
command-rules = 📜 <b>Guruh qoidalari</b>

    1. Hurmat bilan muomala qiling
    2. Spam yubormang
    3. Reklama taqiqlangan
    4. So'kinish taqiqlangan
    5. NSFW kontent taqiqlangan
    
    ⚠️ Qoidalarni buzish ban bilan yakunlanishi mumkin!

# Rules message (used by bot)
rules-message = <b>Chat qoidalari:</b>

    📈 Chatda <u>reputatsiya tizimi</u> amal qiladi
    ⛔️ Yangi a'zolarga media yuborish taqiqlangan
    🤬 So'kinish va haqoratlar taqiqlangan va <u>avtomatik o'chiriladi</u> bizning bot tomonidan
    👹 Offtop/spam/trolling 🍌 bananlar bilan jazolanadi

    <b>Hammaga tinchlik 🤞</b>

command-help = ℹ️ <b>Yordam</b>

    📋 <b>Foydalanuvchi buyruqlari:</b>
    !me - Shaxsiy ma'lumotlar
    !rules - Guruh qoidalari
    !report - Xabarni shikoyat qilish (javob sifatida)
    @admin - Adminlarni chaqirish
    
    👮 <b>Admin buyruqlari:</b>
    !ban - Foydalanuvchini banlash
    !unban - Bandan chiqarish
    !readonly - Mutelash
    !unreadonly - Mutdan chiqarish
    !checkperms - Ruxsatlarni tekshirish
    
    💬 Savollar uchun adminlarga murojaat qiling!

# ========== ADMIN CALL ==========
admin-call = 🚨 <b>Admin chaqirildi!</b>

    👤 Kim chaqirdi: { $user }
    💬 Guruh: { $chat }

# ========== BOO COMMAND ==========
boo-response = 
    😱 Вау бу нима! ---
    😨 Qo'rqib ketdim! ---
    🫣 Uf, yuraklarni to'xtatdingiz!

# ========== PROF COMMAND ==========
prof-check-clean = ✅ <b>Tekshiruv natijasi:</b> So'kinish topilmadi
prof-check-found = ❌ <b>Tekshiruv natijasi:</b> So'kinish aniqlandi!

# ========== CHATID COMMAND ==========
chatid-result = 🆔 <b>Chat ID:</b> <code>{ $chat_id }</code>

# ========== REWARD/PUNISH ==========
reward-success = ⭐️ { $user } ga +{ $points } reyting berildi
punish-success = ⚠️ { $user } dan -{ $points } reyting olindi
setlevel-success = 📊 { $user } ning darajasi { $level } ga o'zgartirildi
reputation-reset-success = 🔄 { $user } ning reytingi qayta tiklandi

# ========== LOGS ==========
log-test = 📝 <b>Test log xabari</b>

    💬 Matn: { $text }
    👤 Yuborgan: { $user }
    🕐 Vaqt: { $time }

# ========== MESSAGE BOT ==========
msg-sent = ✅ Xabar yuborildi

# ========== WELCOME ==========
welcome-message = 
    👋 <b>Xush kelibsiz, { $name }!</b>
    
    📜 Iltimos, guruh qoidalarini o'qing: !rules
    
    ℹ️ Yordam: !help

# ========== COMMON ==========
button-close = ❌ Yopish
button-cancel = ❌ Bekor qilish
button-confirm = ✅ Tasdiqlash

processing = ⏳ Qayta ishlanmoqda...
done = ✅ Bajarildi!
error = ❌ Xatolik yuz berdi
permission-denied = 🚫 Ruxsat yo'q

# ========== REPUTATION LABELS ==========
rep-label-wanted = ⭐️⭐️⭐️⭐️⭐️ qidiruv besh yulduz
rep-label-dangerous = o'ta xavfli
rep-label-shady = shubhali shaxs
rep-label-violator = qoidabuzar
rep-label-neutral = neytral
rep-label-good = yaxshi
rep-label-very-good = juda yaxshi
rep-label-generous = saxiy
rep-title = Reputatsiya

# Member levels
level-king = 👑 Qirol
level-noname = 🥷 Noma'lum
level-newbie = 🌚 Yangi
level-experienced = 😎 Tajribali
level-professional = 🤵 Professional
level-veteran = 😈 Veteran
level-master = ⭐️ Usta
level-legend = 🌟 Afsona

# Admin roles (random)
admin-roles =
    Politsiyachi
    ---
    S.W.A.T.
    ---
    FBI agenti
    ---
    Qasoskor
    ---
    Moderator
    ---
    Adolat qo'li

# Creator rep label
rep-creator = ⭐️⭐️⭐️⭐️⭐️ Qidiruv besh yulduz

# ========== ACTION RESULTS (for callbacks) ==========
action_deleted = 
    🗑 <b>O'chirildi</b>
action_deleted_banned = 
    🗑❌ <b>O'chirildi, foydalanuvchi banlandi</b>
action_deleted_readonly = 
    🗑🙊 <b>O'chirildi, + kun davomida mute berildi.</b>
action_deleted_readonly2 = 
    🗑🙊 <b>O'chirildi, + hafta davomida mute berildi.</b>
action_dismissed = 
    ❎ <b>Qoidabuzarlik topilmadi.</b>
action_deleted_dismissed2 = 
    ❎ <b>Qoidabuzarlik topilmadi (🙊 shikoyatchiga 1 kun mute berildi).</b>
action_deleted_dismissed3 = 
    ❎ <b>Qoidabuzarlik topilmadi (🙊 shikoyatchiga 7 kun mute berildi).</b>
action_deleted_dismissed4 = 
    ❎ <b>Qoidabuzarlik topilmadi (❌ shikoyatchi banlandi).</b>

# ========== FUN RESPONSES - !бу command ==========
bu-responses =
    Qo'rqib ketdim!
    ---
    Qo'rqitmang!
    ---
    Xudoyim ...
    ---
    Murakkab hisob-kitoblarni bajarayotgandim :3
    ---
    Yetadi!
    ---
    Xo'p ...
    ---
    Qo'rqib ketdim ...
    ---
    Nega unday qilasiz :3
    ---
    Qo'rqinchli, o'chiring
    ---
    Kulgili emas :3

# ========== VOICE MESSAGE RESPONSES ==========
voice-responses =
    fu! FU DEDIM, BO'LMAYDI. KAKANI QO'Y. MATN YOZING.
    ---
    Keskin harakatlarsiz! Telefonni yerga qo'ying ... va boshqa ovozli xabar yubormang :3
    ---
    Ovozli xabarlar - zamonaviy jamiyatning boshi. Xulosa chiqar, makaroshka :3
    ---
    Mening vaqtimda odamlar matn bilan yozishardi ...

# ========== BOT COMMENTS ON CHANNEL POSTS ==========
bot-comments =
    Shunday ham bo'ladi ...
    ---
    Bananlar 🍌
    ---
    Kim hozir bu yerda birinchi 😎
    ---
    Men birinchi emasman, ikkinchi emasman, bunday kishilarni banlayapin :3
    ---
    Kirgin qo'rqma, chiqsang yig'lama :3
    ---
    Muallif 1 soniya hech narsa joylamadi, aniq tushib ketdi :3
    ---
    Samurai o'z o'rnida 🫡
    ---
    Postlaymiz yashaymiz :3

# ========== REPORT RESPONSES ==========
report-responses =
    <i>Shikoyat yuborildi.</i>
    ---
    <i>Adminlar ko'rib chiqadi.</i>
    ---
    <i>Politsiya yo'lda :3</i>
    ---
    <i>SWAT allaqachon chiqdi :3</i>
    ---
    <i>Hozir kimdir qarab chiqadi :3</i>

# ========== REPORT STATUS ==========
report-under-review =
    ⚠️ <i>Xabar adminlar tomonidan tekshirilmoqda.</i>
    ---
    <b>SWAT</b> allaqachon chiqdi. <i>Xabar ko'rib chiqilmoqda.</i>
    ---
    🐸 Agar bu yerda qoidabuzarlik bo'lsa, mening qo'lim titramaydi!
    ---
    ⚠️ <i>Ushbu xabar qoidabuzarlik uchun tekshirilmoqda.</i>

report-completed =
    ✅ <i>Xabar o'chirildi, chunki chat qoidalarini buzgan.</i>
    ---
    <i>Xabar qoidabuzarlik tufayli o'chirildi.</i>
    ---
    <i>SWAT qoidabuzarni olib ketdi.</i>
    ---
    <i>NLO kelib bu xabarni o'chirib ketdi ...</i>

