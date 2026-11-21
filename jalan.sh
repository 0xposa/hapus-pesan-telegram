#!/usr/bin/env bash
# Satu perintah untuk menjalankan penghapus pesan Telegram.
# Bisa jalan di Termux langsung ATAU di Debian proot (proot-distro) —
# skrip ini mendeteksi sendiri lingkungannya.
# Otomatis: ambil versi terbaru, pasang python + pip + telethon
# kalau belum ada, lalu jalankan skrip utamanya.
# Master tinggal jawab pertanyaan di layar.
cd "$(dirname "$0")" || exit 1

if command -v git >/dev/null 2>&1; then
  git pull -q 2>/dev/null
fi

# --- Tentukan perintah python ---
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  PY=""
fi

# --- Pasang python kalau belum ada ---
if [ -z "$PY" ]; then
  if command -v pkg >/dev/null 2>&1; then
    pkg install -y python
    PY=python
  elif command -v apt-get >/dev/null 2>&1; then
    apt-get update -qq && apt-get install -y -qq python3 python3-pip git
    PY=python3
  fi
fi

# --- Pastikan pip ada ---
if ! $PY -m pip --version >/dev/null 2>&1; then
  if command -v pkg >/dev/null 2>&1; then
    pkg install -y python
  elif command -v apt-get >/dev/null 2>&1; then
    apt-get install -y -qq python3-pip
  fi
fi

# --- Pasang telethon kalau belum ada (Debian kadang perlu --break-system-packages) ---
if ! $PY -c "import telethon" 2>/dev/null; then
  $PY -m pip install telethon 2>/dev/null || $PY -m pip install --break-system-packages telethon
fi

exec $PY hapus-pesan-saya-telegram.py
