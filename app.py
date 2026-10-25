from flask import Flask, request, render_template_string

app = Flask(__name__)

GEJALA = {
    "G1": "Hidung meler",
    "G2": "Bersin-bersin",
    "G3": "Demam serta merasa pengap",
    "G4": "Batuk keras dengan tarikan napas awal yang panjang melalui mulut",
    "G5": "Terdengar seperti mau muntah",
    "G6": "Mata merah dan berair",
    "G7": "Wajah berwarna merah atau biru",
    "G8": "Kelelahan yang ekstrem",
    "G9": "Suara tinggi melengking saat menarik napas",
}

PENYAKIT = {
    "P01": {
        "nama": "Pertussis Ringan",
        "gejala": ["G1", "G2", "G3", "G4"],
    },
    "P02": {
        "nama": "Pertussis Akut",
        "gejala": ["G3", "G4", "G5", "G6"],
    },
    "P03": {
        "nama": "Pertussis Subakut/Kronis",
        "gejala": ["G4", "G7", "G8", "G9"],
    },
}

def cosine_similarity(selected, disease_symptoms):
    """Menghitung cosine similarity untuk vektor biner G1-G9."""
    if not selected:
        return 0.0

    dot_product = sum(1 for code in selected if code in disease_symptoms)
    selected_norm = len(selected) ** 0.5
    disease_norm = len(disease_symptoms) ** 0.5

    if selected_norm == 0 or disease_norm == 0:
        return 0.0

    return dot_product / (selected_norm * disease_norm)

HTML = """
<!doctype html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Sistem Informasi Gejala Pertussis</title>
  <style>
    :root { --navy:#17324d; --blue:#246b8e; --pale:#eef6f8; --ink:#263746; --muted:#617383; }
    * { box-sizing: border-box; }
    body { margin:0; font-family: Arial, sans-serif; background:#f4f7fa; color:var(--ink); }
    header { background:linear-gradient(125deg,#17324d,#246b8e); color:white; padding:38px 20px; }
    .wrap { max-width:1000px; margin:auto; }
    header h1 { margin:0 0 10px; font-size:clamp(26px,4vw,38px); }
    header p { margin:0; line-height:1.6; color:#e4f0f6; max-width:760px; }
    main { max-width:1000px; margin:26px auto; padding:0 16px 36px; }
    .panel { background:white; border-radius:16px; padding:24px; margin-bottom:20px; box-shadow:0 5px 20px #16324d12; }
    h2 { margin-top:0; color:var(--navy); }
    .hint { color:var(--muted); line-height:1.6; }
    .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:12px; }
    label.symptom { display:flex; gap:12px; align-items:flex-start; border:1px solid #dce6ec; border-radius:12px; padding:14px; cursor:pointer; line-height:1.45; }
    label.symptom:hover { border-color:var(--blue); background:#f7fbfc; }
    input[type=checkbox] { width:18px; height:18px; margin-top:2px; accent-color:var(--blue); flex-shrink:0; }
    .code { display:inline-block; font-size:12px; color:var(--blue); font-weight:bold; margin-bottom:4px; }
    button { border:0; border-radius:10px; background:var(--blue); color:white; padding:13px 20px; font-size:16px; font-weight:bold; cursor:pointer; margin-top:18px; }
    button:hover { background:#194f6c; }
    .result { border-left:5px solid var(--blue); background:var(--pale); padding:18px; border-radius:10px; margin:12px 0; }
    .result h3 { margin:0 0 8px; color:var(--navy); }
    .bar-bg { background:#dce7ed; height:10px; border-radius:10px; overflow:hidden; margin:10px 0 4px; }
    .bar { height:100%; background:var(--blue); border-radius:10px; }
    .warning { background:#fff8e8; border:1px solid #f0dfb1; border-radius:12px; padding:15px; line-height:1.6; }
    .empty { color:var(--muted); }
    footer { text-align:center; color:var(--muted); font-size:13px; padding:10px 16px 30px; }
    @media(max-width:600px) { .panel { padding:18px; } header { padding:30px 18px; } }
  </style>
</head>
<body>
<header>
  <div class="wrap">
    <h1>Sistem Informasi Gejala Pertussis</h1>
    <p>Pilih gejala yang dialami untuk melihat kemiripan pola gejala dengan tiga kategori pertussis berdasarkan metode Cosine Similarity.</p>
  </div>
</header>
<main>
  <section class="panel">
    <h2>1. Pilih gejala</h2>
    <p class="hint">Centang semua gejala yang sedang dialami. Jika tidak ada gejala yang sesuai, biarkan tidak terpilih.</p>
    <form method="post">
      <div class="grid">
      {% for code, name in symptoms.items() %}
        <label class="symptom">
          <input type="checkbox" name="gejala" value="{{ code }}" {% if code in selected %}checked{% endif %}>
          <span><span class="code">{{ code }}</span><br>{{ name }}</span>
        </label>
      {% endfor %}
      </div>
      <button type="submit">Analisis Kemiripan</button>
    </form>
  </section>

  {% if submitted %}
  <section class="panel">
    <h2>2. Hasil perhitungan</h2>
    {% if not selected %}
      <p class="empty">Belum ada gejala yang dipilih. Silakan pilih setidaknya satu gejala, lalu tekan tombol analisis.</p>
    {% else %}
      <p class="hint">Gejala terpilih: {{ selected|length }}. Hasil berikut adalah skor kemiripan pola gejala, bukan diagnosis medis.</p>
      {% for item in results %}
      <div class="result">
        <h3>{{ item.nama }}</h3>
        <strong>{{ "%.1f"|format(item.score * 100) }}% kemiripan</strong>
        <div class="bar-bg"><div class="bar" style="width:{{ item.score * 100 }}%"></div></div>
        <small>Gejala yang cocok dengan pola: {{ item.overlap }} dari {{ item.total }} gejala pada kategori ini.</small>
      </div>
      {% endfor %}
      <p><strong>Pola yang paling mirip:</strong> {{ results[0].nama }}.</p>
    {% endif %}
  </section>
  {% endif %}

  <section class="panel">
    <h2>Catatan penting</h2>
    <div class="warning">
      Website ini merupakan demonstrasi pembelajaran menggunakan daftar gejala dari artikel dan metode Cosine Similarity. Skor kemiripan tidak menunjukkan peluang seseorang terkena penyakit dan tidak dapat memastikan diagnosis. Pertussis perlu dinilai oleh tenaga kesehatan. Jika ada kesulitan bernapas, bibir/wajah membiru, atau kondisi memburuk, segera cari pertolongan medis.
    </div>
  </section>
</main>
<footer>Demo pembelajaran • Data gejala merujuk artikel “Sistem Pakar Untuk Mendiagnosa Penyakit Pertussis (Batuk Rejan)” (2020).</footer>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    submitted = request.method == "POST"
    selected = request.form.getlist("gejala") if submitted else []
    selected = [code for code in selected if code in GEJALA]

    results = []
    if selected:
        for code, data in PENYAKIT.items():
            disease_symptoms = data["gejala"]
            score = cosine_similarity(selected, disease_symptoms)
            overlap = sum(1 for symptom in selected if symptom in disease_symptoms)
            results.append({
                "kode": code,
                "nama": data["nama"],
                "score": score,
                "overlap": overlap,
                "total": len(disease_symptoms),
            })
        results.sort(key=lambda item: item["score"], reverse=True)

    return render_template_string(
        HTML,
        symptoms=GEJALA,
        selected=selected,
        submitted=submitted,
        results=results,
    )

if __name__ == "__main__":
    app.run(debug=True)
