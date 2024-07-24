import streamlit as st
import mysql.connector
import pandas as pd
from mysql.connector import Error
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error
import pickle
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np



# Fungsi untuk membuat koneksi MySQL
def create_connection(host, user, password, database):
    conn = None
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        st.success("Terhubung ke database MySQL")
    except Error as e:
        st.error(f"Kesalahan saat menghubungkan ke database MySQL: {e}")
    return conn

# Fungsi untuk memasukkan riwayat model ke database MySQL
def insert_model_history(conn, nama_barang, jenis_model, mae):
    try:
        cursor = conn.cursor()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = "INSERT INTO history_model (nama_barang, jenis_model, tanggal_training, mae) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (nama_barang, jenis_model, current_time, mae))
        conn.commit()
        st.success(f"Riwayat model untuk {jenis_model} dari {nama_barang} berhasil dimasukkan ke database.")
    except Error as e:
        st.error(f"Kesalahan saat memasukkan riwayat model ke database: {e}")

# Fungsi untuk melatih model Holt-Winters
def train_hw_model(data, conn, nama_barang):
    # Preprocessing data
    data['JUMLAH_STOK'] = data['JUMLAH_STOK'].interpolate(method='linear')
    
    # Fit model Holt-Winters
    hw_model = ExponentialSmoothing(data['JUMLAH_STOK'], seasonal='add', seasonal_periods=12)
    hw_fit = hw_model.fit()

    # Simpan model dengan Pickle
    with open('training_model/holtwinters_model.pkl', 'wb') as hw_file:
        pickle.dump(hw_fit, hw_file)
    
    # Prediksi dengan Holt-Winters
    hw_forecast = hw_fit.forecast(steps=10)
    
    # Visualisasi
    st.subheader('Prediksi Holt-Winters')
    st.line_chart(pd.DataFrame({
        'Actual Data': data['JUMLAH_STOK'],
        'Holt-Winters Forecast': hw_forecast
    }))
    st.markdown("""
        **Penjelasan Grafik:**
        - **Actual Data**: Data jumlah stok aktual ditampilkan dalam grafik.
        - **Holt-Winters Forecast**: Prediksi jumlah stok berdasarkan model Holt-Winters ditampilkan dalam grafik.
    """)
    
    # Hitung MAE
    hw_mae = mean_absolute_error(data['JUMLAH_STOK'][-10:], hw_forecast)
    st.write(f'MAE Holt-Winters: {hw_mae}')

    # Masukkan riwayat model ke database
    insert_model_history(conn, nama_barang, 'Holt-Winters', hw_mae)

    return hw_forecast, hw_mae

# Fungsi untuk melatih model ARIMA
def train_arima_model(data, conn, nama_barang):
    # Set frekuensi secara eksplisit (mis. harian)
    data = data.set_index('TGL_TRANSAKSI').asfreq('D')
    
    # Fit model ARIMA
    arima_model = ARIMA(data['JUMLAH_STOK'], order=(5, 1, 0))
    arima_fit = arima_model.fit()

    # Simpan model dengan Pickle
    with open('training_model/arima_model.pkl', 'wb') as arima_file:
        pickle.dump(arima_fit, arima_file)
    
    # Prediksi dengan ARIMA
    arima_forecast = arima_fit.forecast(steps=10)
    
    # Visualisasi
    st.subheader('Prediksi ARIMA')
    st.line_chart(pd.DataFrame({
        'Actual Data': data['JUMLAH_STOK'],
        'ARIMA Forecast': arima_forecast
    }))
    st.markdown("""
        **Penjelasan Grafik:**
        - **Actual Data**: Data jumlah stok aktual ditampilkan dalam grafik.
        - **ARIMA Forecast**: Prediksi jumlah stok berdasarkan model ARIMA ditampilkan dalam grafik.
    """)
    
    # Hitung MAE
    arima_mae = mean_absolute_error(data['JUMLAH_STOK'][-10:], arima_forecast)
    st.write(f'MAE ARIMA: {arima_mae}')

    # Masukkan riwayat model ke database
    insert_model_history(conn, nama_barang, 'ARIMA', arima_mae)

    return arima_forecast, arima_mae

# Fungsi untuk menampilkan halaman pelatihan model
def show_halaman_trainingmodel():
    st.title("Pelatihan Model Prediksi")
    # Unggah file CSV
    uploaded_file = st.file_uploader("Unggah file CSV", type=["csv"])
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file, parse_dates=['TGL_TRANSAKSI'])
        
        # Pilih produk
        product_names = data['NAMA_BARANG'].unique().tolist()
        selected_product = st.selectbox("Pilih Produk", product_names)
        filtered_data = data[data['NAMA_BARANG'] == selected_product]
        
        host = "localhost"
        user = "root"
        password = ""  # Ganti dengan password MySQL Anda
        database = "db_forecasting"  # Ganti dengan nama database Anda
        conn = create_connection(host, user, password, database)  # Buat koneksi MySQL
        
        if st.button("Latih Model"):
            st.subheader(f"Model untuk {selected_product}")
            hw_forecast, hw_mae = train_hw_model(filtered_data, conn, selected_product)
            arima_forecast, arima_mae = train_arima_model(filtered_data, conn, selected_product)
        
            # Bandingkan hasil kedua model
            st.subheader(f"Perbandingan Hasil Prediksi untuk {selected_product}")
            comparison_df = pd.DataFrame({
                'Holt-Winters Forecast': hw_forecast,
                'ARIMA Forecast': arima_forecast,
                'Actual Data': filtered_data['JUMLAH_STOK'].reset_index(drop=True)
            })
            st.line_chart(comparison_df)
            st.markdown("""
                **Penjelasan Grafik Perbandingan Hasil Prediksi:**
                - **Holt-Winters Forecast**: Garis biru menunjukkan Prediksi menggunakan model Holt-Winters.
                Holt-Winters adalah metode eksponensial smoothing yang cocok untuk data dengan komponen musiman.
                - **ARIMA Forecast**: Garis oranye menunjukkan Prediksi menggunakan model ARIMA.
                ARIMA (Autoregressive Integrated Moving Average) cocok untuk data yang stasioner setelah diferensiasi.
                - **Actual Data**: Garis hijau menunjukkan data aktual stok barang.
                Data aktual digunakan sebagai dasar perbandingan untuk mengevaluasi performa kedua model.
                - **MAE**: Mean Absolute Error digunakan untuk mengukur seberapa baik kedua model dalam memprediksi data aktual.
            """)
            st.markdown(f"""
                **Kesimpulan Perbandingan:**
                - Model dengan nilai MAE lebih rendah memiliki kinerja yang lebih baik dalam memprediksi data aktual.
                - **MAE Holt-Winters**: {hw_mae}
                - **MAE ARIMA**: {arima_mae}
            """)

        conn.close()  # Tutup koneksi MySQL

#


if __name__ == '__main__':
    show_halaman_trainingmodel()
