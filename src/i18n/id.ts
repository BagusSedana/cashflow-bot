const id: Record<string, string> = {
  // Welcome & Help
  welcome: `🤖 *Selamat datang di AI Bot!*

Saya asisten AI dengan fitur-fitur berikut:

🧠 *Chat* — Tanya apa saja (didukung ChatGPT)
🎨 *Gambar* — Buat gambar dari teks
🔊 *Suara* — Ubah teks menjadi suara
📝 *Rangkum* — Rangkum teks panjang
🌐 *Terjemah* — Terjemahkan antar bahasa
💻 *Kode* — Analisis dan jelaskan kode

Gunakan /help untuk melihat semua perintah.`,

  help: `📋 *Perintah yang Tersedia:*

*Fitur AI:*
/ask <pertanyaan> — Tanya AI apa saja
/image <deskripsi> — Buat gambar
/voice <teks> — Ubah teks ke suara
/summarize <teks> — Rangkum teks
/translate <bahasa> <teks> — Terjemahkan teks
/code <kode> — Analisis kode

*Akun:*
/usage — Lihat statistik penggunaan
/premium — Upgrade ke premium
/language — Ganti bahasa
/clear — Hapus riwayat percakapan

*Umum:*
/start — Pesan selamat datang
/help — Tampilkan bantuan ini`,

  // Features
  ask_prompt: "💬 Apa yang ingin kamu tanyakan? Kirim pertanyaanmu.",
  ask_thinking: "🤔 Sedang berpikir...",
  image_prompt: "🎨 Deskripsikan gambar yang ingin kamu buat:",
  image_generating: "🎨 Sedang membuat gambar...",
  image_revised: "📝 *Prompt yang direvisi:* ",
  voice_prompt: "🔊 Kirim teks yang ingin kamu ubah ke suara:",
  voice_generating: "🔊 Sedang membuat suara...",
  summarize_prompt: "📝 Kirim teks yang ingin kamu rangkum:",
  summarize_processing: "📝 Sedang merangkum...",
  translate_prompt:
    "🌐 Penggunaan: /translate <bahasa> <teks>\nContoh: /translate Inggris Halo, apa kabar?",
  translate_processing: "🌐 Sedang menerjemahkan...",
  code_prompt: "💻 Kirim kode yang ingin kamu analisis:",
  code_analyzing: "💻 Sedang menganalisis kode...",

  // Limits & Premium
  limit_reached: `⚠️ *Batas harian tercapai!*

Kamu sudah menggunakan semua permintaan gratis untuk hari ini.

🌟 *Upgrade ke Premium* untuk akses tanpa batas!
Gunakan /premium untuk detail.`,

  premium_info: `🌟 *Paket Premium*

✅ Permintaan AI tanpa batas
✅ Waktu respons prioritas
✅ Generasi gambar HD
✅ Memori percakapan lebih panjang
✅ Dukungan prioritas

💰 *Harga:* $PRICE/bulan

Hubungi admin untuk upgrade!`,

  already_premium: "✅ Kamu sudah punya akses premium! Berakhir: ",

  // Usage
  usage_title: "📊 *Statistik Penggunaanmu:*",
  usage_requests_today: "Permintaan hari ini: ",
  usage_total: "Total permintaan: ",
  usage_account_type: "Tipe akun: ",
  usage_premium: "⭐ Premium",
  usage_free: "Gratis",

  // Settings
  language_changed: "✅ Bahasa diubah ke Bahasa Indonesia!",
  language_select: "🌐 Pilih bahasamu:",
  conversation_cleared: "🗑️ Riwayat percakapan dihapus!",

  // Errors
  error_generic: "❌ Terjadi kesalahan. Silakan coba lagi nanti.",
  error_banned: "🚫 Akunmu telah ditangguhkan. Hubungi admin untuk bantuan.",
  error_empty_message: "Mohon berikan pesan setelah perintah.",

  // Admin
  admin_only: "⛔ Perintah ini hanya untuk admin.",
};

export default id;
