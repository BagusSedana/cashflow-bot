"""Indonesian-language strings used across the bot."""
from __future__ import annotations

from .config import settings


def fmt_rp(amount: int) -> str:
    """Format integer rupiah dengan separator titik. 12345 -> 'Rp 12.345'."""
    return f"Rp {amount:,}".replace(",", ".")


def welcome(first_name: str | None) -> str:
    nama = first_name or "Sobat Cuan"
    brand = settings.brand_name
    return (
        f"👋 Halo, {nama}!\n\n"
        f"Selamat datang di <b>{brand}</b> — bot earn-money yang <b>jujur & beneran bayar</b>.\n\n"
        f"💰 Cara dapat saldo:\n"
        f"  • Tonton iklan singkat ({fmt_rp(settings.earn_per_ad)} per iklan)\n"
        f"  • Selesaikan tugas/offer\n"
        f"  • Ajak teman (bonus {fmt_rp(settings.referral_signup_bonus)} per teman + "
        f"{settings.referral_percent}% earning teman seumur hidup)\n\n"
        f"💸 Tarik dana mulai dari <b>{fmt_rp(settings.min_withdraw)}</b> "
        f"ke {', '.join(settings.payout_methods)}.\n\n"
        f"Pilih menu di bawah untuk mulai 👇"
    )


MENU_BUTTON_EARN = "🎬 Tonton Iklan"
MENU_BUTTON_DAILY = "🎁 Bonus Harian"
MENU_BUTTON_TASKS = "📋 Tugas Berbayar"
MENU_BUTTON_BALANCE = "💰 Saldo Saya"
MENU_BUTTON_REFERRAL = "👥 Ajak Teman"
MENU_BUTTON_WITHDRAW = "💸 Tarik Dana"
MENU_BUTTON_HELP = "ℹ️ Bantuan"
MENU_BUTTON_PROOF = "📢 Bukti Pembayaran"

BTN_BACK = "⬅️ Kembali"
BTN_CANCEL = "❌ Batal"
BTN_CONFIRM = "✅ Konfirmasi"


def balance_view(user) -> str:  # noqa: ANN001
    return (
        "💰 <b>Saldo Saya</b>\n\n"
        f"Saldo aktif : <b>{fmt_rp(user.balance)}</b>\n"
        f"Total earned: {fmt_rp(user.total_earned)}\n"
        f"Total ditarik: {fmt_rp(user.total_withdrawn)}\n"
        f"Iklan ditonton: {user.ads_watched}\n\n"
        f"Minimum tarik: <b>{fmt_rp(settings.min_withdraw)}</b>"
    )


def referral_view(user, bot_username: str, ref_count: int, ref_earnings: int) -> str:  # noqa: ANN001
    link = f"https://t.me/{bot_username}?start=ref_{user.telegram_id}"
    return (
        "👥 <b>Program Referral</b>\n\n"
        f"Link kamu:\n<code>{link}</code>\n\n"
        f"📊 <b>Statistik:</b>\n"
        f"  • Teman terdaftar: <b>{ref_count}</b>\n"
        f"  • Total bonus referral: <b>{fmt_rp(ref_earnings)}</b>\n\n"
        f"💡 <b>Cara kerja:</b>\n"
        f"  • Setiap teman daftar lewat link kamu → kamu dapat "
        f"<b>{fmt_rp(settings.referral_signup_bonus)}</b>\n"
        f"  • Plus, kamu dapat <b>{settings.referral_percent}%</b> dari setiap earning "
        f"teman tersebut, seumur hidup.\n\n"
        f"⚠️ Mengajak teman <b>tidak wajib</b> untuk tarik dana. "
        f"Cuma bonus tambahan."
    )


def help_text() -> str:
    return (
        "ℹ️ <b>Bantuan & FAQ</b>\n\n"
        "<b>Q: Apakah bot ini beneran bayar?</b>\n"
        f"A: Ya. Lihat channel bukti pembayaran kami untuk transparansi.\n\n"
        "<b>Q: Berapa lama tarik dana cair?</b>\n"
        "A: Maksimum 1×24 jam setelah disetujui admin (manual review).\n\n"
        "<b>Q: Kenapa saldo saya tidak bertambah saat nonton iklan?</b>\n"
        f"A: Ada cooldown {settings.ad_cooldown_seconds} detik antar iklan untuk anti-spam. "
        f"Tunggu sebentar lalu coba lagi.\n\n"
        "<b>Q: Apakah saya wajib mengajak teman untuk tarik dana?</b>\n"
        "A: <b>Tidak.</b> Referral hanya bonus tambahan.\n\n"
        "<b>Q: Berapa minimum tarik dana?</b>\n"
        f"A: {fmt_rp(settings.min_withdraw)}.\n\n"
        "<b>Q: Saya menemukan bug atau pertanyaan lain?</b>\n"
        "A: Hubungi admin via tombol di bawah."
    )


