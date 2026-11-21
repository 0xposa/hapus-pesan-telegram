#!/data/data/com.termux/files/usr/bin/bash
# Satu perintah untuk menjalankan penghapus pesan Telegram.
# Otomatis: ambil versi terbaru, pasang python + telethon kalau belum ada,
# lalu jalankan skrip utamanya. Master tinggal jawab pertanyaan di layar.
cd "$(dirname "$0")" || exit 1
git pull -q 2>/dev/null
command -v python >/dev/null 2>&1 || pkg install -y python
python -c "import telethon" 2>/dev/null || pip install telethon
exec python hapus-pesan-saya-telegram.py
