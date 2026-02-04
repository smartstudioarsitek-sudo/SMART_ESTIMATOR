import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# ==========================================
# 1. KONFIGURASI SISTEM & STYLE GEMS
# ==========================================
st.set_page_config(
    page_title="GEMS SmartStudio - Estimator System",
    page_icon="🏗️",
    layout="wide"
)

# Custom CSS untuk tampilan "Gagah" khas GEMS
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 10px 20px;
        border-radius: 5px 5px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0f172a !important;
        color: white !important;
    }
    div[data-testid="stMetricValue"] { font-size: 24px; font-weight: bold; color: #1e40af; }
    .footer-gems { text-align: center; color: #94a3b8; font-size: 12px; margin-top: 50px; border-top: 1px solid #e2e8f0; padding-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATA INITIALIZATION (ANTI-WIPE)
# ==========================================
# Menggunakan session_state agar data tetap ada selama aplikasi running
if 'project_data' not in st.session_state:
    st.session_state.project_data = {
        "info": {
            "name": "PEMBANGUNAN RUKO 2 LANTAI (4 UNIT)",
            "loc": "DENPASAR - BALI",
            "year": "2026",
            "owner": "BAPAK RIO",
            "cont": "SMART STUDIO",
            "fee_pct": 10.0,
            "tax_pct": 11.0
        },
        "boq": pd.DataFrame([
            {"No": 1, "Divisi": "I. PERSIAPAN", "Uraian": "Pengukuran & Bouwplank", "Satuan": "m2", "Volume": 425.18, "Harga Satuan": 15000, "Total": 0},
            {"No": 2, "Divisi": "I. PERSIAPAN", "Uraian": "Direksi Keet & Gudang", "Satuan": "Ls", "Volume": 1.0, "Harga Satuan": 15000000, "Total": 0},
            {"No": 3, "Divisi": "II. TANAH", "Uraian": "Galian Tanah Pondasi", "Satuan": "m3", "Volume": 166.37, "Harga Satuan": 75000, "Total": 0},
            {"No": 4, "Divisi": "II. TANAH", "Uraian": "Urugan Pasir Bawah", "Satuan": "m3", "Volume": 7.76, "Harga Satuan": 220000, "Total": 0},
            {"No": 5, "Divisi": "III. LANTAI 1", "Uraian": "Beton Kolom Lt 1", "Satuan": "m3", "Volume": 12.18, "Harga Satuan": 4500000, "Total": 0},
            {"No": 6, "Divisi": "III. LANTAI 1", "Uraian": "Dinding Bata Ringan", "Satuan": "m2", "Volume": 397.27, "Harga Satuan": 125000, "Total": 0},
        ]),
        "basic_prices": pd.DataFrame([
            {"Kode": "L01", "Kategori": "Upah", "Nama": "Pekerja", "Sat": "OH", "Harga": 120000},
            {"Kode": "M01", "Kategori": "Material", "Nama": "Semen PC 50kg", "Sat": "Zak", "Harga": 68000},
            {"Kode": "M16", "Kategori": "Material", "Nama": "Besi Beton", "Sat": "Kg", "Harga": 14500},
        ])
    }

# ==========================================
# 3. CORE LOGIC CALCULATOR (ANTI-BUG)
# ==========================================
def run_calculation():
    df = st.session_state.project_data['boq']
    # Pastikan tipe data numerik untuk kalkulasi
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce').fillna(0)
    df['Harga Satuan'] = pd.to_numeric(df['Harga Satuan'], errors='coerce').fillna(0)
    
    # Hitung Jumlah per baris
    df['Total'] = df['Volume'] * df['Harga Satuan']
    
    # Hitung Rekapitulasi Akhir
    real_cost = df['Total'].sum()
    fee_val = real_cost * (st.session_state.project_data['info']['fee_pct'] / 100)
    subtotal = real_cost + fee_val
    tax_val = subtotal * (st.session_state.project_data['info']['tax_pct'] / 100)
    grand_total = subtotal + tax_val
    
    return real_cost, fee_val, subtotal, tax_val, grand_total

def fmt_idr(n):
    return f"Rp {n:,.0f}".replace(",", ".")

# ==========================================
# 4. SIDEBAR SETTINGS
# ==========================================
with st.sidebar:
    st.title("⚙️ Project Settings")
    info = st.session_state.project_data['info']
    info['name'] = st.text_input("Nama Kegiatan", info['name'])
    info['owner'] = st.text_input("Pemilik (Owner)", info['owner'])
    info['cont'] = st.text_input("Kontraktor", info['cont'])
    
    st.divider()
    st.subheader("Parameter Biaya")
    info['fee_pct'] = st.number_input("Jasa Kontraktor (%)", value=info['fee_pct'], step=0.5)
    info['tax_pct'] = st.number_input("PPN (%)", value=info['tax_pct'], step=1.0)
    
    if st.button("💾 Simpan Data Proyek", use_container_width=True):
        st.success("Data berhasil diamankan ke Session State!")

# ==========================================
# 5. MAIN INTERFACE (TABS)
# ==========================================
st.title("👑 GEMS SmartStudio Estimator")
st.caption(f"Sistem Perhitungan Engineering Estimate (EE) - {info['name']}")

# Run Calculation
real_cost, fee_val, subtotal, tax_val, grand_total = run_calculation()

tab_cover, tab_rekap, tab_rab, tab_basic = st.tabs([
    "📑 0. Cover", "📊 1. Rekapitulasi", "🏗️ 2. RAB Detail", "💰 3. Harga Dasar"
])

# --- TAB 0: COVER ---
with tab_cover:
    st.markdown(f"""
    <div style="background-color: white; padding: 40px; border: 2px solid #0f172a; border-radius: 10px; text-align: center;">
        <h1 style="color: #0f172a;">RENCANA ANGGARAN BIAYA (RAB)</h1>
        <hr>
        <div style="display: grid; grid-template-columns: 1fr 1fr; text-align: left; margin: 30px 0;">
            <div>
                <p><b>NAMA KEGIATAN:</b><br>{info['name']}</p>
                <p><b>LOKASI:</b><br>{info['loc']}</p>
            </div>
            <div>
                <p><b>OWNER:</b><br>{info['owner']}</p>
                <p><b>TAHUN:</b><br>{info['year']}</p>
            </div>
        </div>
        <div style="background-color: #0f172a; color: white; padding: 20px; border-radius: 8px;">
            <p style="margin:0;">ESTIMASI TOTAL BIAYA</p>
            <h1 style="margin:0; color: #fbbf24;">{fmt_idr(grand_total)}</h1>
        </div>
        <div style="margin-top: 50px; display: flex; justify-content: space-between;">
            <div style="border-top: 1px solid black; width: 200px; padding-top: 10px;">{info['owner']}<br>(Owner)</div>
            <div style="border-top: 1px solid black; width: 200px; padding-top: 10px;">{info['cont']}<br>(Kontraktor)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- TAB 1: REKAPITULASI ---
with tab_rekap:
    st.header("Ringkasan Eksekutif")
    c1, c2, c3 = st.columns(3)
    c1.metric("Konstruksi (Net)", fmt_idr(real_cost))
    c2.metric(f"Jasa ({info['fee_pct']}%)", fmt_idr(fee_val))
    c3.metric("Grand Total", fmt_idr(grand_total), help="Termasuk PPN")

    # Dataframe Rekap per Divisi
    df_boq = st.session_state.project_data['boq']
    rekap_divisi = df_boq.groupby('Divisi')['Total'].sum().reset_index()
    rekap_divisi['Bobot (%)'] = (rekap_divisi['Total'] / real_cost * 100).round(2)
    
    st.subheader("Tabel Rekapitulasi")
    st.table(rekap_divisi.style.format({
        'Total': lambda x: f"{x:,.0f}",
        'Bobot (%)': '{:.2f}%'
    }))

# --- TAB 2: RAB DETAIL ---
with tab_rab:
    st.header("Rincian Pekerjaan")
    st.info("Input jumlah volume atau harga satuan pada tabel di bawah ini. Total akan terupdate otomatis.")
    
    # Data Editor untuk manipulasi data tabel
    edited_boq = st.data_editor(
        st.session_state.project_data['boq'],
        column_config={
            "No": st.column_config.NumberColumn(disabled=True),
            "Divisi": st.column_config.SelectboxColumn("Divisi", options=["I. PERSIAPAN", "II. TANAH", "III. LANTAI 1", "IV. LANTAI 2", "V. ATAP"]),
            "Volume": st.column_config.NumberColumn(format="%.2f"),
            "Harga Satuan": st.column_config.NumberColumn(format="Rp %d"),
            "Total": st.column_config.NumberColumn(format="Rp %d", disabled=True)
        },
        num_rows="dynamic",
        use_container_width=True,
        key="editor_rab"
    )
    
    # Simpan perubahan kembali ke session_state
    st.session_state.project_data['boq'] = edited_boq
    
    if st.button("🔄 Refresh Perhitungan"):
        st.rerun()

# --- TAB 3: HARGA DASAR ---
with tab_basic:
    st.header("Database Harga Dasar Material & Upah")
    st.data_editor(
        st.session_state.project_data['basic_prices'],
        num_rows="dynamic",
        use_container_width=True,
        key="editor_prices"
    )

# ==========================================
# 6. FOOTER
# ==========================================
st.markdown(f"""
    <div class="footer-gems">
        GEMS ENGINE X - Konstruksi Digital Bali 2026<br>
        Sistem ini ditenagai oleh Python Streamlit untuk akurasi Engineering Estimate tinggi.
    </div>
    """, unsafe_allow_html=True)
