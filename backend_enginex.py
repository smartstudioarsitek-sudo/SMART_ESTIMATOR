import pandas as pd
import streamlit as st

class EnginexBackend:
    def __init__(self):
        # Kita definisikan data langsung sebagai DataFrame agar konsisten
        self.default_boq = pd.DataFrame([
            {"Divisi": "I. PERSIAPAN", "Uraian": "Pengukuran & Bouwplank", "Satuan": "m2", "Volume": 425.18, "HargaSatuan": 15000},
            {"Divisi": "I. PERSIAPAN", "Uraian": "Direksi Keet & Gudang", "Satuan": "Ls", "Volume": 1.0, "HargaSatuan": 15000000},
            {"Divisi": "II. TANAH", "Uraian": "Galian Tanah Pondasi", "Satuan": "m3", "Volume": 166.37, "HargaSatuan": 85000},
            {"Divisi": "II. TANAH", "Uraian": "Urugan Pasir Bawah", "Satuan": "m3", "Volume": 7.76, "HargaSatuan": 220000},
            {"Divisi": "III. LANTAI 1", "Uraian": "Beton Kolom Lt 1", "Satuan": "m3", "Volume": 12.18, "HargaSatuan": 4500000},
            {"Divisi": "III. LANTAI 1", "Uraian": "Dinding Bata Ringan", "Satuan": "m2", "Volume": 397.27, "HargaSatuan": 135000},
            {"Divisi": "IV. LANTAI 2", "Uraian": "Beton Balok Lt 2", "Satuan": "m3", "Volume": 21.28, "HargaSatuan": 4800000},
        ])
        
        self.default_info = {
            "name": "PEMBANGUNAN RUKO 2 LANTAI",
            "owner": "BAPAK RIO",
            "cont": "SMART STUDIO",
            "fee_pct": 10.0,
            "tax_pct": 11.0
        }

    def init_session(self):
        # Inisialisasi Session State dengan DataFrame
        if 'project_data_boq' not in st.session_state:
            st.session_state['project_data_boq'] = self.default_boq.copy()
        
        if 'project_info' not in st.session_state:
            st.session_state['project_info'] = self.default_info

    def get_boq_data(self):
        """Mengambil data BOQ murni (Input User)"""
        return st.session_state['project_data_boq']

    def update_boq_data(self, new_df):
        """Menyimpan data BOQ baru ke session"""
        st.session_state['project_data_boq'] = new_df

    def calculate_rab(self, df_input):
        """
        Menghitung RAB berdasarkan DataFrame Input.
        Tidak mengubah state, hanya mengembalikan hasil hitungan.
        """
        # Copy agar tidak merusak data asli
        df = df_input.copy()
        info = st.session_state['project_info']
        
        # 1. Sanitasi Angka (Cegah Error)
        df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce').fillna(0)
        df['HargaSatuan'] = pd.to_numeric(df['HargaSatuan'], errors='coerce').fillna(0)
        
        # 2. Hitung Total
        df['JumlahHarga'] = df['Volume'] * df['HargaSatuan']
        
        # 3. Hitung Rekap Global
        real_cost = df['JumlahHarga'].sum()
        fee_val = real_cost * (info['fee_pct'] / 100)
        subtotal = real_cost + fee_val
        tax_val = subtotal * (info['tax_pct'] / 100)
        grand_total = subtotal + tax_val
        
        summary = {
            "real_cost": real_cost,
            "fee_val": fee_val,
            "subtotal": subtotal,
            "tax_val": tax_val,
            "grand_total": grand_total
        }
        
        return df, summary

    def fmt_idr(self, val):
        return f"Rp {val:,.0f}".replace(",", ".")
