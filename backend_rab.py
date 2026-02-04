import pandas as pd
import streamlit as st

class EnginexBackend:
    def __init__(self):
        # Default Data jika belum ada
        self.default_info = {
            "name": "PEMBANGUNAN RUKO 2 LANTAI",
            "loc": "DENPASAR - BALI",
            "year": "2026",
            "owner": "BAPAK RIO",
            "cont": "SMART STUDIO",
            "fee_pct": 10.0,
            "tax_pct": 11.0
        }
        
        self.default_boq = [
            {"Divisi": "I. PERSIAPAN", "Uraian": "Pengukuran & Bouwplank", "Satuan": "m2", "Volume": 425.18, "HargaSatuan": 15000},
            {"Divisi": "I. PERSIAPAN", "Uraian": "Direksi Keet & Gudang", "Satuan": "Ls", "Volume": 1.0, "HargaSatuan": 15000000},
            {"Divisi": "II. TANAH", "Uraian": "Galian Tanah Pondasi", "Satuan": "m3", "Volume": 166.37, "HargaSatuan": 85000},
            {"Divisi": "II. TANAH", "Uraian": "Urugan Pasir Bawah", "Satuan": "m3", "Volume": 7.76, "HargaSatuan": 220000},
            {"Divisi": "III. LANTAI 1", "Uraian": "Beton Kolom Lt 1", "Satuan": "m3", "Volume": 12.18, "HargaSatuan": 4500000},
            {"Divisi": "III. LANTAI 1", "Uraian": "Dinding Bata Ringan", "Satuan": "m2", "Volume": 397.27, "HargaSatuan": 135000},
            {"Divisi": "IV. LANTAI 2", "Uraian": "Beton Balok Lt 2", "Satuan": "m3", "Volume": 21.28, "HargaSatuan": 4800000},
        ]
        
        self.default_basic = [
            {"Kode": "L01", "Nama": "Pekerja", "Sat": "OH", "Harga": 120000},
            {"Kode": "M01", "Nama": "Semen PC 50kg", "Sat": "Zak", "Harga": 68000},
        ]

    def init_session(self):
        """Memastikan session state terisi"""
        if 'project_data' not in st.session_state:
            st.session_state.project_data = {
                "info": self.default_info,
                "boq": self.default_boq,
                "basic": self.default_basic
            }

    def get_data(self):
        """Mengambil data mentah untuk Editor"""
        self.init_session()
        return st.session_state.project_data

    def calculate_rab(self):
        """
        Menghitung RAB secara on-the-fly.
        Mengembalikan tuple: (DataFrame Lengkap, Dictionary Rekap)
        """
        data = self.get_data()
        df = pd.DataFrame(data['boq'])
        
        # Sanitasi Data (Penting agar tidak error saat dikalikan)
        df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce').fillna(0)
        df['HargaSatuan'] = pd.to_numeric(df['HargaSatuan'], errors='coerce').fillna(0)
        
        # Hitung Total
        df['JumlahHarga'] = df['Volume'] * df['HargaSatuan']
        
        # Hitung Grand Total
        real_cost = df['JumlahHarga'].sum()
        fee_val = real_cost * (data['info']['fee_pct'] / 100)
        subtotal = real_cost + fee_val
        tax_val = subtotal * (data['info']['tax_pct'] / 100)
        grand_total = subtotal + tax_val
        
        summary = {
            "real_cost": real_cost,
            "fee_val": fee_val,
            "subtotal": subtotal,
            "tax_val": tax_val,
            "grand_total": grand_total
        }
        
        return df, summary

    def update_boq(self, new_df):
        """
        Menyimpan data dari Editor kembali ke Session State.
        PENTING: Kita buang kolom 'JumlahHarga' agar tidak double store.
        """
        # Hapus kolom hasil hitungan (derived column)
        if 'JumlahHarga' in new_df.columns:
            clean_df = new_df.drop(columns=['JumlahHarga'])
        else:
            clean_df = new_df
            
        # Simpan ke state
        st.session_state.project_data['boq'] = clean_df.to_dict('records')
        
    def fmt_idr(self, val):
        return f"Rp {val:,.0f}".replace(",", ".")
