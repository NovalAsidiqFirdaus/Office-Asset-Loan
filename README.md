# Office Asset Loan (`office_asset_loan`)

> **Tugas Odoo Bootcamp Batch #10 (Basic): Custom Module “Office Asset Loan”**  
> **Odoo Community Edition 19.0** · Level: Basic

---

## 1. Deskripsi Modul
Modul `office_asset_loan` dirancang untuk memfasilitasi pencatatan inventaris bersama kantor (proyektor, laptop cadangan, kamera, kabel roll, dsb.) dan mengelola siklus peminjamannya secara transparan, akurat, dan terstruktur.

Dengan modul ini:
- Setiap aset memiliki kode unik dan status ketersediaan (*Available*).
- Menghindari peminjaman ganda (*double borrowing*) pada aset yang sedang dipinjam orang lain.
- Mencegah peminjaman aset yang berstatus rusak (*damaged*).
- Menghitung durasi peminjaman dan mendeteksi keterlambatan pengembalian (*overdue*) secara otomatis.
- Mencegah penghapusan peminjaman yang sedang berjalan (*Borrowed*) atau sudah selesai (*Returned*).

---

## 2. Fitur Utama & Aturan Bisnis (BR-1 s/d BR-8)

1. **Master Inventaris Kantor (`office.asset`)**
   - Pencatatan aset: Nama Aset, Kode Aset, Kategori (*Electronics, Furniture, Vehicle, Other*), Tanggal Beli, Kondisi (*Good, Fair, Damaged*), Catatan, dan Status Aktif (*Archive support*).
   - **BR-1**: Kode aset dijamin unik di tingkat database menggunakan `models.Constraint('UNIQUE(code)', ...)`.
   - **Smart Button "Loans" (Bonus +3)**: Menampilkan jumlah peminjaman dan membuka daftar peminjaman terkait.
   - **Ketersediaan Real-Time**: Kolom `is_available` bernilai *True* jika tidak ada peminjaman berstatus *Borrowed*.

2. **Pencatatan Peminjaman (`office.asset.loan`)**
   - **BR-3**: Nomor peminjaman otomatis berformat `LOAN/0001`, `LOAN/0002`, dst. menggunakan `ir.sequence` dan `@api.model_create_multi`.
   - **BR-2**: Validasi tenggat pengembalian (`due_date` tidak boleh lebih awal dari `loan_date`) menggunakan `@api.constrains`.
   - **BR-8**: Otomatis mengisi `due_date = loan_date + 7 hari` ketika `loan_date` diubah jika `due_date` kosong atau lebih awal.
   - **BR-4**: Tombol **Borrow** hanya untuk status *Draft*. Memvalidasi bahwa aset tidak sedang dipinjam pihak lain dan kondisi aset bukan *Damaged*.
   - **BR-5**: Tombol **Return** hanya untuk status *Borrowed*, mencatat tanggal kembali (*return_date*) hari ini dan mengubah status menjadi *Returned*.
   - **BR-6**: Tombol **Cancel** membatalkan peminjaman berstatus *Draft*.
   - **BR-7**: Peminjaman berstatus *Borrowed* atau *Returned* dilarang dihapus (`@api.ondelete(at_uninstall=False)`).
   - **Durasi & Overdue**: Menghitung selisih hari (`duration_days`) dan menandai baris terlambat (*is_overdue*) dengan warna merah (`decoration-danger`).

3. **Fitur Bonus Terintegrasi (Nilai Tambah Maksimal)**
   - **Bonus +3**: Smart button *Loans* pada form aset.
   - **Bonus +3**: Filter *Overdue* pada pencarian peminjaman.
   - **Bonus +2**: Record Rule di mana pengguna internal hanya melihat peminjamannya sendiri, sedangkan Administrator melihat seluruh peminjaman.
   - **Bonus +2**: Data Demo terisi di `demo/office_asset_loan_demo.xml` (4 aset & 3 peminjaman).

---

## 3. Struktur Berkas Modul
```
office_asset_loan/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   ├── office_asset.py
│   └── office_asset_loan.py
├── security/
│   ├── ir.model.access.csv
│   └── office_asset_security.xml
├── data/
│   └── office_asset_loan_sequence.xml
├── demo/
│   └── office_asset_loan_demo.xml
├── views/
│   ├── office_asset_views.xml
│   ├── office_asset_loan_views.xml
│   └── office_asset_menus.xml
└── static/description/
    └── icon.png
```

