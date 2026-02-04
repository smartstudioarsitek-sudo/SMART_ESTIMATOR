import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# ==========================================
# 1. PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="RAB SmartStudio PRO",
    page_icon="🏗️",
    layout="wide"
)

# Style CSS
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: white; border-radius: 4px; }
    .stTabs [aria-selected="true"] { background-color: #1e3a8a !important; color: white !important; }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #1e3a8a; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. INISIALISASI STATE (HANYA SEKALI)
# ==========================================
# Kita gunakan fungsi ini agar data tidak ter-reset saat muter-muter
def init_data():
    if 'project_data' not in st.session_state:
        st.session_state.project_data = {
            "info": {
                "name": "PEMBANGUNAN RUKO 2 LANTAI",
                "loc": "DENPASAR - BALI",
                "year": "2026",
                "owner": "BAPAK RIO",
                "cont": "SMART STUDIO",
                "fee_pct": 10.0,
                "tax_pct": 11.0
            },
            # PERHATIKAN: TIDAK ADA KOLOM 'TOTAL' ATAU 'JUMLAH HARGA' DISINI
            # HANYA KOLOM INPUT MURNI AGAR TIDAK LOOPING
            "boq": [
                {"Divisi": "I. PERSIAPAN", "Uraian": "Pengukuran & Bouwplank", "Satuan": "m2", "Volume": 425.18, "HargaSatuan": 15000},
                {"Divisi": "I. PERSIAPAN", "Uraian": "Direksi Keet & Gudang", "Satuan": "Ls", "Volume": 1.0, "HargaSatuan": 15000000},
                {"Divisi": "II. TANAH", "Uraian": "Galian Tanah Pondasi", "Satuan": "m3", "Volume": 166.37, "HargaSatuan": 85000},
                {"Divisi": "II. TANAH", "Uraian": "Urugan Pasir Bawah", "Satuan": "m3", "Volume": 7.76, "HargaSatuan": 220000},
                {"Divisi": "III. LANTAI 1", "Uraian": "Beton Kolom Lt 1", "Satuan": "m3", "Volume": 12.18, "HargaSatuan": 4500000},
                {"Divisi": "III. LANTAI 1", "Uraian": "Dinding Bata Ringan", "Satuan": "m2", "Volume": 397.27, "HargaSatuan": 135000},
                {"Divisi": "IV. LANTAI 2", "Uraian": "Beton Balok Lt 2", "Satuan": "m3", "Volume": 21.28, "HargaSatuan": 4800000},
            ],
            "basic": [
                {"Kode": "L01", "Nama": "Pekerja", "Sat": "OH", "Harga": 120000},
                {"Kode": "M01", "Nama": "Semen PC 50kg", "Sat": "Zak", "Harga": 68000},
            ]
        }

# Panggil fungsi init
init_data()

# ==========================================
# 3. LOGIC ENGINE (HITUNG DI MEMORI)
# ==========================================
# Helper Format Rupiah
def fmt_idr(n):
    return f"Rp {n:,.0f}".replace(",", ".")

# Shortcut ke variable info
info = st.session_state.project_data['info']

# --- PROSES PERHITUNGAN (ANTI LOOP) ---
# 1. Ambil data mentah dari session state
df_raw = pd.DataFrame(st.session_state.project_data['boq'])

# 2. Pastikan tipe data numeric (PENTING: Mencegah error tipe data)
df_raw['Volume'] = pd.to_numeric(df_raw['Volume'], errors='coerce').fillna(0)
df_raw['HargaSatuan'] = pd.to_numeric(df_raw['HargaSatuan'], errors='coerce').fillna(0)

# 3. Hitung 'Total' di Dataframe SEMENTARA (df_calc)
# df_calc inilah yang akan ditampilkan, tapi TIDAK disimpan mentah-mentah
df_calc = df_raw.copy()
df_calc['JumlahHarga'] = df_calc['Volume'] * df_calc['HargaSatuan']

# 4. Hitung Grand Total
real_cost = df_calc['JumlahHarga'].sum()
fee_val = real_cost * (info['fee_pct'] / 100)
subtotal = real_cost + fee_val
tax_val = subtotal * (info['tax_pct'] / 100)
grand_total = subtotal + tax_val

# ==========================================
# 4. SIDEBAR
# ==========================================
with st.sidebar:
    st.title("⚙️ Pengaturan")
    info['name'] = st.text_input("Nama Proyek", info['name'])
    info['owner'] = st.text_input("Owner", info['owner'])
    info['cont'] = st.text_input("Kontraktor", info['cont'])
    st.divider()
    info['fee_pct'] = st.number_input("Fee (%)", value=info['fee_pct'])
    info['tax_pct'] = st.number_input("PPN (%)", value=info['tax_pct'])
    
    if st.button("🔴 Reset Data"):
        del st.session_state['project_data']
        st.rerun()

# ==========================================
# 5. MAIN UI TABS
# ==========================================
t_cover, t_rekap, t_rab, t_basic = st.tabs(["0. Cover", "1. Rekapitulasi", "2. RAB Detail", "3. Harga Dasar"])

# --- TAB COVER ---
with t_cover:
    st.markdown(f"""
    <div style="text-align:center; padding:30px; border:4px double #1e3a8a; border-radius:10px; background:white;">
        <h2 style="color:#1e3a8a;">RENCANA ANGGARAN BIAYA</h2>
        <hr>
        <h1>{fmt_idr(grand_total)}</h1>
        <p>Proyek: {info['name']} | Lokasi: {info['loc']}</p>
        <div style="display:flex; justify-content:space-around; margin-top:30px;">
            <div><b>Disetujui:</b><br><br>{info['owner']}</div>
            <div><b>Dibuat:</b><br><br>{info['cont']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- TAB REKAPITULASI ---
with t_rekap:
    c1, c2, c3 = st.columns(3)
    c1.metric("Real Cost", fmt_idr(real_cost))
    c2.metric("Jasa + PPN", fmt_idr(fee_val + tax_val))
    c3.metric("GRAND TOTAL", fmt_idr(grand_total))
    
    rekap_div = df_calc.groupby('Divisi')['JumlahHarga'].sum().reset_index()
    rekap_div['Bobot (%)'] = (rekap_div['JumlahHarga'] / real_cost * 100).fillna(0)
    st.dataframe(rekap_div, use_container_width=True, hide_index=True, column_config={"JumlahHarga": st.column_config.NumberColumn(format="Rp %d")})

# --- TAB RAB DETAIL (CRITICAL PART - JANGAN UBAH BAGIAN INI) ---
with t_rab:
    st.info("Ketik angka di tabel, tekan Enter. Perhitungan otomatis.")
    
    # KITA GUNAKAN LOGIKA KHUSUS DISINI
    edited_df = st.data_editor(
        df_calc, # Kita tampilkan dataframe yang SUDAH ada kolom JumlahHarga
        column_config={
            "Divisi": st.column_config.SelectboxColumn(options=["I. PERSIAPAN", "II. TANAH", "III. LANTAI 1", "IV. LANTAI 2", "V. ATAP"], required=True),
            "Uraian": st.column_config.TextColumn(width="large", required=True),
            "Volume": st.column_config.NumberColumn(required=True, format="%.2f"),
            "HargaSatuan": st.column_config.NumberColumn(required=True, format="Rp %d"),
            # KUNCI KOLOM JUMLAH HARGA AGAR TIDAK DIEDIT USER (INI MENCEGAH LOOP)
            "JumlahHarga": st.column_config.NumberColumn(disabled=True, format="Rp %d") 
        },
        num_rows="dynamic",
        use_container_width=True,
        key="editor_utama" # Key ini penting agar Streamlit melacak state
    )

    # --- THE FIX: CARA MENYIMPAN DATA AGAR TIDAK MUTER ---
    if edited_df is not None:
        # 1. Kita buang kolom 'JumlahHarga' yang dihitung otomatis tadi
        #    Karena kita hanya ingin menyimpan INPUT user (Volume & HargaSatuan)
        clean_df = edited_df.drop(columns=['JumlahHarga'])
        
        # 2. Konversi ke List of Dictionaries
        new_data = clean_df.to_dict('records')
        
        # 3. Cek apakah ada perbedaan dengan data lama?
        #    Hanya update session_state JIKA benar-benar ada data baru
        if new_data != st.session_state.project_data['boq']:
            st.session_state.project_data['boq'] = new_data
            st.rerun() # Force refresh seketika agar angka total update

# --- TAB HARGA DASAR ---
with t_basic:
    basic_df = pd.DataFrame(st.session_state.project_data['basic'])
    edited_basic = st.data_editor(basic_df, num_rows="dynamic", use_container_width=True, key="editor_basic")
    
    if edited_basic is not None:
        # Logika simpan yang sama
        new_basic = edited_basic.to_dict('records')
        if new_basic != st.session_state.project_data['basic']:
            st.session_state.project_data['basic'] = new_basic
            # Tidak perlu rerun disini jika tidak mempengaruhi RAB langsung, tapi aman jika dipakai

# Footer
st.markdown("---")
st.caption("GEMS Grandmaster System | Stable Core V4.0")
