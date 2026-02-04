import streamlit as st
import pandas as pd
from backend_enginex import EnginexBackend

# ==========================================
# 1. SETUP UI
# ==========================================
st.set_page_config(page_title="GEMS EngineX", page_icon="🏗️", layout="wide")

# CSS Agar Tampilan Full Professional
st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #1e3a8a; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: white; border-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
    .stTabs [aria-selected="true"] { background-color: #1e3a8a !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOAD BACKEND
# ==========================================
engine = EnginexBackend()
engine.init_session() # Pastikan data ada

# Ambil Info Project
info = st.session_state.project_data['info']

# ==========================================
# 3. SIDEBAR
# ==========================================
with st.sidebar:
    st.title("⚙️ Control Panel")
    info['name'] = st.text_input("Nama Proyek", info['name'])
    info['owner'] = st.text_input("Owner", info['owner'])
    info['cont'] = st.text_input("Kontraktor", info['cont'])
    st.divider()
    info['fee_pct'] = st.number_input("Fee (%)", value=info['fee_pct'])
    info['tax_pct'] = st.number_input("PPN (%)", value=info['tax_pct'])
    
    if st.button("🔴 Reset Project"):
        st.session_state.clear()
        st.rerun()

# ==========================================
# 4. MAIN LOGIC (HITUNG DULU DISINI)
# ==========================================
# Kita hitung RAB setiap kali halaman direfresh/berubah
df_calc, summary = engine.calculate_rab()

# ==========================================
# 5. TAMPILAN UTAMA (TABS)
# ==========================================
st.title("🏗️ GEMS EngineX Estimator")
st.caption(f"Project: {info['name']} | Status: Active")

t0, t1, t2 = st.tabs(["📑 Cover & Summary", "📝 Input RAB (Editor)", "📊 Rekapitulasi"])

# --- TAB 0: COVER ---
with t0:
    st.markdown(f"""
    <div style="background:white; padding:30px; border:2px solid #1e3a8a; border-radius:10px; text-align:center;">
        <h2 style="color:#1e3a8a;">ENGINEERING ESTIMATE</h2>
        <hr>
        <h1 style="font-size:48px; color:#0f172a;">{engine.fmt_idr(summary['grand_total'])}</h1>
        <p style="color:grey;">(Termasuk Jasa {info['fee_pct']}% & PPN {info['tax_pct']}%)</p>
        <br>
        <div style="display:flex; justify-content:space-between; padding:0 50px;">
            <div><b>Disetujui:</b><br><br><u>{info['owner']}</u><br>Owner</div>
            <div><b>Dibuat:</b><br><br><u>{info['cont']}</u><br>Kontraktor</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- TAB 1: INPUT RAB (THE CRITICAL PART) ---
with t1:
    st.info("💡 Edit Volume atau Harga Satuan di sini. Total akan terhitung otomatis.")
    
    # SETUP EDITOR
    # Kita menggunakan df_calc (yang sudah ada kolom Totalnya) untuk ditampilkan
    edited_df = st.data_editor(
        df_calc,
        column_config={
            "Divisi": st.column_config.SelectboxColumn(options=["I. PERSIAPAN", "II. TANAH", "III. LANTAI 1", "IV. LANTAI 2"], required=True),
            "Uraian": st.column_config.TextColumn(width="large", required=True),
            "Volume": st.column_config.NumberColumn(format="%.2f", required=True),
            "HargaSatuan": st.column_config.NumberColumn(format="Rp %d", required=True),
            # KOLOM PENTING: Disabled agar user tidak edit Total manual (Penyebab Loop)
            "JumlahHarga": st.column_config.NumberColumn(format="Rp %d", disabled=True)
        },
        num_rows="dynamic",
        use_container_width=True,
        key="main_editor"
    )
    
    # LOGIKA SAVE YANG AMAN
    # Jika ada perubahan di editor...
    if edited_df is not None:
        # Kita bandingkan data Editor (tanpa kolom total) dengan data di Session State
        clean_input = edited_df.drop(columns=['JumlahHarga']).to_dict('records')
        current_state = st.session_state.project_data['boq']
        
        # Hanya simpan jika berbeda (Anti Muter)
        if clean_input != current_state:
            engine.update_boq(edited_df)
            st.rerun()

# --- TAB 2: REKAPITULASI ---
with t2:
    c1, c2, c3 = st.columns(3)
    c1.metric("Real Cost", engine.fmt_idr(summary['real_cost']))
    c2.metric("Jasa + PPN", engine.fmt_idr(summary['fee_val'] + summary['tax_val']))
    c3.metric("GRAND TOTAL", engine.fmt_idr(summary['grand_total']))
    
    st.subheader("Bobot Pekerjaan")
    rekap = df_calc.groupby('Divisi')['JumlahHarga'].sum().reset_index()
    rekap['Bobot (%)'] = (rekap['JumlahHarga'] / summary['real_cost'] * 100).fillna(0)
    
    st.dataframe(
        rekap, 
        use_container_width=True, 
        hide_index=True,
        column_config={"JumlahHarga": st.column_config.NumberColumn(format="Rp %d"), "Bobot (%)": st.column_config.NumberColumn(format="%.2f %%")}
    )

st.markdown("---")
st.caption("Powered by GEMS EngineX | Modular Architecture")
