# ============================================================
# PENGHAPUS PESAN TELEGRAM SAYA
# Menghapus SEMUA pesan SAYA SENDIRI di satu chat Telegram.
# Pesan lawan bicara tidak disentuh sama sekali.
#
# Jalan di HP Master sendiri lewat Termux — tidak perlu edit file.
# Jalankan saja (atau lewat jalan.sh), lalu jawab pertanyaan di layar.
# Semua pertanyaan berbahasa Indonesia, langkahnya diberi nomor.
#
# api_id / api_hash / kode login / password JANGAN pernah
# dikirim ke chat mana pun — ketik hanya di Termux ini.
#
# PERINGATAN: pesan yang dihapus hilang juga di HP lawan bicara
# dan TIDAK BISA dikembalikan. Skrip selalu menghitung dulu dan
# minta ketik HAPUS sebelum benar-benar menghapus.
# File kunci.json dan sesi-saya.session = kunci akun Master.
# Jangan dibagikan ke siapa pun.
# ============================================================

import asyncio
import json
import os
import re
import sys
import time
from getpass import getpass

from telethon import TelegramClient, errors

DASAR = os.path.dirname(os.path.abspath(__file__))
FILE_KUNCI = os.path.join(DASAR, "kunci.json")


def tanya(teks):
    return input(teks).strip()


def bersihkan_nomor(n):
    """Terima nomor apa adanya (08xx, +62xx, pakai spasi/strip) -> format +62..."""
    n = re.sub(r"[\s\-()]", "", n)
    if n.startswith("0"):
        n = "+62" + n[1:]
    elif n.startswith("62"):
        n = "+" + n
    elif not n.startswith("+"):
        n = "+" + n
    return n


def ambil_kunci():
    if os.path.exists(FILE_KUNCI):
        try:
            with open(FILE_KUNCI, "r", encoding="utf-8") as f:
                data = json.load(f)
            return int(data["api_id"]), str(data["api_hash"])
        except Exception:
            print("File kunci lama rusak — kita isi ulang ya.\n")
    print("Bagian 1 — Kunci API (cuma ditanya sekali ini saja)")
    print("Ambilnya di my.telegram.org, menu API development tools.")
    while True:
        mentah = tanya("  API_ID (angka semua): ").replace(" ", "")
        if mentah.isdigit():
            api_id = int(mentah)
            break
        print("  API_ID itu isinya angka semua — coba lagi ya.")
    api_hash = tanya("  API_HASH (kode panjang): ").replace(" ", "")
    with open(FILE_KUNCI, "w", encoding="utf-8") as f:
        json.dump({"api_id": api_id, "api_hash": api_hash}, f)
    print("  Tersimpan. Lain kali tidak ditanya lagi.\n")
    return api_id, api_hash


async def masuk(client):
    await client.connect()
    if await client.is_user_authorized():
        return
    print("Bagian 2 — Masuk ke Telegram Master")
    phone = bersihkan_nomor(tanya("  Nomor HP Master (contoh: 0812...): "))
    await client.send_code_request(phone)
    print("  Kode masuk ke APLIKASI Telegram Master (biasanya bukan SMS).")
    code = tanya("  Ketik kodenya di sini: ").replace(" ", "")
    try:
        await client.sign_in(phone, code)
    except errors.SessionPasswordNeededError:
        pw = getpass("  Ada password dua langkah — ketik di sini (tidak kelihatan): ")
        await client.sign_in(password=pw)
    except errors.PhoneCodeInvalidError:
        print("  Kodenya salah. Jalankan lagi skripnya ya, Master.")
        sys.exit(1)
    except errors.PhoneCodeExpiredError:
        print("  Kodenya kedaluwarsa. Jalankan lagi skripnya ya, Master.")
        sys.exit(1)
    print("  Berhasil masuk.\n")


async def main():
    print("=" * 46)
    print("  PENGHAPUS PESAN TELEGRAM SAYA")
    print("  Yang dihapus cuma pesan Master — pesan dia utuh.")
    print("=" * 46)
    print()
    api_id, api_hash = ambil_kunci()
    client = TelegramClient(os.path.join(DASAR, "sesi-saya"), api_id, api_hash)
    await masuk(client)
    try:
        me = await client.get_me()
        print(f"Masuk sebagai: {me.first_name}\n")

        print("Bagian 3 — Pilih chatnya")
        target_input = tanya("  Username (tanpa @) atau nomor HP orangnya: ")
        if target_input.startswith("@"):
            target_input = target_input[1:]
        if re.fullmatch(r"[0-9\s\-+()]+", target_input):
            target_input = bersihkan_nomor(target_input)
        try:
            target = await client.get_input_entity(target_input)
            entity = await client.get_entity(target)
        except Exception:
            print("  Orangnya tidak ketemu. Cek lagi username / nomornya ya.")
            return
        nama = (
            getattr(entity, "first_name", None)
            or getattr(entity, "title", None)
            or str(target_input)
        )
        print(f"  Chat dengan: {nama}")

        print("  Menghitung pesan Master di chat ini...")
        jumlah = 0
        async for m in client.iter_messages(target):
            if m.sender_id == me.id:
                jumlah += 1
        if jumlah == 0:
            print("  Tidak ada pesan Master di chat ini. Aman — selesai.")
            return
        print(f"  Ada {jumlah} pesan Master di chat ini.")
        print("  Kalau dihapus, pesan itu hilang di HP Master DAN di HP dia.")
        jawab = tanya("  Hapus semua? Ketik HAPUS lalu Enter (selain itu = batal): ").lower()
        if jawab not in ("hapus", "ya", "y"):
            print("  Dibatalkan. Tidak ada pesan yang dihapus.")
            return

        print("\n  Menghapus... jangan tutup Termux-nya ya.")
        ids = []
        total = 0
        mulai = time.time()

        async def flush():
            nonlocal total
            while ids:
                try:
                    await client.delete_messages(target, list(ids), revoke=True)
                    total += len(ids)
                    ids.clear()
                    print(f"    terhapus {total} dari {jumlah}...")
                except errors.FloodWaitError as e:
                    print(f"    Telegram minta jeda {e.seconds} detik — kita tunggu otomatis...")
                    await asyncio.sleep(e.seconds + 1)
                await asyncio.sleep(1)

        async for m in client.iter_messages(target):
            if m.sender_id == me.id:
                ids.append(m.id)
                if len(ids) >= 100:
                    await flush()
        await flush()
        print(f"\n  SELESAI — {total} pesan Master terhapus dalam {int(time.time() - mulai)} detik.")
        print("  Pesan dia tidak ada yang berubah. Sampai jumpa, Master.")
    finally:
        await client.disconnect()


asyncio.run(main())