---

## 4. Cara Instalasi

### Metode 1: Melalui Antarmuka Odoo (UI)
1. Pastikan folder `office_asset_loan` berada di dalam direktori `custom-addons` yang terdaftar pada konfigurasi `addons_path` di `odoo.conf`:
   ```ini
   addons_path = C:\odoo-dev\odoo\odoo\addons,C:\odoo-dev\odoo\addons,C:\odoo-dev\custom-addons
   ```
2. Restart Odoo Server (di VS Code tekan `F5` atau tombol Restart 🔄).
3. Buka browser: `http://localhost:8069`
4. Aktifkan **Developer Mode** di menu *Settings* (atau tambahkan `?debug=1` pada URL).
5. Buka menu **Apps** (Aplikasi) ➔ klik menu **Update Apps List** ➔ klik tombol **Update**.
6. Pada kotak pencarian, hapus filter dan ketik: `Office Asset Loan`
7. Klik tombol **Activate** / **Install**.

### Metode 2: Melalui Terminal (CLI)
Jalankan perintah instalasi langsung ke database:
```powershell
& "C:\odoo-dev\odoo\.venv\Scripts\python.exe" "C:\odoo-dev\odoo\odoo-bin" -c "C:\odoo-dev\odoo\odoo.conf" -d <nama_database> -i office_asset_loan
```

---

## 5. Verifikasi Skenario Uji (12 Skenario Lolos 100%)

| # | Langkah Pengujian | Hasil Pengujian | Status |
|---|---|---|:---:|
| 1 | Install modul pada database baru | Terinstal bersih tanpa error dan tanpa warning | ✅ Lolos |
| 2 | Buat aset "Proyektor Epson", kode `AST-001` | Tersimpan, status *Available* tercentang | ✅ Lolos |
| 3 | Buat aset kedua dengan kode `AST-001` | Ditolak oleh PostgreSQL constraint (BR-1) | ✅ Lolos |
| 4 | Buat peminjaman baru, pilih Proyektor Epson | Nomor `LOAN/0001` terbentuk, peminjam login user, tanggal pinjam hari ini | ✅ Lolos |
| 5 | Ubah `due_date` menjadi kemarin, lalu simpan | Muncul `ValidationError` (BR-2) | ✅ Lolos |
| 6 | Perbaiki `due_date`, klik Borrow | Status *Borrowed*, form read-only, aset tidak *Available* | ✅ Lolos |
| 7 | Buat peminjaman kedua untuk aset yang sama, klik Borrow | Ditolak dengan `UserError` bahwa aset sedang dipinjam (BR-4) | ✅ Lolos |
| 8 | Hapus peminjaman yang berstatus *Borrowed* | Ditolak dengan `UserError` (BR-7) | ✅ Lolos |
| 9 | Pada peminjaman pertama klik Return | Status *Returned*, `return_date` hari ini, aset kembali *Available* | ✅ Lolos |
| 10 | Ubah kondisi aset menjadi Damaged, coba Borrow | Ditolak dengan `UserError` karena kondisi Damaged (BR-4) | ✅ Lolos |
| 11 | Buka tab Loan History pada form aset | Seluruh riwayat peminjaman aset tampil rapi | ✅ Lolos |
| 12 | Login sebagai user internal biasa | Menu tampil normal, ACL & Record Rule bekerja | ✅ Lolos |

---

## 6. Kepatuhan Odoo 19 Community Edition
- Menggunakan `<list>` dan `view_mode="list,form"` (tanpa `<tree>`).
- Menggunakan ekspresi Python langsung pada `invisible="..."` dan `readonly="..."` (tanpa `attrs`).
- Menggunakan `models.Constraint(...)` (tanpa `_sql_constraints`).
- Menggunakan `@api.model_create_multi` dengan `vals_list` pada `create()`.
- Menggunakan `@api.ondelete(at_uninstall=False)` untuk proteksi integritas data.
- Menggunakan `self.env.cr`, `self.env.uid`, dan `self.env.context` (tanpa atribut privat usang).
- Skema XML Search View mematuhi standar validasi RelaxNG Odoo 19.

