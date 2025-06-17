# 📋 PANDUAN PENGGUNAAN APLIKASI MoM (MINUTES OF MEETING)

## 🚀 Cara Menjalankan Aplikasi

1. **Jalankan aplikasi Flask:**
   ```bash
   python app.py
   ```

2. **Buka browser dan akses:**
   ```
   http://localhost:5000
   ```

## ✅ VERIFIKASI FILE MoM TERSIMPAN

### Ketika Upload File Audio:

1. **Upload file audio** (MP3, WAV, M4A, MP4) - maksimal 250MB
2. **Proses otomatis yang terjadi:**
   - ✅ File audio di-transkrip menggunakan Whisper
   - ✅ Transkrip diformat menggunakan stack-based processing
   - ✅ **MoM di-generate otomatis menggunakan GPT-4**
   - ✅ **File MoM disimpan ke folder uploads**

3. **File yang dihasilkan:**
   ```
   uploads/
   ├── namafile.mp4          # File audio asli
   ├── namafile.txt          # File transkrip
   └── namafile.mom.txt      # File MoM (YANG KITA CARI!)
   ```

### Indikator Sukses di Web Interface:

- **Status hijau:** "File berhasil diproses... MoM tersimpan sebagai [nama_file].mom.txt"
- **Card MoM muncul** dengan preview notulen
- **Alert hijau:** "✅ File MoM berhasil dibuat! 📁 Tersimpan sebagai: [nama_file].mom.txt"

### Jika Ada Masalah:

- **Alert merah:** "❌ File MoM tidak dapat disimpan"
- **Cek log aplikasi** di terminal untuk detail error
- **Pastikan OpenAI API key valid**

## 🧪 Testing dengan File yang Sudah Ada

Jika ingin test dengan file transkrip yang sudah ada:

```bash
# Akses endpoint test
http://localhost:5000/test_mom/20250526.txt
```

## 📁 Lokasi File MoM

File MoM tersimpan di:
```
/ProyekAnalisiRapat.v2/uploads/[nama_file].mom.txt
```

## 🔧 Troubleshooting

### Jika MoM tidak terbuat:
1. **Cek API Key OpenAI** di `app.py` (line 36)
2. **Cek koneksi internet** untuk akses OpenAI API
3. **Cek log aplikasi** di terminal untuk error details
4. **Pastikan transkripsi tidak kosong**

### Log yang Normal:
```
INFO:__main__:=== MEMULAI GENERATE MoM ===
INFO:prompt_handlers:Memulai generate MoM. Panjang teks: XXXX karakter
INFO:prompt_handlers:Mengirim request ke OpenAI...
INFO:prompt_handlers:MoM berhasil di-generate. Panjang hasil: XXXX karakter
INFO:__main__:✅ MoM berhasil di-generate!
INFO:__main__:✅ File MoM berhasil disimpan: namafile.mom.txt
INFO:__main__:✅ File MoM terverifikasi tersimpan (ukuran: XXXX bytes)
```

## 🎯 RINGKASAN FITUR

✅ **Upload kapasitas 250MB**  
✅ **Stack-based text processing**  
✅ **Auto-generate MoM dengan GPT-4**  
✅ **File MoM tersimpan otomatis**  
✅ **Verifikasi file tersimpan**  
✅ **Status feedback yang jelas**  

---

**🔥 SEKARANG APLIKASI SIAP DIGUNAKAN!**  
File MoM akan otomatis dibuat setiap kali Anda upload file audio. 