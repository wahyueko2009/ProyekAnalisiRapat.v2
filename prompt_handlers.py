import re
import logging
from api_config import client, MAX_CHARS_OPENAI

# Setup logging
logger = logging.getLogger(__name__)

def format_transcript(text):
    # Hapus kata-kata yang tidak perlu seperti "oke", "ya", dll
    text = re.sub(r'\b(oke|ya|ya ya|silahkan)\b', '', text, flags=re.IGNORECASE)
    
    # Bersihkan spasi berlebih
    text = re.sub(r'\s+', ' ', text)
    
    # Pisahkan berdasarkan kalimat
    sentences = re.split(r'(?<=[.!?]) +', text)
    
    # Filter kalimat kosong atau terlalu pendek
    sentences = [s.strip() for s in sentences if len(s.strip()) > 3]
    
    # Format ulang dengan stack
    formatted_text = []
    stack = []
    current_speaker = None
    
    for sentence in sentences:
        # Deteksi pembicara baru
        if re.match(r'^(Pak|Bu|Ibu|Bapak|Sdr\.)', sentence, re.IGNORECASE):
            # Jika stack tidak kosong, tambahkan ke formatted_text
            if stack:
                formatted_text.append(' '.join(stack))
                stack = []
            
            if current_speaker:
                formatted_text.append('')  # Tambah baris kosong antar pembicara
            
            current_speaker = sentence.split()[0]
            stack.append(sentence)
        else:
            # Jika kalimat terlalu panjang, buat paragraf baru
            if len(' '.join(stack + [sentence])) > 200:
                if stack:
                    formatted_text.append(' '.join(stack))
                    stack = []
            stack.append(sentence)
    
    # Tambahkan sisa stack jika ada
    if stack:
        formatted_text.append(' '.join(stack))
    
    # Gabungkan semua paragraf dengan baris kosong di antaranya
    return '\n\n'.join(formatted_text)

def generate_mom_from_transcript(transcript_text):
    try:
        logger.info(f"Memulai generate MoM. Panjang teks: {len(transcript_text)} karakter")
        
        # Jika teks terlalu panjang, potong untuk testing
        if len(transcript_text) > MAX_CHARS_OPENAI:
            logger.warning(f"Teks terlalu panjang ({len(transcript_text)} karakter), dipotong menjadi {MAX_CHARS_OPENAI} karakter")
            transcript_text = transcript_text[:MAX_CHARS_OPENAI]
        
        prompt = (
            "Buatlah NOTULEN RAPAT yang PROFESIONAL dan RINGKAS dari transkrip berikut. "
            "Gunakan bahasa yang NETRAL dan FORMAL.\n\n"
            
            "FORMAT YANG HARUS DIGUNAKAN:\n"
            "═══════════════════════════════════════════════════════════════\n"
            "                        NOTULEN RAPAT\n"
            "═══════════════════════════════════════════════════════════════\n\n"
            
            "📅 INFORMASI RAPAT\n"
            "─────────────────────────────────────────────────────────────\n"
            "• Tanggal/Waktu : [Tentukan berdasarkan konteks atau tulis 'Tidak disebutkan']\n"
            "• Tempat        : [Ekstrak dari transkrip atau tulis 'Tidak disebutkan']\n"
            "• Jenis Rapat   : [Identifikasi: Meeting Project/Review/Koordinasi/dll]\n"
            "• Peserta       : [Daftar nama yang disebutkan dalam transkrip]\n\n"
            
            "📋 AGENDA & PEMBAHASAN\n"
            "─────────────────────────────────────────────────────────────\n"
            "[Untuk setiap agenda/topik yang dibahas, gunakan format berikut:]\n\n"
            "1. [NAMA AGENDA/TOPIK]\n"
            "   • [Ringkasan pembahasan dalam 2-3 kalimat]\n"
            "   • [Keputusan yang diambil]\n"
            "   • [PIC dan timeline jika ada]\n\n"
            
            "2. [NAMA AGENDA/TOPIK BERIKUTNYA]\n"
            "   • [Ringkasan pembahasan]\n"
            "   • [Keputusan]\n"
            "   • [PIC dan timeline]\n\n"
            
            "📌 TINDAK LANJUT\n"
            "─────────────────────────────────────────────────────────────\n"
            "• [Action item 1] - [PIC] - [Deadline]\n"
            "• [Action item 2] - [PIC] - [Deadline]\n"
            "• [Action item 3] - [PIC] - [Deadline]\n\n"
            
            "🎯 KESIMPULAN\n"
            "─────────────────────────────────────────────────────────────\n"
            "[Rangkuman hasil rapat dalam 2-3 kalimat yang padat]\n\n"
            
            "═══════════════════════════════════════════════════════════════\n"
            "Notulen disusun berdasarkan rekaman rapat.\n"
            "═══════════════════════════════════════════════════════════════\n\n"
            
            "PANDUAN PENULISAN:\n"
            "1. Gunakan bahasa Indonesia yang baku dan profesional\n"
            "2. Fokus pada substansi penting: keputusan, instruksi, deadline\n"
            "3. Hindari detail percakapan yang tidak relevan\n"
            "4. Strukturkan berdasarkan agenda/topik\n"
            "5. Gunakan bullet points untuk memudahkan pembacaan\n"
            "6. Pastikan kesimpulan mencerminkan hasil utama rapat\n\n"
            
            "TRANSKRIP RAPAT:\n"
            "─────────────────────────────────────────────────────────────\n"
            f"{transcript_text}\n"
        )
        
        logger.info("Mengirim request ke OpenAI...")
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "Anda adalah sekretaris profesional yang ahli dalam menyusun notulen rapat. Tugas Anda adalah menganalisis transkrip rapat dan menyusunnya menjadi notulen yang terstruktur berdasarkan agenda/pokok bahasan. Fokus pada substansi penting seperti keputusan, instruksi, dan tindak lanjut. Gunakan bahasa formal yang netral dan hindari detail percakapan yang tidak relevan. Kelompokkan pembahasan berdasarkan topik/agenda untuk memudahkan tracking progress."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2500,
            temperature=0.2
        )
        
        result = response.choices[0].message.content.strip()
        logger.info(f"MoM berhasil di-generate. Panjang hasil: {len(result)} karakter")
        return result
        
    except Exception as e:
        logger.error(f"Error saat generate MoM: {str(e)}")
        raise 