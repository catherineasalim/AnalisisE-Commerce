# Proyek Analisis Data: E-Commerce Public Dataset ✨

Analisis data E-Commerce Public Dataset (Olist, Brasil) untuk pesanan *delivered* periode Januari 2017 – Agustus 2018, beserta dashboard interaktif Streamlit.

**Pertanyaan bisnis**
1. Bagaimana tren jumlah pesanan dan revenue bulanan Jan 2017 – Agu 2018, dan berapa pertumbuhan revenue Jan–Agu 2018 vs Jan–Agu 2017?
2. Kategori produk apa yang menyumbang revenue terbesar dan terkecil, dan berapa kontribusi 10 kategori teratas?
3. Seberapa besar selisih skor review pesanan terlambat vs tepat waktu, dan state mana yang paling sering terlambat?

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

