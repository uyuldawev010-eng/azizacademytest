# Oylik imtihon Telegram bot

Bu loyiha `aiogram 3` va `SQLite` asosida yozilgan.

## Imkoniyatlar

- `/start` dan keyin menyu:
  - **Oylik imtihon**
  - **Natijalar**
  - **Guruh yaratish** (faqat admin)
- Admin:
  - filial tanlaydi
  - fan tanlaydi
  - guruh raqamini yozadi
  - guruh saqlanadi
- Foydalanuvchi:
  - filial -> fan -> daraja -> blok (`1-4`, `5-8`, `9-12`) -> guruh tanlaydi
  - ism-familya yozadi
  - test boshlanadi
- Test:
  - 30 minut
  - vaqt tugasa avtomatik yakunlanadi
  - natija bazaga saqlanadi
- Natijalar:
  - filial -> fan -> guruh tanlanadi
  - o'sha guruhdagi test ishlagan o'quvchilar ro'yxati chiqadi
  - o'quvchini bosganda natijasi va javoblari ko'rinadi

## Tuzilma

- `app/bot.py` — asosiy bot kodi
- `app/db.py` — SQLite bazasi
- `app/config.py` — sozlamalar
- `app/keyboards.py` — tugmalar
- `app/exam_service.py` — test yordamchi funksiyalari
- `data/questions.json` — savollar bazasi

## Ishga tushirish

### 1) Virtual environment

**Windows PowerShell:**

```powershell
python -m venv venv
venv\Scripts\activate
```

### 2) Kutubxonalar

```powershell
pip install -r requirements.txt
```

### 3) `.env` fayl oching

`.env.example` dan nusxa oling va `.env` nomi bilan saqlang:

```env
BOT_TOKEN=BOTFATHER_DAN_OLGAN_TOKEN
ADMIN_IDS=1999009002,123456789
```

> `ADMIN_IDS` ga vergul bilan admin user id larni yozing.

### 4) Botni ishga tushirish

```powershell
python -m app.bot
```

## Savollarni o'zgartirish

`data/questions.json` faylda savollar quyidagi tuzilishda bo'ladi:

```json
{
  "English": {
    "Beginner": {
      "1-4": [
        {
          "question": "Savol matni",
          "options": ["A", "B", "C", "D"],
          "correct_index": 1
        }
      ]
    }
  }
}
```

- `correct_index` 0 dan boshlanadi
- masalan `1` bo'lsa, to'g'ri javob `options[1]`

## Eslatma

Hozir namunaviy savollar qo'shib berilgan:
- English
- Rus tili
- Matematika

Qolgan fanlar uchun ham shu formatda savollarni davom ettirasiz.


## Muhim eslatma
Agar `Unauthorized` xatosi chiqsa, bu kod xatosi emas. Bu `BOT_TOKEN` noto'g'ri yoki eski ekanini bildiradi.

Eng oson yo'l:
1. `setup_env.bat` ni ishga tushiring
2. Yangi BotFather tokenini kiriting
3. `start_bot.bat` ni ishga tushiring


## Kimyo bo‘limi
- Endi `Kimyo` fanida `Kimyo 1` va `Kimyo 2` tanlovi chiqadi.
- `Kimyo 1` tanlanganda guruh tanlanadi va test boshlanadi.
- `Kimyo 2` uchun hozircha savollar bo‘sh qoldirilgan.


Qo'shilgan fanlar: Kimyo, Huquq, Tarix. Tarix va Huquq fanlari guruh tanlangach to'g'ridan-to'g'ri testni ochadi.


## Biologiya bo‘limi
- Endi `Biologiya` fanida `Biologiya 1` va `Biologiya 2` tanlovi chiqadi.
- `Biologiya 1` tanlanganda guruh tanlanadi va test boshlanadi.
- `Biologiya 2` hozircha bo‘sh qoldirilgan.


Qo'shimcha: English fanida endi darajalar orasida Starter ham bor. Beginner tanlanganda Beginner 1, Beginner 2, Beginner 3 bo'limlari chiqadi.

Qo'shilgan fanlar: Kimyo, Huquq, Tarix, Biologiya, Hamshiralik.
Hamshiralik ichida 1-yordam / Anatomiya / Kasalliklar bo'limlari bor.

Qo'shilgan yangi fan: IT (HTML&CSS 1, HTML&CSS 2, JAVASCRIPT 1, JAVASCRIPT 2).
