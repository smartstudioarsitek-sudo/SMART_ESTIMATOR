import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# ==========================================
# 1. KONFIGURASI SISTEM & STYLE
# ==========================================
st.set_page_config(
    page_title="RAB SmartStudio - Pro System",
    page_icon="🏗️",
    layout="wide"
)

# Custom CSS untuk meniru nuansa "Clean & Professional" dari kode asli
st.markdown("""
    <style>
    .main { background-color: #f1f5f9; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 4px;
        color: #64748b;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e3a8a !important;
        color: white !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 26px;
        color: #1e3a8a;
        font-weight: bold;
    }
    .css-1r6slb0 { background-color: white; border: 1px solid #e2e8f0; padding: 20px; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. INISIALISASI DATA (SESSION STATE)
# ==========================================
if 'project_data' not in st.session_state:
    # Mengonversi Data JS 'db' Anda ke Python Dictionary
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
        # Data BOQ/RAB (Versi DataFrame-ready)
        "boq": [
            # I. PERSIAPAN
            {"Divisi": "I. PERSIAPAN", "Uraian": "Pengukuran & Bouwplank", "Satuan": "m2", "Volume": 425.18, "HargaSatuan": 15000},
            {"Divisi": "I. PERSIAPAN", "Uraian": "Pembersihan Lahan", "Satuan": "m2", "Volume": 425.18, "HargaSatuan": 12500},
            {"Divisi": "I. PERSIAPAN", "Uraian": "Direksi Keet & Gudang", "Satuan": "Ls", "Volume": 1.0, "HargaSatuan": 15000000},
            {"Divisi": "I. PERSIAPAN", "Uraian": "Air & Listrik Kerja", "Satuan": "Ls", "Volume": 1.0, "HargaSatuan": 7500000},
            # II. TANAH
            {"Divisi": "II. TANAH", "Uraian": "Galian Tanah Pondasi", "Satuan": "m3", "Volume": 166.37, "HargaSatuan": 85000},
            {"Divisi": "II. TANAH", "Uraian": "Urugan Pasir Bawah", "Satuan": "m3", "Volume": 7.76, "HargaSatuan": 220000},
            {"Divisi": "II. TANAH", "Uraian": "Pasangan Batu Kali", "Satuan": "m3", "Volume": 57.83, "HargaSatuan": 950000},
            {"Divisi": "II. TANAH", "Uraian": "Beton Footplate (K-250)", "Satuan": "m3", "Volume": 15.90, "HargaSatuan": 1350000},
            {"Divisi": "II. TANAH", "Uraian": "Beton Sloof", "Satuan": "m3", "Volume": 15.52, "HargaSatuan": 1450000},
            # III. LANTAI 1
            {"Divisi": "III. LANTAI 1", "Uraian": "Beton Kolom Lt 1", "Satuan": "m3", "Volume": 12.18, "HargaSatuan": 4500000}, # Include Besi+Bekisting (Average)
            {"Divisi": "III. LANTAI 1", "Uraian": "Dinding Bata Ringan", "Satuan": "m2", "Volume": 397.27, "HargaSatuan": 135000},
            {"Divisi": "III. LANTAI 1", "Uraian": "Plesteran Dinding", "Satuan": "m2", "Volume": 794.54, "HargaSatuan": 65000},
            {"Divisi": "III. LANTAI 1", "Uraian": "Lantai Granit Utama", "Satuan": "m2", "Volume": 239.48, "HargaSatuan": 285000},
            # IV. LANTAI 2
            {"Divisi": "IV. LANTAI 2", "Uraian": "Beton Balok Lt 2", "Satuan": "m3", "Volume": 21.28, "HargaSatuan": 4800000},
            {"Divisi": "IV. LANTAI 2", "Uraian": "Beton Plat Lantai", "Satuan": "m3", "Volume": 33.80, "HargaSatuan": 4200000},
            {"Divisi": "IV. LANTAI 2", "Uraian": "Dinding Bata Ringan", "Satuan": "m2", "Volume": 383.15, "HargaSatuan": 135000},
            {"Divisi": "IV. LANTAI 2", "Uraian": "Lantai Granit Lt 2", "Satuan": "m2", "Volume": 268.05, "HargaSatuan": 285000},
        ],
        # Data Harga Dasar (Basic Prices)
        "basic": [
            {"Kode": "L01", "Kategori": "Upah", "Nama": "Pekerja", "Sat": "OH", "Harga": 120000},
            {"Kode": "L02", "Kategori": "Upah", "Nama": "Tukang Batu", "Sat": "OH", "Harga": 160000},
            {"Kode": "M01", "Kategori": "Material", "Nama": "Semen Portland", "Sat": "Zak", "Harga": 68000},
            {"Kode": "M04", "Kategori": "Material", "Nama": "Pasir Beton", "Sat": "m3", "Harga": 350000},
            {"Kode": "M16", "Kategori": "Material", "Nama": "Besi Beton", "Sat": "Kg", "Harga": 14500},
        ]
    }

# ==========================================
# 3. LOGIC ENGINE (CALCULATOR)
# ==========================================
def run_calculation():
    """
    Fungsi ini menghitung ulang seluruh RAB tanpa mengubah state secara langsung
    untuk mencegah Infinite Loop pada Streamlit.
    """
    info = st.session_state.project_data['info']
    
    # Load Dataframe
    df = pd.DataFrame(st.session_state.project_data['boq'])
    
    # Sanitasi Input (Pastikan Angka)
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce').fillna(0)
    df['HargaSatuan'] = pd.to_numeric(df['HargaSatuan'], errors='coerce').fillna(0)
    
    # Hitung Total Per Item
    df['JumlahHarga'] = df['Volume'] * df['HargaSatuan']
    
    # Hitung Rekap
    real_cost = df['JumlahHarga'].sum()
    fee_val = real_cost * (info['fee_pct'] / 100)
    subtotal = real_cost + fee_val
    tax_val = subtotal * (info['tax_pct'] / 100)
    grand_total = subtotal + tax_val
    
    return df, real_cost, fee_val, subtotal, tax_val, grand_total

def terbilang(n):
    # Fungsi sederhana terbilang (placeholder)
    return f"{n:,.0f} (Rupiah)"

def fmt_idr(n):
    return f"Rp {n:,.0f}".replace(",", ".")

# ==========================================
# 4. UI SIDEBAR (SETTINGS)
# ==========================================
with st.sidebar:
    st.title("⚙️ Project Settings")
    
    # Shortcut variables
    info = st.session_state.project_data['info']
    
    info['name'] = st.text_input("Nama Kegiatan", info['name'])
    info['loc'] = st.text_input("Lokasi", info['loc'])
    info['year'] = st.text_input("Tahun", info['year'])
    st.divider()
    info['owner'] = st.text_input("Pemilik (Owner)", info['owner'])
    info['cont'] = st.text_input("Kontraktor", info['cont'])
    st.divider()
    
    c1, c2 = st.columns(2)
    with c1: info['fee_pct'] = st.number_input("Fee (%)", value=info['fee_pct'])
    with c2: info['tax_pct'] = st.number_input("PPN (%)", value=info['tax_pct'])
    
    if st.button("💾 Reset Data"):
        st.session_state.clear()
        st.rerun()

# ==========================================
# 5. MAIN APPLICATION
# ==========================================

# Run Calculation First (Data Driven)
df_rab, real_cost, fee_val, subtotal, tax_val, grand_total = run_calculation()

# Header
c_head1, c_head2 = st.columns([1, 4])
with c_head1:
    st.markdown('<div style="background:#1e3a8a;color:white;width:50px;height:50px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:24px;">S</div>', unsafe_allow_html=True)
with c_head2:
    st.markdown(f"**SMART STUDIO ESTIMATOR**\n\n<span style='color:grey;font-size:12px;'>Project: {info['name']}</span>", unsafe_allow_html=True)

st.markdown("---")

# Tabs Navigation
tabs = st.tabs(["📑 0. Project Identity", "📊 1. Rekapitulasi", "📝 2. RAB Detail", "💰 3. Harga Dasar"])

# --- TAB 0: COVER ---
with tabs[0]:
    st.markdown(f"""
    <div style="background:white; padding:40px; border:2px solid #e2e8f0; text-align:center; border-radius:10px;">
        <h2 style="color:#0f172a; margin-bottom:0;">RENCANA ANGGARAN BIAYA</h2>
        <p style="letter-spacing:3px; font-weight:bold; color:#94a3b8; font-size:12px;">ENGINEERING ESTIMATE (EE)</p>
        <hr style="margin:20px 0;">
        
        <div style="display:grid; grid-template-columns:1fr 1fr; text-align:left; gap:20px; margin-bottom:40px;">
            <div>
                <p style="font-size:10px; font-weight:bold; color:#94a3b8;">KEGIATAN</p>
                <p style="font-weight:bold;">{info['name']}</p>
            </div>
            <div>
                <p style="font-size:10px; font-weight:bold; color:#94a3b8;">LOKASI</p>
                <p style="font-weight:bold;">{info['loc']}</p>
            </div>
        </div>
        
        <div style="background:#0f172a; color:white; padding:30px; border-radius:12px; margin-bottom:40px;">
            <p style="margin:0; font-size:12px; letter-spacing:2px;">TOTAL ESTIMASI BIAYA</p>
            <h1 style="margin:10px 0; font-size:48px; color:#fbbf24;">{fmt_idr(grand_total)}</h1>
            <p style="font-style:italic; font-size:14px; opacity:0.7;">(Termasuk Jasa {info['fee_pct']}% & PPN {info['tax_pct']}%)</p>
        </div>
        
        <div style="display:flex; justify-content:space-between; padding:0 50px;">
            <div style="text-align:center;">
                <p style="font-size:10px; font-weight:bold; color:#64748b;">DISETUJUI OLEH:</p>
                <br><br><br>
                <p style="border-bottom:1px solid #000; font-weight:bold; padding-bottom:5px;">{info['owner']}</p>
                <p style="font-size:12px;">OWNER</p>
            </div>
            <div style="text-align:center;">
                <p style="font-size:10px; font-weight:bold; color:#64748b;">DIBUAT OLEH:</p>
                <br><br><br>
                <p style="border-bottom:1px solid #000; font-weight:bold; padding-bottom:5px;">{info['cont']}</p>
                <p style="font-size:12px;">KONTRAKTOR</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- TAB 1: REKAPITULASI ---
with tabs[1]:
    col_metrics = st.columns(3)
    col_metrics[0].metric("Total Konstruksi", fmt_idr(real_cost))
    col_metrics[1].metric(f"Jasa ({info['fee_pct']}%)", fmt_idr(fee_val))
    col_metrics[2].metric("Grand Total (+PPN)", fmt_idr(grand_total))
    
    st.subheader("Rekapitulasi Per Divisi")
    
    # Grouping logic
    rekap_df = df_rab.groupby('Divisi')['JumlahHarga'].sum().reset_index()
    rekap_df['Bobot (%)'] = (rekap_df['JumlahHarga'] / real_cost * 100).fillna(0)
    
    st.dataframe(
        rekap_df,
        column_config={
            "Divisi": st.column_config.TextColumn("Uraian Pekerjaan"),
            "JumlahHarga": st.column_config.NumberColumn("Jumlah Harga (Rp)", format="Rp %d"),
            "Bobot (%)": st.column_config.ProgressColumn("Bobot", format="%.2f%%", min_value=0, max_value=100)
        },
        use_container_width=True,
        hide_index=True
    )

# --- TAB 2: RAB DETAIL (THE CORE) ---
with tabs[2]:
    st.info("💡 **Petunjuk:** Ubah angka pada kolom **Volume** atau **Harga Satuan**. Tekan Enter untuk update Total.")
    
    # Editable Dataframe
    edited_df = st.data_editor(
        df_rab,
        column_config={
            "Divisi": st.column_config.SelectboxColumn("Divisi", options=["I. PERSIAPAN", "II. TANAH", "III. LANTAI 1", "IV. LANTAI 2", "V. ATAP"], width="medium"),
            "Uraian": st.column_config.TextColumn("Uraian Pekerjaan", width="large"),
            "Volume": st.column_config.NumberColumn("Vol", format="%.2f"),
            "Satuan": st.column_config.TextColumn("Sat", width="small"),
            "HargaSatuan": st.column_config.NumberColumn("Harga Satuan", format="Rp %d"),
            "JumlahHarga": st.column_config.NumberColumn("Jumlah Harga", format="Rp %d", disabled=True) # Read-only calculated field
        },
        num_rows="dynamic",
        use_container_width=True,
        key="editor_rab"
    )
    
    # Save Logic (Anti-Circular Loop)
    # Kita hanya menyimpan kolom INPUT, bukan kolom HASIL (JumlahHarga)
    if edited_df is not None:
        cols_to_save = ["Divisi", "Uraian", "Satuan", "Volume", "HargaSatuan"]
        # Konversi ke list of dicts untuk disimpan ke session state
        st.session_state.project_data['boq'] = edited_df[cols_to_save].to_dict('records')

# --- TAB 3: HARGA DASAR ---
with tabs[3]:
    st.subheader("Database Harga Dasar (Material & Upah)")
    basic_df = pd.DataFrame(st.session_state.project_data['basic'])
    
    edited_basic = st.data_editor(
        basic_df,
        column_config={
            "Kode": st.column_config.TextColumn(disabled=True),
            "Harga": st.column_config.NumberColumn(format="Rp %d")
        },
        num_rows="dynamic",
        use_container_width=True,
        key="editor_basic"
    )
    
    if edited_basic is not None:
        st.session_state.project_data['basic'] = edited_basic.to_dict('records')

# Footer
st.markdown("---")
st.markdown(f"<div style='text-align:center; color:#94a3b8; font-size:12px;'>Generated by GEMS SmartStudio Python Engine | {datetime.now().strftime('%d %B %Y')}</div>", unsafe_allow_html=True)
