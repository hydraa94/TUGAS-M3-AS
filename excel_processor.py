import json
from pathlib import Path

import pandas as pd

SUMBER_FILE = Path("data/attendance.xlsx")
FILE_OUTPUT = Path("data/attendance_data.json")


def baca_statistik_bulanan(df, nama_bulan):
    kolom_tanggal = []
    for kolom in range(2, df.shape[1] - 3):
        tanggal = str(df.iat[1, kolom]).strip()
        if tanggal.replace(".0", "").isdigit():
            kolom_tanggal.append(kolom)

    data_siswa = df.iloc[2:38]
    data_siswa = data_siswa[data_siswa.iloc[:, 0].notna()]

    per_siswa = []
    for _, baris in data_siswa.iterrows():
        tanda = baris.iloc[kolom_tanggal].astype(str).str.strip().str.upper()
        sakit = int((tanda == "S").sum())
        izin = int((tanda == "I").sum())
        alpa = int((tanda == "A").sum())
        per_siswa.append({
            "no": int(float(str(baris.iloc[0]).strip())),
            "name": str(baris.iloc[1]).strip(),
            "sakit": sakit,
            "izin": izin,
            "alpa": alpa,
            "total": sakit + izin + alpa,
        })

    harian = {
        "sakit": sum(item["sakit"] for item in per_siswa),
        "izin": sum(item["izin"] for item in per_siswa),
        "alpa": sum(item["alpa"] for item in per_siswa),
    }

    blok_rekap = data_siswa.iloc[:, -3:].apply(pd.to_numeric, errors="coerce").fillna(0)
    rekap = {
        "sakit": int(blok_rekap.iloc[:, 0].sum()),
        "izin": int(blok_rekap.iloc[:, 1].sum()),
        "alpa": int(blok_rekap.iloc[:, 2].sum()),
    }

    statistik = {
        "bulan": nama_bulan.strip().title(),
        "hari_tercatat": len(kolom_tanggal),
        **harian,
        "total": sum(harian.values()),
    }
    return statistik, rekap, per_siswa


def main():
    with pd.ExcelFile(SUMBER_FILE, engine="openpyxl") as excel:
        semua_bulan = []
        semua_rekap = {}
        siswa_bulanan = []

        for nama_sheet in excel.sheet_names:
            df = pd.read_excel(excel, sheet_name=nama_sheet, header=None)
            statistik, rekap, per_siswa = baca_statistik_bulanan(df, nama_sheet)
            semua_bulan.append(statistik)
            semua_rekap[statistik["bulan"]] = rekap
            siswa_bulanan.append((statistik["bulan"], per_siswa))

    siswa = {}
    for bulan, daftar in siswa_bulanan:
        for data in daftar:
            no = data["no"]
            if no not in siswa:
                siswa[no] = {
                    "no": no,
                    "name": data["name"],
                    "sakit": 0,
                    "izin": 0,
                    "alpa": 0,
                    "per_bulan": [],
                }
            siswa[no]["sakit"] += data["sakit"]
            siswa[no]["izin"] += data["izin"]
            siswa[no]["alpa"] += data["alpa"]
            siswa[no]["per_bulan"].append({
                "bulan": bulan,
                "sakit": data["sakit"],
                "izin": data["izin"],
                "alpa": data["alpa"],
            })

    for data in siswa.values():
        data["total"] = data["sakit"] + data["izin"] + data["alpa"]

    per_siswa = []
    for data in sorted(siswa.values(), key=lambda item: (-item["total"], item["no"])):
        per_siswa.append({
            "no": data["no"],
            "name": data["name"],
            "sakit": data["sakit"],
            "izin": data["izin"],
            "alpa": data["alpa"],
            "total": data["total"],
            "per_bulan": data["per_bulan"],
        })

    ringkasan = {
        "sakit": sum(item["sakit"] for item in semua_bulan),
        "izin": sum(item["izin"] for item in semua_bulan),
        "alpa": sum(item["alpa"] for item in semua_bulan),
    }
    ringkasan["total_ketidakhadiran"] = sum(ringkasan.values())
    jumlah_hari = sum(item["hari_tercatat"] for item in semua_bulan)

    catatan_data = [
        "Statistik dihitung dari tanda S/I/A pada kolom tanggal; kolom Rekap tidak dijumlahkan agar tidak terjadi penghitungan ganda.",
        f"Persentase kehadiran tidak dihitung karena jumlah hari sekolah tidak tersedia; {jumlah_hari} adalah jumlah hari yang tercatat.",
        "Data per siswa menggunakan nomor absen dan nama dari lembar absensi.",
    ]

    for item in semua_bulan:
        rekap = semua_rekap[item["bulan"]]
        if any(item[k] != rekap[k] for k in ["sakit", "izin", "alpa"]):
            catatan_data.append(
                f"Pada {item['bulan']}, rincian harian menunjukkan sakit {item['sakit']}, "
                f"izin {item['izin']}, alpa {item['alpa']}, sedangkan kolom Rekap menunjukkan "
                f"sakit {rekap['sakit']}, izin {rekap['izin']}, alpa {rekap['alpa']}. "
                "Statistik menggunakan rincian harian."
            )

    hasil = {
        "sumber_data": SUMBER_FILE.name,
        "jumlah_siswa": len(per_siswa),
        "jumlah_bulan_tercatat": len(semua_bulan),
        "jumlah_hari_tercatat": jumlah_hari,
        "ringkasan": ringkasan,
        "per_bulan": semua_bulan,
        "per_siswa": per_siswa,
        "catatan_data": catatan_data,
    }

    FILE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(FILE_OUTPUT, "w", encoding="utf-8") as file:
        json.dump(hasil, file, indent=2, ensure_ascii=False)

    print(f"Data kehadiran berhasil disimpan ke {FILE_OUTPUT}")


if __name__ == "__main__":
    main()
