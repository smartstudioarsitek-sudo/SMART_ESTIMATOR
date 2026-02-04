import streamlit as st
import pandas as pd
from backend_enginex import EnginexBackend

# ==========================================
# 1. SETUP UI
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
# 2. LOAD BACKEND & DATA
# ==========================================
engine = EnginexBackend()
engine.init_session()

# Ambil Data Mentah (Input User) dari State
df_input = engine.get_boq_data()
info = st.session_state['project_info']

# Lakukan Perhitungan (Menghasilkan df_display yang punya kolom 'JumlahHarga')
df_display, summary = engine.calculate_rab(df_input)

# ==========================================
# 3. SIDEBAR
# ==========================================
with st.sidebar:
    st.title("⚙️ Project Control")
    
    # Input Project Info (Aman menggunakan key update manual)
    new_name = st.text_input("Nama Proyek", value=info['name'])
    if new_name != info['name']:
        st.session_state['project_info']['name'] = new_name
        st.rerun()

    new_owner = st.text_input("Owner", value=info['owner'])
    if new_owner != info['owner']:
        st.session_state['project_info']['owner'] = new_owner
        st.rerun()

    new_cont = st.text_input("Kontraktor", value=info['cont'])
    if new_cont != info['cont']:
        st.session_state['project_info']['cont'] = new_cont
        st.rerun()
    
    st.divider()
    
    new_fee = st.number_input("Fee (%)", value=info['fee_pct'], step=0.5)
    if new_fee != info['fee_pct']:
        st.session_state['project_info']['fee_pct'] = new_fee
        st.rerun()

    new_tax = st.number_input("PPN (%)", value=info['tax_pct'], step=1.0)
    if new_tax != info['tax_pct']:
        st.session_state['project_info']['tax_pct'] = new_tax
        st.rerun()
    
    if st.button("🔴 Reset Data"):
        st.session_state.clear()
        st.rerun()

# ==========================================
# 4. MAIN INTERFACE
# ==========================================
st.title("🏗️ GEMS EngineX Estimator")
st.caption(f"Project: {info['name']} | Owner: {info['owner']}")

# Tabs
t0, t1, t2 = st.tabs(["📊 Dashboard", "📝 Input RAB (Editor)", "📈 Analisa"])

# --- TAB 0: DASHBOARD ---
with t0:
    st.markdown(f"""
    <div style="background:white; padding:30px; border:4px double #1e3a8a; border-radius:10px; text-align:center;">
        <h2 style="color:#1e3a8a; margin:0;">ENGINEERING ESTIMATE (EE)</h2>
        <hr>
        <h1 style="font-size:56px; color:#0f172a; margin:10px 0;">{engine.fmt_idr(summary['grand_total'])}</h1>
        <p style="color:#64748b;">(Termasuk Jasa {info['fee_pct']}% & PPN {info['tax_pct']}%)</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Biaya Konstruksi", engine.fmt_idr(summary['real_cost']))
    c2.metric("Jasa + PPN", engine.fmt_idr(summary['fee_val'] + summary['tax_val']))
    c3.metric("Grand Total", engine.fmt_idr(summary['grand_total']))

# --- TAB 1: INPUT RAB (ANTI MUTER LOGIC) ---
with t1:
    st.info("💡 Edit **Volume** atau **Harga Satuan**. Tekan **Enter** untuk update.")
    
    # 1. Tampilkan Data Editor
    # PENTING: Jangan gunakan key="xxx" yang sama dengan nama variabel state!
    # Kita gunakan variabel penampung 'edited_result'
    edited_result = st.data_editor(
        df_display, # Kita tampilkan DF yang sudah ada total-nya agar user bisa lihat
        column_config={
            "Divisi": st.column_config.SelectboxColumn(options=["I. PERSIAPAN", "II. TANAH", "III. LANTAI 1", "IV. LANTAI 2"], required=True),
            "Uraian": st.column_config.TextColumn(width="large", required=True),
            "Volume": st.column_config.NumberColumn(format="%.2f", required=True),
            "HargaSatuan": st.column_config.NumberColumn(format="Rp %d", required=True),
            "JumlahHarga": st.column_config.NumberColumn(format="Rp %d", disabled=True) # Read-only, user tidak bisa edit ini
        },
        num_rows="dynamic",
        use_container_width=True
    )

    # 2. Logika Deteksi Perubahan (Manual Check)
    if edited_result is not None:
        # Kita buang kolom 'JumlahHarga' karena itu kolom hasil hitungan, bukan input
        # Kita hanya ingin menyimpan Input User
        clean_edited = edited_result.drop(columns=['JumlahHarga'])
        
        # Kita bandingkan data input baru dengan data yang ada di session state
        # Jika berbeda, berarti user baru saja mengedit sesuatu
        if not clean_edited.equals(st.session_state['project_data_boq']):
            # Update Session State
            engine.update_boq_data(clean_edited)
            # Rerun agar perhitungan ulang terjadi dan tampilan terupdate
            st.rerun()

# --- TAB 2: ANALISA ---
with t2:
    st.subheader("Distribusi Biaya per Divisi")
    rekap = df_display.groupby('Divisi')['JumlahHarga'].sum().reset_index()
    rekap['Bobot (%)'] = (rekap['JumlahHarga'] / summary['real_cost'] * 100).fillna(0)
    
    st.dataframe(
        rekap, 
        use_container_width=True, 
        hide_index=True,
        column_config={"JumlahHarga": st.column_config.NumberColumn(format="Rp %d"), "Bobot (%)": st.column_config.NumberColumn(format="%.2f %%")}
    )

st.markdown("---")
st.caption("GEMS EngineX | Final Stability Release")
