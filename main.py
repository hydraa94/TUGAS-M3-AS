import json
import os

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise SystemExit("GEMINI_API_KEY belum diisi. Salin .env.example menjadi .env dan isi API key.")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel(
    model_name="gemini-3.5-flash-lite",
)

perintah_untuk_ai = """
Kamu adalah asisten analisis data kehadiran siswa.
Gunakan hanya statistik yang diberikan di bawah ini.
Jangan mengarang angka, fakta, atau penyebab ketidakhadiran.
Jelaskan temuan secara objektif, singkat, dan mudah dipahami.
Jangan menebak alasan siswa sakit, izin, atau alpa.
Jangan menghitung persentase kehadiran karena jumlah hari sekolah tidak diketahui.
Data per siswa menggunakan nomor absen dan nama dari lembar absensi.
Gunakan nama hanya untuk merujuk data yang diberikan; jangan menambahkan informasi pribadi lain.
"""

with open("data/attendance_data.json", "r", encoding="utf-8") as file:
    data_kehadiran = json.load(file)

pertanyaan_uji_coba = """
Analisis data kehadiran berikut:
1. Sebutkan bulan dengan jumlah sakit, izin, dan alpa tertinggi.
2. Jelaskan pola ketidakhadiran yang terlihat dari data.
3. Sebutkan hal yang perlu diperhatikan berdasarkan data.
4. Bandingkan siswa dengan total ketidakhadiran tertinggi dan terendah menggunakan nama yang tersedia.
Gunakan hanya angka yang tersedia dan jangan menebak penyebabnya.
Tampilkan hasil analisis dalam teks berpoin sederhana dan mudah dipahami tanpa format markdown atau tabel.
"""

prompt = f"""
{perintah_untuk_ai}

Data statistik kehadiran:
{json.dumps(data_kehadiran, indent=2, ensure_ascii=False)}

{pertanyaan_uji_coba}
"""

response = model.generate_content(prompt)
hasil = response.text

print("\n==== Hasil Analisis AI ====\n")
print(hasil)
