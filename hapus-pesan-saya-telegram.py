# ============================================================
# Hapus SEMUA pesan SAYA SENDIRI di satu chat Telegram
# (pesan lawan bicara tidak disentuh sama sekali)
#
# Jalan di HP Master sendiri lewat Termux. BUKAN di server Raphael.
# api_id / api_hash / kode login JANGAN pernah dikirim ke chat mana pun.
#
# Cara pakai:
#   1. Ambil api_id + api_hash dari https://my.telegram.org
#      (login pakai nomor Master -> API development tools)
#   2. pip install telethon
#   3. Isi API_ID, API_HASH, dan TARGET di bawah
#   4. python hapus-pesan-saya-telegram.py
#      (pertama kali akan minta nomor HP + kode yang masuk ke Telegram Master)
#
# PERINGATAN: revoke=True = hilang juga di HP lawan bicara.
# Sekali jalan TIDAK BISA dibatalkan / dikembalikan.
# Coba dulu dengan BATAS_UJI kecil (mis. 20) sebelum membuka semua.
# ============================================================

import asyncio
from telethon import TelegramClient

# ---- ISI SENDIRI ----
API_ID = 0                # contoh: 1234567
API_HASH = ""             # contoh: "abcdef123456..."
TARGET = ""               # username lawan bicara (tanpa @) atau nomor +62...
BATAS_UJI = None          # None = hapus SEMUA pesan Master di chat itu.
                          # Kalau mau uji dulu, ganti jadi angka (mis. 20).
REVOKE = True             # True = hilang di dua sisi. False = cuma di HP Master.
# ----------------------

client = TelegramClient("sesi-saya", API_ID, API_HASH)


async def main():
    me = await client.get_me()
    target = await client.get_input_entity(TARGET)

    ids = []
    total = 0

    async def flush():
        nonlocal total
        if ids:
            await client.delete_messages(target, list(ids), revoke=REVOKE)
            total += len(ids)
            print(f"terhapus sejauh ini: {total}")
            ids.clear()
            await asyncio.sleep(2)  # jeda biar tidak kena flood limit

    async for m in client.iter_messages(target):
        if m.sender_id == me.id:
            ids.append(m.id)
            if BATAS_UJI is not None and total + len(ids) >= BATAS_UJI:
                await flush()
                break
            if len(ids) >= 100:
                await flush()
    await flush()
    print(f"SELESAI. Total pesan Master yang terhapus: {total}")


with client:
    client.loop.run_until_complete(main())
