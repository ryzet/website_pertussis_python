SISTEM INFORMASI GEJALA PERTUSSIS (DEMO PYTHON)

Isi:
- app.py: aplikasi web Flask
- requirements.txt: dependensi

Cara menjalankan di Windows:
1. Pastikan Python sudah terpasang.
2. Ekstrak ZIP ini.
3. Buka folder hasil ekstrak.
4. Klik address bar File Explorer, ketik cmd, lalu Enter.
5. Jalankan:
   py -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
6. Buka browser dan kunjungi:
   http://127.0.0.1:5000

Cara kerja:
- User memilih gejala G1-G9 dari artikel.
- Sistem membuat vektor biner dari gejala terpilih.
- Sistem menghitung Cosine Similarity terhadap pola gejala P01, P02, dan P03.
- Kategori dengan skor tertinggi ditampilkan sebagai pola yang paling mirip.

Catatan:
Ini hanya demonstrasi pembelajaran, bukan alat diagnosis medis. Skor kemiripan bukan probabilitas terkena penyakit. Data kategori gejala diambil dari tabel gejala artikel yang dilampirkan; validasi klinis diperlukan sebelum digunakan untuk tujuan kesehatan.
