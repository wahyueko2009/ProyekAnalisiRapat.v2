# Aplikasi Analisis Rapat

Aplikasi ini digunakan untuk menganalisis file audio rapat dan menghasilkan transkripsi serta notulen rapat (MoM) secara otomatis.

## Fitur

- Upload file audio (MP3, WAV, M4A, MP4)
- Pra-proses audio (noise reduction, filtering, normalisasi)
- Transkripsi otomatis dengan speaker diarization
- Pembuatan notulen rapat (MoM) terstruktur
- Dukungan bahasa Indonesia
- Batas ukuran file 250MB

## Persyaratan Sistem

- Python 3.8 atau lebih tinggi
- FFmpeg
- GPU dengan dukungan CUDA (opsional, untuk performa lebih baik)
- Koneksi internet

## Cara Instalasi

1. Clone repository ini:
```bash
git clone https://github.com/username/analisis-rapat.git
cd analisis-rapat
```

2. Buat virtual environment:
```bash
python -m venv venv
```

3. Aktifkan virtual environment:
```bash
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Buat file .env dan isi dengan token Hugging Face:
```
HUGGINGFACE_TOKEN=your_token_here
```

## Cara Penggunaan

1. Jalankan aplikasi:
```bash
python app.py
```

2. Buka browser dan akses:
```
http://localhost:5000
```

3. Upload file audio melalui interface web

4. Tunggu proses selesai

5. Download hasil transkripsi dan MoM

## Format File yang Didukung

- MP3
- WAV
- M4A
- MP4

## Batasan

- Ukuran file maksimal: 250MB
- Durasi audio: tidak terbatas
- Jumlah speaker: 1-10 orang

## Troubleshooting

1. Error "Module not found":
   - Pastikan virtual environment aktif
   - Jalankan `pip install -r requirements.txt`

2. Error CUDA:
   - Pastikan GPU terinstall dengan benar
   - Gunakan CPU jika tidak ada GPU

3. Error FFmpeg:
   - Install FFmpeg di sistem
   - Pastikan FFmpeg ada di PATH

4. Error Hugging Face:
   - Periksa token di file .env
   - Pastikan token valid

## Lisensi

MIT License 