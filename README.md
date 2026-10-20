# Proyek Analisis Data: E-Commerce Public Dataset ✨

Analisis data E-Commerce Public Dataset (Olist, Brasil) untuk pesanan *delivered* periode Januari 2017 – Agustus 2018, beserta dashboard interaktif Streamlit.

**Pertanyaan bisnis**
Pertanyaan 1: Bagaimana tren jumlah pesanan dan revenue bulanan pada periode Januari 2017 – Agustus 2018, dan berapa persen pertumbuhan revenue Januari–Agustus 2018 dibandingkan Januari–Agustus 2017?

Pertanyaan 2: Kategori produk apa saja yang menyumbang revenue terbesar dan terkecil selama Januari 2017 – Agustus 2018, dan berapa persen kontribusi 10 kategori teratas terhadap total revenue?

Pertanyaan 3: Seberapa besar selisih rata-rata skor review antara pesanan yang terlambat dan yang tepat waktu selama Januari 2017 – Agustus 2018, dan negara bagian (state) mana yang memiliki persentase keterlambatan pengiriman tertinggi?

**Analisis lanjutan:** RFM Analysis, clustering dengan manual grouping & binning, serta geospatial analysis (folium).

## Struktur Direktori
```
submission
├───dashboard
│   ├───main_data.csv
│   └───dashboard.py
├───data
│   ├───customers_dataset.csv
│   ├───geolocation_dataset.csv
│   ├───order_items_dataset.csv
│   ├───order_payments_dataset.csv
│   ├───order_reviews_dataset.csv
│   ├───orders_dataset.csv
│   ├───product_category_name_translation.csv
│   ├───products_dataset.csv
│   └───sellers_dataset.csv
├───notebook.ipynb
├───README.md
├───requirements.txt
└───url.txt
```

## ⚙️ Prasyarat
- **Python 3.9 atau lebih baru** (disarankan Python 3.11)
- **pip** (sudah termasuk saat instalasi Python)

Cek versi Python:
```bash
python --version
```

## 🧪 Setup Virtual Environment

Buka terminal (Command Prompt / PowerShell / Terminal), lalu masuk ke folder proyek:
```bash
cd submission
```

### Opsi A — Menggunakan `venv` (bawaan Python)

**1. Buat virtual environment**
```bash
python -m venv venv
```

**2. Aktifkan virtual environment**

Windows (Command Prompt):
```bash
venv\Scripts\activate
```

Windows (PowerShell):
```bash
.\venv\Scripts\Activate.ps1
```

macOS / Linux:
```bash
source venv/bin/activate
```

Jika berhasil, akan muncul tanda `(venv)` di awal baris terminal.

### Opsi B — Menggunakan Anaconda
```bash
conda create --name main-ds python=3.11
conda activate main-ds
```

## 📦 Instalasi Dependencies
Pastikan virtual environment sudah aktif, lalu jalankan:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Library yang akan terpasang: `numpy`, `pandas`, `matplotlib`, `seaborn`, `folium`, dan `streamlit`.

## 📓 Menjalankan Notebook (Opsional)
1. Install Jupyter (jika belum ada):
```bash
   pip install notebook
```
2. Jalankan dari folder `submission`:
```bash
   jupyter notebook notebook.ipynb
```
3. Jalankan seluruh sel (**Kernel → Restart & Run All**). Notebook membaca data dari folder `data/` dan menghasilkan ulang `dashboard/main_data.csv`.

## 🚀 Menjalankan Dashboard Streamlit di Lokal
1. Pastikan berada di folder `submission` dan virtual environment sudah aktif.
2. Jalankan perintah berikut:
```bash
   streamlit run dashboard/dashboard.py
```
3. Browser akan terbuka otomatis di **http://localhost:8501**. Jika tidak, buka alamat tersebut secara manual.
4. Gunakan filter **rentang tanggal** dan **state** di sidebar untuk mengeksplorasi data pada tab:
   - 📈 Tren Penjualan
   - 📦 Kategori Produk
   - 🚚 Pengiriman & Kepuasan
   - 👥 Segmentasi RFM
   - 🗺️ Peta
5. Untuk menghentikan dashboard, tekan **Ctrl + C** di terminal.

> **Catatan:** jalankan perintah dari folder `submission` (bukan dari dalam folder `dashboard`) agar tema pada `.streamlit/config.toml` ikut terbaca. Tab **Peta** membutuhkan koneksi internet untuk memuat peta dasar.

## 🌐 Dashboard Online
Dashboard juga dapat diakses melalui Streamlit Cloud pada tautan di file `url.txt`.
