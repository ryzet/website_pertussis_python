import tempfile
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------------------------------
# Data (tidak diubah dari versi Flask)
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# CSS asli dari versi Flask (tidak diubah sama sekali)
# ---------------------------------------------------------------------------
STYLE = """
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
"""


def _render_results(selected, results):
    if not selected:
        return (
            '<p class="empty">Belum ada gejala yang dipilih. Silakan pilih '
            "setidaknya satu gejala, lalu tekan tombol analisis.</p>"
        )

    items = []
    for item in results:
        items.append(
            f"""
      <div class="result">
        <h3>{item["nama"]}</h3>
        <strong>{item["score"] * 100:.1f}% kemiripan</strong>
        <div class="bar-bg"><div class="bar" style="width:{item["score"] * 100}%"></div></div>
        <small>Gejala yang cocok dengan pola: {item["overlap"]} dari {item["total"]} gejala pada kategori ini.</small>
      </div>"""
        )

    return (
        f'<p class="hint">Gejala terpilih: {len(selected)}. Hasil berikut adalah skor '
        "kemiripan pola gejala, bukan diagnosis medis.</p>"
        + "".join(items)
        + f'<p><strong>Pola yang paling mirip:</strong> {results[0]["nama"]}.</p>'
    )


def render_page(selected, submitted, results):
    """Membangun HTML halaman dengan CSS & struktur yang sama seperti versi Flask."""
    selected_set = set(selected)

    symptom_cards = []
    for code, name in GEJALA.items():
        checked = " checked" if code in selected_set else ""
        symptom_cards.append(
            f"""
        <label class="symptom">
          <input type="checkbox" name="gejala" value="{code}"{checked}>
          <span><span class="code">{code}</span><br>{name}</span>
        </label>"""
        )

    result_section = ""
    if submitted:
        result_section = f"""
  <section class="panel">
    <h2>2. Hasil perhitungan</h2>
    {_render_results(selected, results)}
  </section>"""

    return f"""<style>{STYLE}</style>
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
      <div class="grid">{"".join(symptom_cards)}
      </div>
      <button type="submit">Analisis Kemiripan</button>
    </form>
  </section>
{result_section}
  <section class="panel">
    <h2>Catatan penting</h2>
    <div class="warning">
      Website ini merupakan demonstrasi pembelajaran menggunakan daftar gejala dari artikel dan metode Cosine Similarity. Skor kemiripan tidak menunjukkan peluang seseorang terkena penyakit dan tidak dapat memastikan diagnosis. Pertussis perlu dinilai oleh tenaga kesehatan. Jika ada kesulitan bernapas, bibir/wajah membiru, atau kondisi memburuk, segera cari pertolongan medis.
    </div>
  </section>
</main>
<footer>Demo pembelajaran • Data gejala merujuk artikel “Sistem Pakar Untuk Mendiagnosa Penyakit Pertussis (Batuk Rejan)” (2020).</footer>"""


def calculate_results(selected):
    results = []
    if selected:
        for code, data in PENYAKIT.items():
            disease_symptoms = data["gejala"]
            score = cosine_similarity(selected, disease_symptoms)
            overlap = sum(1 for symptom in selected if symptom in disease_symptoms)
            results.append(
                {
                    "kode": code,
                    "nama": data["nama"],
                    "score": score,
                    "overlap": overlap,
                    "total": len(disease_symptoms),
                }
            )
        results.sort(key=lambda item: item["score"], reverse=True)
    return results


