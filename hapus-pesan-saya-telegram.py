# ============================================================
# Hapus SEMUA pesan SAYA SENDIRI di satu chat Telegram
# (pesan lawan bicara tidak disentuh sama sekali)
#
# Jalan di HP Master sendiri lewat Termux. BUKAN di server Raphael.
# TIDAK PERLU EDIT FILE INI — jalankan saja, nanti ditanya satu-satu.
# api_id / api_hash / kode login JANGAN pernah dikirim ke chat mana pun.
#
# Cara pakai:
#   1. Ambil api_id + api_hash dari https://my.telegram.org
#      (login pakai nomor Master -> API development tools)
#   2. pip install telethon
#   3. python hapus-pesan-saya-telegram.py
#      - Pertama kali: ditanya api_id, api_hash (disimpan di kunci.json
#        di folder yang sama, biar tidak ditanya lagi), lalu nomor HP +
#        kode yang masuk ke Telegram Master.
#      - Setiap jalan: ditanya chat siapa yang mau dibersihkan.
#      - Sebelum menghapus, jumlah pesan dihitung dulu dan skrip minta
#        Master mengetik HAPUS sebagai tanda yakin.
#
# PERINGATAN: penghapusan berlaku untuk DUA SISI (hilang juga di HP
# lawan bicara) dan TIDAK BISA dibatalkan / dikembalikan.
# File kunci.json dan sesi-saya.session = kunci akun Master.
# Jangan dibagikan ke siapa pun.
# ============================================================

import asyncio
import json
import os

from telethon import TelegramClient

FILE_KUNCI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kunci.json")


def ambil_kunci():
    """Baca api_id + api_hash dari kunci.json; kalau belum ada, tanya lalu simpan."""
    if os.path.exists(FILE_KUNCI):
        with open(FILE_KUNCI, "r", encoding="utf-8") as f:
            data = json.load(f)
        return int(data["api_id"]), data["api_hash"]

    print("Sekali ini saja Master perlu isi kunci API (dari my.telegram.org).")
    api_id = input("API_ID (angka): ").strip()
    api_hash = input("API_HASH (kode panjang): ").strip()
    with open(FILE_KUNCI, "w", encoding="utf-8") as f:
        json.dump({"api_id": int(api_id), "api_hash": api_hash}, f)
    print("Tersimpan di kunci.json — lain kali tidak ditanya lagi.")
    print("INGAT: kunci.json jangan dibagikan ke siapa pun.\n")
    return int(api_id), api_hash


async def main():
    api_id, api_hash = ambil_kunci()
    client = TelegramClient("sesi-saya", api_id, api_hash)

    async with client:
        me = await client.get_me()

        target_input = input(
            "Chat siapa yang mau dibersihkan? (username tanpa @, atau nomor +62...): "
        ).strip()
        target = await client.get_input_entity(target_input)

        # Hitung dulu pesan Master di chat ini — tanpa menghapus apa pun.
        print("Menghitung pesan Master di chat ini...")
        jumlah = 0
        async for m in client.iter_messages(target):
            if m.sender_id == me.id:
                jumlah += 1
        print(f"Ditemukan {jumlah} pesan Master di chat ini.")
        if jumlah == 0:
            print("Tidak ada yang perlu dihapus. Selesai.")
            return

        jawab = input(
            f"Hapus SEMUA {jumlah} pesan itu, hilang juga di HP dia? "
            "Ketik HAPUS (huruf besar) kalau yakin: "
        ).strip()
        if jawab != "HAPUS":
            print("Dibatalkan. Tidak ada pesan yang dihapus.")
            return

        ids = []
        total = 0

        async def flush():
            nonlocal total
            if ids:
                await client.delete_messages(target, list(ids), revoke=True)
                total += len(ids)
                print(f"terhapus sejauh ini: {total} / {jumlah}")
                ids.clear()
                await asyncio.sleep(2)  # jeda biar tidak kena flood limit

        async for m in client.iter_messages(target):
            if m.sender_id == me.id:
                ids.append(m.id)
                if len(ids) >= 100:
                    await flush()
        await flush()
        print(f"SELESAI. Total pesan Master yang terhapus: {total}")


asyncio.run(main())
