# CashFlow ID — Bot Telegram Earn-Money Jujur

Bot Telegram di mana user bisa dapat saldo dengan menonton iklan rewarded, menyelesaikan tugas, dan ajak teman, lalu **tarik dana real ke DANA / GoPay / OVO / BANK / USDT**.

> ⚠️ **Filosofi:** bot ini dibangun untuk **beneran bayar user**, bukan tipu-tipu. Differentiator vs banyak bot CashClip-style yang scam.

## Arsitektur singkat

```
bot/
├── main.py              # entrypoint (aiogram polling)
├── config.py            # settings dari env (.env / fly secrets)
├── db.py                # SQLAlchemy async + ORM models
├── texts.py             # string Indonesia
├── keyboards.py         # reply / inline keyboards
├── handlers/
│   ├── start.py         # /start + referral
│   ├── menu.py          # balance, referral, help, proof
│   ├── earn.py          # tonton iklan (mock → Adsgram di v2)
│   ├── withdraw.py      # FSM: amount → method → account → name → confirm
│   └── admin.py         # /stats /pending /user /ban /give /broadcast + approve
├── middlewares/
│   └── banned.py        # short-circuit user banned
└── services/
    ├── user_service.py
    ├── earning_service.py
    └── withdraw_service.py
```

Database: SQLite default (untuk dev), siap upgrade ke Postgres (`DATABASE_URL=postgresql+asyncpg://...`).

## Quick start (lokal)

Prereq: Python 3.11+, akun Telegram, sudah dapat token dari [@BotFather](https://t.me/BotFather).

```bash
git clone https://github.com/BagusSedana/cashflow-bot
cd cashflow-bot

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# edit .env: TELEGRAM_BOT_TOKEN, ADMIN_IDS

python -m bot.main
```

Lalu chat botmu di Telegram → kirim `/start`.

## Cara dapat Telegram Bot Token

1. Buka [@BotFather](https://t.me/BotFather)
2. `/newbot` → ikuti instruksi (nama display, lalu username yang harus berakhiran `_bot`)
3. Copy token yang dikasih (formatnya seperti `1234567890:AAEabc...`)
4. Tempel ke `TELEGRAM_BOT_TOKEN` di `.env`

## Cara dapat User ID kamu (untuk `ADMIN_IDS`)

1. Chat [@userinfobot](https://t.me/userinfobot)
2. Bot bales dengan `Id: 123456789`
3. Tempel ke `ADMIN_IDS` di `.env` (bisa multiple admin, dipisah koma)

## Konfigurasi

Semua via env. Lihat [`.env.example`](.env.example). Yang penting:

| Var | Default | Keterangan |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | wajib | dari BotFather |
| `ADMIN_IDS` | wajib | comma-separated, contoh `123,456` |
| `EARN_PER_AD` | 10 | rupiah per 1 view iklan |
| `AD_COOLDOWN_SECONDS` | 30 | jeda antar view (anti-spam) |
| `REFERRAL_PERCENT` | 5 | % komisi upline lifetime |
| `REFERRAL_SIGNUP_BONUS` | 500 | bonus saat downline daftar |
| `MIN_WITHDRAW` | 5000 | nominal minimum tarik |
| `MAX_WITHDRAW` | 500000 | per request max |
| `PAYOUT_METHODS` | `DANA,GoPay,OVO,BANK` | comma-separated |
| `PROOF_CHANNEL_USERNAME` | `""` | username channel proof of payment (tanpa @) |

> 💡 **Tips unit economics:** `EARN_PER_AD` harus < (revenue Adsgram per view × 60-70%). Kalau Adsgram bayar $0.001/view ≈ Rp 16, maka `EARN_PER_AD=10` (60%) menyisakan Rp 6 untuk operasional + profit. Jangan tergoda bayar lebih dari yang masuk akal — bot mati cepat.

## Deploy ke Fly.io (gratis tier)

```bash
# install flyctl: https://fly.io/docs/hands-on/install-flyctl/
fly auth signup        # atau fly auth login

cd cashflow-bot
fly launch --no-deploy --copy-config --name cashflow-bot-yourname

# set secrets (token & admin id)
fly secrets set \
    TELEGRAM_BOT_TOKEN="1234567890:..." \
    ADMIN_IDS="123456789"

fly volumes create cashflow_data --region sin --size 1
fly deploy
fly logs    # lihat log real-time
```

## Deploy ke Railway (alternatif)

1. Push repo ke GitHub
2. Buka [railway.app](https://railway.app) → "New Project" → "Deploy from GitHub" → pilih repo ini
3. Settings → Variables: tambahkan `TELEGRAM_BOT_TOKEN`, `ADMIN_IDS`, dst.
4. Settings → Volume: mount ke `/app/data` (untuk SQLite persistence)

## Roadmap

**v0.1 (MVP — current)** ✅
- /start dengan deep-link referral
- Balance, referral stats, menu utama
- Tonton iklan (mock)
- Withdraw flow + admin approve/reject/paid
- Auto-post bukti pembayaran ke channel
- Admin: /stats /pending /user /ban /unban /give /broadcast

**v0.2 (Adsgram integration)**
- Telegram Mini App (HTML + Adsgram SDK)
- Server callback: hanya grant reward setelah Adsgram konfirmasi ad watched (anti spoofing)
- Pengaturan rate dynamic per region

**v0.3 (Offerwall + payout otomatis)**
- Integrasi offerwall (CPAlead, AdGate, Lootably)
- Tugas berbayar per signup/install
- Payout otomatis ke DANA/GoPay via Tripay/Xendit (butuh KYC)

**v0.4 (Anti-fraud lanjutan)**
- Device fingerprinting via Mini App
- Captcha sebelum withdraw
- KYC selfie untuk withdraw besar

## Etika

Bot ini wajib **beneran bayar**. Jika kamu fork dan jadikan scam:
- Akun Telegram bot kemungkinan besar di-banned
- Adsgram/Monetag akan men-ban publisher kamu (deteksi pola fraud)
- Bisa kena pasal 28 ayat 1 UU ITE (penipuan online)

Jadi serius — biarin yang scam-scam itu mati pelan-pelan. Yang jujur menang dalam jangka panjang.

## Lisensi

MIT
