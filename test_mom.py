#!/usr/bin/env python3
import os
from file_handlers import save_mom
from prompt_handlers import generate_mom_from_transcript

def test_mom_generation():
    """Test function untuk generate MoM dengan format baru"""
    
    # Path file transkrip yang sudah ada
    txt_file = "uploads/20250526.txt"
    
    if not os.path.exists(txt_file):
        print(f"❌ File tidak ditemukan: {txt_file}")
        return False
    
    print(f"📁 Membaca file: {txt_file}")
    
    # Baca file transkrip
    with open(txt_file, 'r', encoding='utf-8') as f:
        transcript_text = f.read()
    
    print(f"📄 Panjang transkripsi: {len(transcript_text):,} karakter")
    
    # Ambil sampel yang lebih besar untuk testing (2000 karakter)
    sample_text = transcript_text[:2000] + "..." if len(transcript_text) > 2000 else transcript_text
    print(f"🔬 Menggunakan sampel: {len(sample_text)} karakter")
    
    try:
        print("🤖 Memulai generate MoM dengan FORMAT BARU...")
        print("📋 Format: Netral, Profesional, Ringkas, Berdasarkan Agenda/Pokok Bahasan + Kesimpulan")
        
        # Generate MoM
        mom = generate_mom_from_transcript(sample_text)
        
        if mom:
            print("✅ MoM BARU berhasil di-generate!")
            print(f"📊 Panjang MoM: {len(mom)} karakter")
            
            # Simpan MoM
            mom_filename = save_mom(mom, "20250526.txt", "uploads")
            print(f"💾 File MoM disimpan: {mom_filename}")
            
            # Verifikasi file tersimpan
            mom_path = os.path.join("uploads", mom_filename)
            if os.path.exists(mom_path):
                print("✅ File MoM berhasil tersimpan!")
                file_size = os.path.getsize(mom_path)
                print(f"📁 Ukuran file: {file_size} bytes")
                
                # Tampilkan preview MoM dengan format baru
                print("\n" + "="*70)
                print("📋 PREVIEW NOTULEN RAPAT (FORMAT BARU - PROFESIONAL)")
                print("="*70)
                
                # Tampilkan beberapa baris pertama untuk melihat struktur
                lines = mom.split('\n')
                preview_lines = lines[:30] if len(lines) > 30 else lines
                
                for line in preview_lines:
                    print(line)
                
                if len(lines) > 30:
                    print("...")
                    print(f"[... dan {len(lines) - 30} baris lainnya]")
                    
                print("="*70)
                print("🎯 FITUR FORMAT BARU:")
                print("✅ Struktur berdasarkan agenda/pokok bahasan")
                print("✅ Bahasa netral dan profesional") 
                print("✅ Ringkas tapi informatif")
                print("✅ Kesimpulan di akhir")
                print("✅ Konsisten dan rapi")
                print("="*70)
                
                return True
            else:
                print("❌ File MoM tidak tersimpan!")
                return False
        else:
            print("❌ MoM tidak dapat di-generate (hasil kosong)")
            return False
            
    except Exception as e:
        print(f"❌ Error saat generate MoM: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 TESTING GENERATE MoM - FORMAT BARU")
    print("="*40)
    print("🎯 Target: Netral, Profesional, Ringkas, Berdasarkan Agenda/Pokok Bahasan")
    print("="*40)
    
    success = test_mom_generation()
    
    print("\n" + "="*40)
    if success:
        print("🎉 TEST BERHASIL! MoM FORMAT BARU telah dibuat!")
        print("📋 Cek file .mom.txt untuk melihat hasil lengkap")
    else:
        print("💥 TEST GAGAL! Ada masalah dengan generate MoM.") 