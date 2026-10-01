import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# JUDUL DASHBOARD
# ==========================================

st.set_page_config(
    page_title="Dashboard Gempa Terkini",
    page_icon="🌋",
    layout="wide"
)

st.title("🌋 Dashboard Gempa Terkini")
st.write(
    "Dashboard ini menampilkan data gempa terkini "
    "yang diperoleh melalui API USGS."
)

# ==========================================
# API USGS
# ==========================================

url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"

response = requests.get(url)
data = response.json()

# ==========================================
# MEMBUAT DATAFRAME
# ==========================================

rows = []

for gempa in data["features"]:

    rows.append({
        "waktu": gempa["properties"]["time"],
        "lokasi": gempa["properties"]["place"],
        "magnitudo": gempa["properties"]["mag"],
        "kedalaman": gempa["geometry"]["coordinates"][2],
        "latitude": gempa["geometry"]["coordinates"][1],
        "longitude": gempa["geometry"]["coordinates"][0]
    })

df = pd.DataFrame(rows)

# ==========================================
# MENGUBAH WAKTU
# ==========================================

df["waktu"] = pd.to_datetime(
    df["waktu"],
    unit="ms"
)

# Urutkan berdasarkan waktu
df = df.sort_values("waktu").reset_index(drop=True)

# ==========================================
# ROLLING WINDOW
# ==========================================

df["rolling_magnitudo"] = (
    df["magnitudo"]
    .rolling(window=5)
    .mean()
)

# ==========================================
# INFORMASI UTAMA
# ==========================================

jumlah_gempa = len(df)
magnitudo_maks = df["magnitudo"].max()
rata_rata = df["magnitudo"].mean()

# ==========================================
# METRIC
# ==========================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "🔢 Jumlah Gempa",
        jumlah_gempa
    )

with col2:
    st.metric(
        "📈 Magnitudo Terbesar",
        f"{magnitudo_maks:.2f}"
    )

with col3:
    st.metric(
        "📊 Rata-rata Magnitudo",
        f"{rata_rata:.2f}"
    )

# ==========================================
# GRAFIK ROLLING WINDOW
# ==========================================

st.subheader("📈 Magnitudo dan Rolling Window")

fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(
    df["magnitudo"],
    label="Magnitudo"
)

ax.plot(
    df["rolling_magnitudo"],
    label="Rolling Mean 5 Gempa"
)

ax.set_xlabel("Urutan Gempa")
ax.set_ylabel("Magnitudo")
ax.set_title("Magnitudo Gempa dan Rolling Mean 5 Gempa")

ax.legend()
ax.grid()

st.pyplot(fig)

# ==========================================
# PETA GEMPA
# ==========================================

st.subheader("🗺️ Lokasi Gempa")

map_df = df[
    ["latitude", "longitude"]
].dropna()

st.map(
    map_df,
    latitude="latitude",
    longitude="longitude"
)

# ==========================================
# TABEL DATA
# ==========================================

st.subheader("📋 Data Gempa")

tabel = df[
    [
        "waktu",
        "lokasi",
        "magnitudo",
        "kedalaman",
        "latitude",
        "longitude",
        "rolling_magnitudo"
    ]
]

st.dataframe(
    tabel,
    use_container_width=True
)

# ==========================================
# TOMBOL REFRESH
# ==========================================

st.subheader("🔄 Perbarui Data")

if st.button("Ambil Data Terbaru"):

    st.rerun()

# ==========================================
# SUMBER DATA
# ==========================================

st.caption(
    "Sumber data: U.S. Geological Survey (USGS) "
    "| Data diambil melalui GeoJSON API"
)