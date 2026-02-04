import streamlit as st
import pandas as pd
from backend_enginex import EnginexBackend

# ==========================================
# 1. SETUP & STYLE
# ==========================================
st.set_page_config(page_title="GEMS EngineX Pro", page_icon="🏗️", layout="wide")

st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #1e3a8a; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: white; border-radius: 4px; border: 1px solid #e2e8f0; }
    .stTabs [aria-selected="true"] { background-color: #1e3a8a !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOAD BACKEND
# ==========================================
engine = EnginexBackend()
engine.init_session() # Pastikan data awal masuk ke session state

# ==========================================
# 3. LOGIC (STATE-FIRST APPROACH)
# ==========================================
# PENTING: Kita hitung dulu RAB menggunakan data yang ada di session state 'rab_editor_data'.
# Saat user mengedit tabel, Streamlit otomatis update 'rab_editor_data' SEBELUM baris ini jalan.
# Jadi hasil 'df_calc' & 'summary' pasti sudah memakai angka terbaru.
df_calc, summary = engine.calculate_from_state()
info = st.session_state['project_info']

# ==========================================
# 4. SIDEBAR
# ==========================================
with st.sidebar:
    st.title("⚙️ Project Control")
    # Menggunakan key untuk langsung bind ke session state (Anti-Lag)
    st.text_input("Nama Proyek", key="name_input", value=info['name'], 
                  on_change=lambda: st.session_state['project_info'].update({'name': st.session_state.name_input}))
    
    st.text_input("Owner", key="owner_input", value=info['owner'], 
                  on_change=lambda: st.session_state['project_info'].update({'owner': st.session_state.owner_input}))
    
    st.text_input("Kontraktor", key="cont_input", value=info['cont'], 
                  on_change=lambda: st.session_state['project_info'].update({'cont': st.session_state.cont_input}))
    
    st.divider()
    
    st.number_input("Fee (%)", key="fee_input", value=info['fee_pct'], step=0.5,
                    on_change=lambda: st.session_state['project_info'].update({'fee_pct': st.session_state.fee_input}))
    
    st.number_input("PPN (%)", key="tax_input", value=info['tax_pct'], step=1.0,
                    on_change=lambda: st.session_state['project_info'].update({'tax_pct': st.session_state.tax_input}))
    
    if st.button("🔴 Reset Semua Data"):
        st.session_state.clear()
        st.rerun()

# ==========================================
# 5. MAIN INTERFACE
# ==========================================
st.title("🏗️ GEMS EngineX Estimator")
st.caption(f"Project: {info['name']} | Owner: {info['owner']}")

# Tabs
t0, t1, t2 = st.tabs(["📊 Dashboard & Cover", "📝 Input RAB (Editor)", "📈 Analisa Data"])

# --- TAB 0: COVER (Hasil Hitungan Real-Time) ---
with t0:
    st.markdown(f"""
    <div style="background:white; padding:30px; border:4px double #1e3a8a; border-radius:10px; text-align:center;">
        <h2 style="color:#1e3a8a; margin:0;">ENGINEERING ESTIMATE (EE)</h2>
        <p style="color:#64748b;">{info['name']}</p>
        <hr>
        <h1 style="font-size:56px; color:#0f172a; margin:10px 0;">{engine.fmt_idr(summary['grand_total'])}</h1>
        <p style="color:#64748b; font-style:italic;">(Termasuk Jasa {info['fee_pct']}% & PPN {info['tax_pct']}%)</p>
        <br>
        <div style="display:flex; justify-content:space-around; margin-top:20px;">
            <div>Disetujui:<br><b>{info['owner']}</b></div>
            <div>Dibuat:<br><b>{info['cont']}</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Biaya Konstruksi", engine.fmt_idr(summary['real_cost']))
    col2.metric("Jasa + PPN", engine.fmt_idr(summary['fee_val'] + summary['tax_val']))
    col3.metric("Grand Total", engine.fmt_idr(summary['grand_total']))

# --- TAB 1: INPUT RAB (Sumber Masalah 'Muter' Dulu) ---
with t1:
    st.info("💡 **Petunjuk:** Ubah angka di tabel. Tekan Enter. Perhitungan otomatis update (Tanpa Loading Lama).")
    
    # KUNCI ANTI MUTER: 
    # 1. Gunakan 'key' yang sama dengan yang kita init di backend ('rab_editor_data').
    # 2. HAPUS st.rerun(). Streamlit editor otomatis handle update state via 'key'.
    # 3. Kolom 'JumlahHarga' kita tampilkan dari hasil hitungan (df_calc), TAPI dinonaktifkan di editor
    #    agar tidak disimpan balik ke input (karena itu hasil rumus).
    
    # Kita perlu merge 'JumlahHarga' dari df_calc ke editor data agar user bisa lihat total per item
    # Tapi editor HANYA boleh mengubah Volume & HargaSatuan
    
    display_df = df_calc[["Divisi", "Uraian", "Satuan", "Volume", "HargaSatuan", "JumlahHarga"]]
    
    edited = st.data_editor(
        display_df,
        key="rab_editor_data", # <--- INI KUNCINYA. Streamlit langsung update session_state['rab_editor_data']
        column_config={
            "Divisi": st.column_config.SelectboxColumn(options=["I. PERSIAPAN", "II. TANAH", "III. LANTAI 1", "IV. LANTAI 2"], required=True),
            "Uraian": st.column_config.TextColumn(width="large", required=True),
            "Volume": st.column_config.NumberColumn(format="%.2f", required=True),
            "HargaSatuan": st.column_config.NumberColumn(format="Rp %d", required=True),
            "JumlahHarga": st.column_config.NumberColumn(format="Rp %d", disabled=True) # Read-only
        },
        num_rows="dynamic",
        use_container_width=True
    )
    # TIDAK ADA KODE LOGIKA/RERUN DISINI. Biarkan Streamlit bekerja secara native.

# --- TAB 2: ANALISA ---
with t2:
    st.subheader("Distribusi Biaya")
    rekap = df_calc.groupby('Divisi')['JumlahHarga'].sum().reset_index()
    rekap['Bobot (%)'] = (rekap['JumlahHarga'] / summary['real_cost'] * 100).fillna(0)
    
    st.dataframe(
        rekap, 
        use_container_width=True, 
        hide_index=True,
        column_config={"JumlahHarga": st.column_config.NumberColumn(format="Rp %d"), "Bobot (%)": st.column_config.NumberColumn(format="%.2f %%")}
    )
    
    st.bar_chart(rekap, x="Divisi", y="JumlahHarga", color="#1e3a8a")

st.markdown("---")
st.caption("Powered by GEMS EngineX | Zero-Loop Architecture")