# ---------------------------------------------------------------------------
# Komponen Streamlit kustom
#
# HTML/CSS asli tetap dipakai apa adanya. Komponen ini hanya "jembatan" agar
# checkbox dan tombol HTML asli dapat mengirim nilainya kembali ke Python.
# ---------------------------------------------------------------------------
COMPONENT_SHELL = """<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<style>
  html, body { margin:0; padding:0; width:100%; background:transparent; }
  #root { width:100%; }
</style>
</head>
<body>
<div id="root"></div>
<script>
(function () {
  var RENDER = "streamlit:render";
  var READY = "streamlit:componentReady";
  var SET_VALUE = "streamlit:setComponentValue";
  var SET_HEIGHT = "streamlit:setFrameHeight";
  var lastHtml = null;
  var lastHeight = -1;

  function send(type, data) {
    var message = { isStreamlitMessage: true, type: type };
    if (data) {
      for (var key in data) {
        if (Object.prototype.hasOwnProperty.call(data, key)) {
          message[key] = data[key];
        }
      }
    }
    window.parent.postMessage(message, "*");
  }

  function setHeight() {
    var doc = document.documentElement;
    var height = Math.ceil(Math.max(
      document.body.scrollHeight,
      document.body.offsetHeight,
      doc.scrollHeight,
      doc.offsetHeight
    ));
    if (height < 1) {
      return;
    }
    if (height !== lastHeight) {
      lastHeight = height;
      send(SET_HEIGHT, { height: height });
    }
  }

  function bindForm() {
    var form = document.querySelector("form");
    if (!form || form.dataset.pertussisBound === "1") {
      return;
    }
    form.dataset.pertussisBound = "1";
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var checked = Array.prototype.slice
        .call(document.querySelectorAll('input[name="gejala"]:checked'))
        .map(function (input) { return input.value; });
      send(SET_VALUE, {
        dataType: "json",
        value: {
          gejala: checked,
          submitted: true,
          nonce: String(Date.now()) + "-" + Math.random().toString(36).slice(2)
        }
      });
      setTimeout(setHeight, 0);
    });
  }

  function render(event) {
    var data = event.data;
    if (!data || data.type !== RENDER) {
      return;
    }
    var args = data.args || {};
    if (typeof args.html === "string" && args.html !== lastHtml) {
      lastHtml = args.html;
      document.getElementById("root").innerHTML = args.html;
      bindForm();
    }
    requestAnimationFrame(setHeight);
    setTimeout(setHeight, 50);
    setTimeout(setHeight, 250);
  }

  window.addEventListener("message", render);
  window.addEventListener("resize", setHeight);

  if (window.ResizeObserver) {
    new ResizeObserver(setHeight).observe(document.getElementById("root"));
  }

  send(READY, { apiVersion: 1 });
  setTimeout(function () {
    send(READY, { apiVersion: 1 });
  }, 300);
})();
</script>
</body>
</html>
"""


def _get_component():
    component_dir = Path(tempfile.gettempdir()) / "pertussis_streamlit_component"
    component_dir.mkdir(parents=True, exist_ok=True)
    (component_dir / "index.html").write_text(COMPONENT_SHELL, encoding="utf-8")
    return components.declare_component("pertussis_component", path=str(component_dir))


# ---------------------------------------------------------------------------
# Aplikasi Streamlit
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Sistem Informasi Gejala Pertussis",
    layout="wide",
    initial_sidebar_state="collapsed",
)

pertussis_component = _get_component()

# Menyembunyikan chrome Streamlit dan padding bawaan agar halaman asli tampil
# penuh. CSS desain asli di dalam komponen tidak diubah.
st.markdown(
    """
<style>
  header[data-testid="stHeader"],
  [data-testid="stToolbar"],
  [data-testid="stDecoration"],
  [data-testid="stStatusWidget"],
  [data-testid="stAppDeployButton"],
  #MainMenu,
  footer {
    display: none !important;
  }
  .stApp,
  [data-testid="stAppViewContainer"],
  [data-testid="stMain"] {
    background: #f4f7fa !important;
  }
  .block-container,
  [data-testid="stMainBlockContainer"],
  [data-testid="stBottomBlockContainer"] {
    padding: 0 !important;
    max-width: 100% !important;
  }
  [data-testid="stVerticalBlock"] {
    gap: 0 !important;
  }
  [data-testid="stCustomComponentV1"] {
    width: 100% !important;
  }
  [data-testid="stCustomComponentV1"] iframe {
    display: block !important;
    width: 100% !important;
  }
</style>
""",
    unsafe_allow_html=True,
)

if "pertussis_form" not in st.session_state:
    st.session_state.pertussis_form = {
        "gejala": [],
        "submitted": False,
        "nonce": None,
    }

form_state = st.session_state.pertussis_form
selected = form_state["gejala"]
submitted = form_state["submitted"]
results = calculate_results(selected)

component_value = pertussis_component(
    html=render_page(selected, submitted, results),
    height=1200,
    key="pertussis_html_form",
)

if isinstance(component_value, dict):
    value_nonce = component_value.get("nonce")
    if value_nonce is not None and value_nonce != form_state["nonce"]:
        selected = [
            code for code in component_value.get("gejala", []) if code in GEJALA
        ]
        st.session_state.pertussis_form = {
            "gejala": selected,
            "submitted": True,
            "nonce": value_nonce,
        }
        st.rerun()
