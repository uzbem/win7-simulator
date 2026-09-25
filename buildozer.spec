[app]

# Ilova nomi va paket identifikatori
title = Windows7 Mobile Simulator
package.name = win7simulator
package.domain = org.win7sim

# Manba kodi joylashgan papka va kiritiladigan fayl kengaytmalari
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,txt

# Asosiy versiya
version = 1.0.0

# Zaruriy Python kutubxonalari (Kivy asosiy karkas)
requirements = python3,kivy==2.3.0,plyer

# Android ruxsatnomalari - fayl tizimiga kirish uchun (Fayl Menejeri,
# Bloknot va Media Player fayllar bilan ishlashi uchun zarur)
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# Ekran orientatsiyasi: "sensor" - foydalanuvchi tutgan holatiga qarab
# portrait va landscape o'rtasida avtomatik almashadi (talab #1 ga mos)
orientation = sensor

# Ilova to'liq ekranli rejimda emas (status bar ko'rinib tursin)
fullscreen = 0

# Ikon va splash-ekran (agar mavjud bo'lsa, quyidagi fayllarga yo'l bering)
# icon.filename = %(source.dir)s/data/icon.png
# presplash.filename = %(source.dir)s/data/presplash.png

# Minimal va maqsadli Android API darajalari
android.minapi = 21
android.api = 33
android.ndk = 25b

# 64-bit va 32-bit arxitekturalar uchun qurish (kengroq qurilma qamrovi)
android.archs = arm64-v8a, armeabi-v7a

# Android manifestiga qo'shimcha - orqaga qaytish tugmasini ilova
# ichida boshqarish uchun (ixtiyoriy, kerak bo'lsa yoqiladi)
# android.add_activities = 

[buildozer]

# Log darajasi: 2 - batafsil (debug uchun qulay)
log_level = 2

# Root huquqisiz build (tavsiya etiladi)
warn_on_root = 1
