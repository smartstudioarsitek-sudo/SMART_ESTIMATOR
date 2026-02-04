import streamlit as st
import pandas as pd
# Pastikan nama file backend_enginex.py (bukan backend_enginex (3).py)
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
# Cache resource agar backend tidak di-init ulang setiap rerun (opsional tapi bagus)
@st.cache_resource
def get_engine():
    return EnginexBackend()

engine = get_engine()
engine.init_session()

# ==========================================
# 3. LOGIC (CALCULATE FIRST)
# ==========================================
# Hitung ulang berdasarkan data terakhir di state
df_calc, summary = engine.calculate_from_state()
info = st.session_state['project_info']

# ==========================================
# 4. SIDEBAR
# ==========================================
with st.sidebar:
    st.title("⚙️ Project Control")
    
    # Callback update sederhana
    def update_info(key_name):
        st.session_state['project_info'][key_name] = st.session_state[f"inp_{key_name}"]

    st.text_input("Nama Proyek", key="inp_name", value=info['name'], on_change=update_info, args=('name',))
    st.text_input("Owner", key="inp_owner", value=info['owner'], on_change=update_info, args=('owner',))
    st.text_input("Kontraktor", key="inp_cont", value=info['cont'], on_change=update_info, args=('cont',))
    
    st.divider()
    
    st.number_input("Fee (%)", key="inp_fee_pct", value=float(info['fee_pct']), step=0.5, on_change=update_info, args=('fee_pct',))
    st.number_input("PPN (%)", key="inp_tax_pct", value=float(info['tax_pct']), step=1.0, on_change=update_info, args=('tax_pct',))
    
    if st.button("🔴 Reset Semua Data"):
        st.session_state.clear()
        st.rerun()

# ==========================================
# 5. MAIN INTERFACE
# ==========================================
st.title("🏗️ GEMS EngineX Estimator")
st.caption(f"Project: {info['name']} | Owner: {info['owner']}")

t0, t1, t2 = st.tabs(["📊 Dashboard", "📝 Input RAB", "📈 Analisa"])

# --- TAB 0: DASHBOARD ---
with t0:
    st.markdown(f"""
    <div style="background:white; padding:30px; border:4px double #1e3a8a; border-radius:10px; text-align:center; margin-bottom:20px;">
        <h2 style="color:#1e3a8a; margin:0;">ENGINEERING ESTIMATE (EE)</h2>
        <h1 style="font-size:48px; color:#0f172a; margin:10px 0;">{engine.fmt_idr(summary['grand_total'])}</h1>
        <p style="color:#64748b;">(Termasuk Jasa {info['fee_pct']}% & PPN {info['tax_pct']}%)</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Biaya Real", engine.fmt_idr(summary['real_cost']))
    c2.metric("Jasa + PPN", engine.fmt_idr(summary['fee_val'] + summary['tax_val']))
    c3.metric("Total Akhir", engine.fmt_idr(summary['grand_total']))

# --- TAB 1: INPUT RAB ---
with t1:
    st.info("💡 Edit **Volume** atau **Harga Satuan**. Total hitungan otomatis update.")
    
    # Siapkan DataFrame untuk ditampilkan
    # Kita ambil kolom yang diperlukan saja dari hasil hitungan
    display_df = df_calc[["Divisi", "Uraian", "Satuan", "Volume", "HargaSatuan", "JumlahHarga"]]

    edited_df = st.data_editor(
        display_df,
        key="rab_editor_data", # KUNCI: Langsung bind ke session state
        column_config={
            "Divisi": st.column_config.SelectboxColumn(options=["I. PERSIAPAN", "II. TANAH", "III. LANTAI 1", "IV. LANTAI 2"], required=True),
            "Uraian": st.column_config.TextColumn(width="large", required=True),
            "Volume": st.column_config.NumberColumn(format="%.2f", required=True),
            "HargaSatuan": st.column_config.NumberColumn(format="Rp %d", required=True),
            "JumlahHarga": st.column_config.NumberColumn(format="Rp %d", disabled=True) # Read-only agar user tidak bingung
        },
        num_rows="dynamic",
        use_container_width=True
    )

# --- TAB 2: ANALISA ---
with t2:
    st.subheader("Distribusi Biaya per Divisi")
    if not df_calc.empty:
        rekap = df_calc.groupby('Divisi')['JumlahHarga'].sum().reset_index()
        total_real = summary['real_cost'] if summary['real_cost'] > 0 else 1
        rekap['Bobot (%)'] = (rekap['JumlahHarga'] / total_real * 100)
        
        st.dataframe(
            rekap, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "JumlahHarga": st.column_config.NumberColumn(format="Rp %d"), 
                "Bobot (%)": st.column_config.NumberColumn(format="%.2f %%")
            }
        )
        st.bar_chart(rekap, x="Divisi", y="JumlahHarga", color="#1e3a8a")
    else:
        st.warning("Belum ada data.")

st.markdown("---")
st.caption("Powered by GEMS EngineX")