AD_COOLDOWN_NOT_READY = (
    "⏳ Tunggu sebentar ya. Kamu bisa nonton iklan lagi dalam {seconds} detik."
)

AD_REWARD_GRANTED = (
    "🎉 <b>Selamat!</b>\n\n"
    "Saldo kamu bertambah <b>{amount}</b> dari menonton iklan.\n"
    "Saldo sekarang: <b>{balance}</b>\n\n"
    "Lanjut nonton iklan lagi?"
)

WITHDRAW_TOO_LOW = (
    "❌ Saldo kamu belum cukup untuk tarik dana.\n\n"
    "Minimum: <b>{min_amount}</b>\n"
    "Saldo kamu: <b>{balance}</b>"
)

WITHDRAW_ASK_AMOUNT = (
    "💸 <b>Tarik Dana</b>\n\n"
    "Saldo kamu: <b>{balance}</b>\n"
    "Min: {min_amount} • Max per request: {max_amount}\n\n"
    "Ketik nominal yang ingin ditarik (angka saja, contoh: <code>10000</code>)"
)

WITHDRAW_ASK_METHOD = "Pilih metode pembayaran:"

WITHDRAW_ASK_ACCOUNT = (
    "Masukkan nomor {method}\n"
    "Contoh:\n"
    "  • DANA/GoPay/OVO: nomor HP terdaftar (08xxxxxxxxxx)\n"
    "  • BANK: nama bank + no rek (BCA 1234567890)"
)

WITHDRAW_ASK_NAME = "Masukkan nama pemilik akun (sesuai akun {method}):"

WITHDRAW_CONFIRM = (
    "📝 <b>Konfirmasi Tarik Dana</b>\n\n"
    "Nominal     : <b>{amount}</b>\n"
    "Metode      : {method}\n"
    "Nomor       : <code>{account_number}</code>\n"
    "Atas nama   : {account_name}\n\n"
    "Pastikan data benar. Setelah konfirmasi, request akan dikirim ke admin."
)

WITHDRAW_SUBMITTED = (
    "✅ Request tarik dana <b>#{wid}</b> telah dikirim ke admin.\n\n"
    "Saldo kamu sudah dipotong <b>{amount}</b>.\n"
    "Status bisa kamu cek di menu Saldo. Estimasi proses: 1×24 jam."
)

WITHDRAW_INVALID_AMOUNT = (
    "❌ Nominal tidak valid. Ketik angka saja (contoh: <code>10000</code>) "
    "atau ketik /cancel untuk batal."
)

WITHDRAW_CANCELLED = "Permintaan tarik dana dibatalkan."

WITHDRAW_NOTIFY_USER_APPROVED = (
    "🎉 Request tarik dana <b>#{wid}</b> kamu sebesar <b>{amount}</b> "
    "telah <b>disetujui</b> dan sedang diproses!"
)

WITHDRAW_NOTIFY_USER_PAID = (
    "💸 Tarik dana <b>#{wid}</b> sebesar <b>{amount}</b> via {method} "
    "ke {account_number} a.n. {account_name} <b>SUDAH DIBAYARKAN</b>!\n\n"
    "Terima kasih sudah pakai bot kami. Cek channel bukti pembayaran 🔥"
)

WITHDRAW_NOTIFY_USER_REJECTED = (
    "❌ Request tarik dana <b>#{wid}</b> kamu <b>ditolak</b>.\n\n"
    "Alasan: {reason}\n\n"
    "Saldo telah dikembalikan ke akun kamu."
)

REFERRAL_SIGNUP_NOTIFY = (
    "🎉 Teman kamu <b>{name}</b> baru saja daftar lewat link referral kamu!\n"
    "Bonus signup: <b>{bonus}</b> ditambahkan ke saldo."
)

REFERRAL_EARNING_NOTIFY = (
    "💰 Downline kamu <b>{name}</b> baru earn — kamu dapat komisi <b>{amount}</b>!"
)

BANNED_NOTICE = (
    "🚫 Akun kamu telah dinonaktifkan karena mencurigai melanggar aturan bot. "
    "Hubungi admin jika ini kekeliruan."
)
