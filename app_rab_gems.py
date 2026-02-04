import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# ==========================================
# 1. KONFIGURASI SISTEM
# ==========================================
st.set_page_config(
    page_title="GEMS SmartStudio PRO",
    page_icon="🏗️",
    layout="wide"
)

# Style CSS agar tampilan gagah
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    div[data-testid="stMetricValue"] { font-size: 20px; color: #1e3a8a; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: #ffffff; border-radius: 4px; }
    .stTabs [aria-selected="true"] { background-color: #1e3a8a !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. INISIALISASI DATA (SESSION STATE)
# ==========================================
if 'project_data' not in st.session_state:
    st.session_state.project_data = {
        "info": {
            "name": "PROYEK RUKO 2 LANTAI",
            "loc": "DENPASAR - BALI",
            "year": "2026",
            "owner": "BAPAK RIO",
            "cont": "SMART STUDIO",
            "fee_pct": 10.0,
            "tax_pct": 11.0
        },
        # Kita gunakan struktur dictionary list agar mudah dibaca pandas
        "boq": [
            {"No": 1, "Divisi": "I. PERSIAPAN", "Uraian": "Pengukuran & Bouwplank", "Satuan": "m2", "Volume": 425.18, "Harga Satuan": 15000},
            {"No": 2, "Divisi": "I. PERSIAPAN", "Uraian": "Direksi Keet & Gudang", "Satuan": "Ls", "Volume": 1.0, "Harga Satuan": 15000000},
            {"No": 3, "Divisi": "II. TANAH", "Uraian": "Galian Tanah Pondasi", "Satuan": "m3", "Volume": 166.37, "Harga Satuan": 75000},
            {"No": 4, "Divisi": "II. TANAH", "Uraian": "Urugan Pasir Bawah", "Satuan": "m3", "Volume": 7.76, "Harga Satuan": 220000},
            {"No": 5, "Divisi": "III. LANTAI 1", "Uraian": "Beton Kolom Lt 1", "Satuan": "m3", "Volume": 12.18, "Harga Satuan": 4500000},
            {"No": 6, "Divisi": "III. LANTAI 1", "Uraian": "Dinding Bata Ringan", "Satuan": "m2", "Volume": 397.27, "Harga Satuan": 125000},
        ],
        "basic_prices": [
            {"Kode": "L01", "Kategori": "Upah", "Nama": "Pekerja", "Sat": "OH", "Harga": 120000},
            {"Kode": "M01", "Kategori": "Material", "Nama": "Semen PC 50kg", "Sat": "Zak", "Harga": 68000},
            {"Kode": "M16", "Kategori": "Material", "Nama": "Besi Beton", "Sat": "Kg", "Harga": 14500},
        ]
    }

# Fungsi Helper Format Rupiah
def fmt_idr(n):
    return f"Rp {n:,.0f}".replace(",", ".")

# ==========================================
# 3. SIDEBAR (INPUT DATA UMUM)
# ==========================================
with st.sidebar:
    st.title("⚙️ Project Settings")
    
    # Akses langsung ke dictionary info
    info = st.session_state.project_data['info']
    
    info['name'] = st.text_input("Nama Kegiatan", info['name'])
    info['owner'] = st.text_input("Owner", info['owner'])
    info['cont'] = st.text_input("Kontraktor", info['cont'])
    
    st.divider()
    info['fee_pct'] = st.number_input("Jasa Kontraktor (%)", value=info['fee_pct'], step=0.5)
    info['tax_pct'] = st.number_input("PPN (%)", value=info['tax_pct'], step=1.0)
    
    if st.button("♻️ Reset Data Default"):
        del st.session_state['project_data']
        st.rerun()

# ==========================================
# 4. LOGIC ENGINE (DIPISAH DARI RENDER)
# ==========================================
# Ambil data mentah dari state
df_boq = pd.DataFrame(st.session_state.project_data['boq'])

# Pastikan tipe data benar (Anti-Error jika user input teks)
df_boq['Volume'] = pd.to_numeric(df_boq['Volume'], errors='coerce').fillna(0)
df_boq['Harga Satuan'] = pd.to_numeric(df_boq['Harga Satuan'], errors='coerce').fillna(0)

# HITUNG TOTAL (Di memori sementara, tidak langsung save ke state input untuk hindari loop)
df_boq['Total'] = df_boq['Volume'] * df_boq['Harga Satuan']

# Hitung Rekap Global
real_cost = df_boq['Total'].sum()
fee_val = real_cost * (info['fee_pct'] / 100)
subtotal = real_cost + fee_val
tax_val = subtotal * (info['tax_pct'] / 100)
grand_total = subtotal + tax_val

# ==========================================
# 5. MAIN INTERFACE
# ==========================================
st.title("🏗️ GEMS SmartStudio RAB")
st.write(f"**Proyek:** {info['name']} | **Owner:** {info['owner']}")

# Tab Navigasi
t_cover, t_rekap, t_rab, t_basic = st.tabs(["0. Cover", "1. Rekapitulasi", "2. RAB Detail", "3. Harga Dasar"])

# --- TAB 0: COVER ---
with t_cover:
    st.markdown(f"""
    <div style="text-align: center; border: 4px double #1e3a8a; padding: 30px; border-radius: 10px; background: white;">
        <h2 style="color: #1e3a8a; margin-bottom: 5px;">RENCANA ANGGARAN BIAYA</h2>
        <p style="letter-spacing: 2px; font-weight: bold; color: #64748b;">ENGINEERING ESTIMATE</p>
        <hr style="margin: 20px 0;">
        <h1 style="font-size: 42px; color: #0f172a; margin: 10px 0;">{fmt_idr(grand_total)}</h1>
        <p style="color: #64748b; font-style: italic;">(Termasuk Jasa {info['fee_pct']}% & PPN {info['tax_pct']}%)</p>
        <br>
        <div style="display: flex; justify-content: space-around; margin-top: 30px;">
            <div><p>Disetujui Owner:</p><br><b>{info['owner']}</b></div>
            <div><p>Dibuat Kontraktor:</p><br><b>{info['cont']}</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- TAB 1: REKAPITULASI ---
with t_rekap:
    c1, c2, c3 = st.columns(3)
    c1.metric("Biaya Konstruksi", fmt_idr(real_cost))
    c2.metric("Jasa & Pajak", fmt_idr(fee_val + tax_val))
    c3.metric("GRAND TOTAL", fmt_idr(grand_total))
    
    st.subheader("Bobot Pekerjaan")
    # Grouping Data
    rekap_div = df_boq.groupby('Divisi')['Total'].sum().reset_index()
    rekap_div['Bobot (%)'] = (rekap_div['Total'] / real_cost * 100).fillna(0)
    
    st.dataframe(
        rekap_div,
        column_config={
            "Total": st.column_config.NumberColumn(format="Rp %d"),
            "Bobot (%)": st.column_config.NumberColumn(format="%.2f %%")
        },
        use_container_width=True,
        hide_index=True
    )

# --- TAB 2: RAB DETAIL (INTI MASALAH MUTER ADA DISINI - SUDAH DIPERBAIKI) ---
with t_rab:
    st.info("💡 Edit **Volume** atau **Harga Satuan** di tabel. Tekan Enter untuk update perhitungan.")
    
    # 1. Tampilkan Data Editor
    edited_df = st.data_editor(
        df_boq, # Kita masukkan dataframe yang SUDAH memiliki kolom Total (hasil hitungan di atas)
        column_config={
            "No": st.column_config.NumberColumn(width=50, disabled=True),
            "Divisi": st.column_config.SelectboxColumn(options=["I. PERSIAPAN", "II. TANAH", "III. LANTAI 1", "IV. LANTAI 2", "V. ATAP"], required=True),
            "Uraian": st.column_config.TextColumn(width="large", required=True),
            "Volume": st.column_config.NumberColumn(required=True),
            "Harga Satuan": st.column_config.NumberColumn(required=True, format="Rp %d"),
            "Total": st.column_config.NumberColumn(disabled=True, format="Rp %d") # Kolom Total KITA KUNCI agar user tidak bingung
        },
        num_rows="dynamic",
        use_container_width=True,
        key="editor_rab"
    )
    
    # 2. SIMPAN HASIL EDIT KE SESSION STATE
    # Trik Anti-Muter: Kita hanya simpan jika ada perubahan pada kolom INPUT (bukan kolom hasil hitungan)
    # Kita convert balik ke list of dicts untuk disimpan ke session_state.project_data['boq']
    # Tapi kita BUANG kolom 'Total' sebelum disimpan, supaya 'Total' selalu dihitung ulang fresh dari Volume * Harga
    
    input_cols = ["No", "Divisi", "Uraian", "Satuan", "Volume", "Harga Satuan"]
    
    # Cek apakah perlu update state
    # (Streamlit otomatis handle update UI via 'key', tapi kita perlu update data source 'project_data' untuk tab lain)
    if edited_df is not None:
        # Ambil hanya kolom input
        clean_data = edited_df[input_cols].to_dict('records')
        st.session_state.project_data['boq'] = clean_data

# --- TAB 3: HARGA DASAR ---
with t_basic:
    df_basic = pd.DataFrame(st.session_state.project_data['basic_prices'])
    edited_basic = st.data_editor(
        df_basic,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_basic"
    )
    # Simpan balik
    if edited_basic is not None:
        st.session_state.project_data['basic_prices'] = edited_basic.to_dict('records')

# Footer
st.markdown("---")
st.caption("GEMS Grandmaster System | Anti-Halusinasi Engine V3.1")
