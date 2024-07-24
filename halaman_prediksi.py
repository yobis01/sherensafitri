import streamlit as st
import joblib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import mysql.connector
from mysql.connector import Error
import altair as alt
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing

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

# Fungsi untuk membuat prediksi ARIMA
def make_arima_prediction(start_date, end_date, data):
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    num_steps = len(date_range)
    model = ARIMA(data, order=(5, 1, 0))
    model_fit = model.fit()
    arima_forecast = model_fit.forecast(steps=num_steps)
    return arima_forecast, date_range

# Fungsi untuk membuat prediksi Holt-Winters
def make_hw_prediction(start_date, end_date, data):
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    num_steps = len(date_range)
    model = ExponentialSmoothing(data, seasonal='add', seasonal_periods=12)
    model_fit = model.fit()
    hw_forecast = model_fit.forecast(steps=num_steps)
    return hw_forecast, date_range

# Fungsi untuk menghitung stok yang dibutuhkan
def calculate_required_stock(forecast, buffer_stock=0, rounding_method='round'):
    required_stock = forecast + buffer_stock
    if rounding_method == 'round':
        required_stock = np.round(required_stock)
    elif rounding_method == 'ceil':
        required_stock = np.ceil(required_stock)
    elif rounding_method == 'floor':
        required_stock = np.floor(required_stock)
    return required_stock

# Fungsi untuk membaca data aktual dari file CSV
def read_actual_stock_data():
    df_actual = pd.read_csv('data_barang.csv')  # Ganti dengan path sesuai lokasi file
    df_actual['TGL_TRANSAKSI'] = pd.to_datetime(df_actual['TGL_TRANSAKSI'])
    return df_actual

# Fungsi untuk menyimpan hasil prediksi ke database dan menyimpan grafik sebagai file gambar
def save_prediction_to_db(model_type, start_date, end_date, item_name, forecast, required_stock, date_range, conn):
    try:
        cursor = conn.cursor()

        # Simpan grafik sebagai file gambar
        image_path = f"plots/{model_type}_{item_name}_{start_date}_{end_date}.png"

        plt.figure(figsize=(10, 6))
        plt.plot(date_range, forecast, label=f'{model_type} Forecast', color='red' if model_type == 'ARIMA' else 'green')
        plt.plot(date_range, required_stock, label='Required Stock', color='blue')

        # Baca data aktual
        df_actual = read_actual_stock_data()
        plt.plot(df_actual['TGL_TRANSAKSI'], df_actual['JUMLAH_STOK'], label='Actual Stock', color='black')

        plt.title(f'{model_type} Stock Forecast and Required Stock')
        plt.xlabel('Date')
        plt.ylabel('Values')
        plt.legend()
        plt.savefig(image_path)

        # Simpan hasil prediksi ke database
        query = "INSERT INTO prediction_results (model_type, start_date, end_date, item_name, forecast, required_stock, image_path) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (model_type, start_date, end_date, item_name, forecast.to_json(), required_stock.to_json(), image_path))
        conn.commit()

        st.success(f"Hasil prediksi {model_type} berhasil disimpan ke database.")
    except Error as e:
        st.error(f"Kesalahan saat menyimpan hasil prediksi ke database: {e}")

# Fungsi untuk menampilkan halaman prediksi
def show_halaman_prediksi():
    st.title('Stock Forecasting App')

    # Load data stok aktual untuk mendapatkan nama barang yang unik
    df_actual = read_actual_stock_data()
    unique_items = df_actual['NAMA_BARANG'].unique()

    # Antarmuka untuk input pengguna
    item_name = st.selectbox('Pilih Nama Barang:', unique_items)
    model_selection = st.selectbox('Pilih Model:', ['ARIMA', 'Holt-Winters'])
    buffer_stock = st.number_input('Buffer Stock:', min_value=0, value=10)
    rounding_method = st.selectbox('Metode Pembulatan:', ['round', 'ceil', 'floor'])

    if model_selection == 'ARIMA':
        start_date = st.date_input('Tanggal Mulai Prediksi ARIMA:')
        end_date = st.date_input('Tanggal Akhir Prediksi ARIMA:')

        if start_date and end_date:
            # Tombol untuk memulai prediksi ARIMA
            if st.button('Prediksi ARIMA'):
                # Filter data berdasarkan nama barang yang dipilih
                df_item = df_actual[df_actual['NAMA_BARANG'] == item_name]
                data = df_item.set_index('TGL_TRANSAKSI')['JUMLAH_STOK']

                arima_forecast, date_range = make_arima_prediction(start_date, end_date, data)

                # Menghitung stok yang dibutuhkan
                required_stock = calculate_required_stock(arima_forecast, buffer_stock, rounding_method)

                # Tampilkan prediksi ARIMA
                st.subheader(f"Prediksi ARIMA dan Stok yang Dibutuhkan untuk {item_name}")
                chart_data = pd.DataFrame({
                    'Tanggal': date_range,
                    'Prediksi ARIMA': arima_forecast,
                    'Stok yang Dibutuhkan': required_stock
                })

                # Ubah kolom Tanggal menjadi format string agar kompatibel dengan altair
                chart_data['Tanggal'] = chart_data['Tanggal'].astype(str)

                # Plot menggunakan Altair
                chart = alt.Chart(chart_data).transform_fold(
                    ['Prediksi ARIMA', 'Stok yang Dibutuhkan']
                ).mark_line().encode(
                    x=alt.X('Tanggal:T', axis=alt.Axis(title='Tanggal')),
                    y=alt.Y('value:Q', title='Stok'),
                    color='key:N'
                ).properties(
                    title=f'Prediksi ARIMA dan Stok yang Dibutuhkan dari {start_date} hingga {end_date} untuk {item_name}'
                ).interactive()
                st.altair_chart(chart, use_container_width=True)

                # Simpan prediksi ke database dan simpan grafik sebagai gambar
                conn = create_connection('localhost', 'root', '', 'db_forecasting')  # Sesuaikan dengan kredensial database Anda
                save_prediction_to_db('ARIMA', start_date, end_date, item_name, arima_forecast, required_stock, date_range, conn)
                conn.close()

                # Tampilkan tabel detail dan deskripsi
                st.subheader("Detail Prediksi ARIMA dan Stok yang Dibutuhkan")
                df_arima = pd.DataFrame({
                    'Tanggal': date_range,
                    'Prediksi ARIMA': arima_forecast,
                    'Stok yang Dibutuhkan': required_stock
                })
                st.write(df_arima)

                # Deskripsi per baris
                st.subheader("Deskripsi per Baris")
                for index, row in df_arima.iterrows():
                    st.write(f"Pada {row['Tanggal']}, prediksi stok ARIMA adalah {row['Prediksi ARIMA']} dan stok yang dibutuhkan adalah {row['Stok yang Dibutuhkan']}.")

    elif model_selection == 'Holt-Winters':
        start_date = st.date_input('Tanggal Mulai Prediksi Holt-Winters:')
        end_date = st.date_input('Tanggal Akhir Prediksi Holt-Winters:')

        if start_date and end_date:
            # Tombol untuk memulai prediksi Holt-Winters
            if st.button('Prediksi Holt-Winters'):
                # Filter data berdasarkan nama barang yang dipilih
                df_item = df_actual[df_actual['NAMA_BARANG'] == item_name]
                data = df_item.set_index('TGL_TRANSAKSI')['JUMLAH_STOK']

                hw_forecast, date_range = make_hw_prediction(start_date, end_date, data)

                # Menghitung stok yang dibutuhkan
                required_stock = calculate_required_stock(hw_forecast, buffer_stock, rounding_method)

                # Tampilkan prediksi Holt-Winters
                st.subheader(f"Prediksi Holt-Winters dan Stok yang Dibutuhkan untuk {item_name}")
                chart_data = pd.DataFrame({
                    'Tanggal': date_range,
                    'Prediksi Holt-Winters': hw_forecast,
                    'Stok yang Dibutuhkan': required_stock
                })

                # Ubah kolom Tanggal menjadi format string agar kompatibel dengan altair
                chart_data['Tanggal'] = chart_data['Tanggal'].astype(str)

                # Plot menggunakan Altair

                chart = alt.Chart(chart_data).transform_fold(
                    ['Prediksi Holt-Winters', 'Stok yang Dibutuhkan']
                ).mark_line().encode(
                    x=alt.X('Tanggal:T', axis=alt.Axis(title='Tanggal')),
                    y=alt.Y('value:Q', title='Stok'),
                    color='key:N'
                ).properties(
                    title=f'Prediksi Holt-Winters dan Stok yang Dibutuhkan dari {start_date} hingga {end_date} untuk {item_name}'
                ).interactive()
                st.altair_chart(chart, use_container_width=True)

                # Simpan prediksi ke database dan simpan grafik sebagai gambar
                conn = create_connection('localhost', 'root', '', 'db_forecasting')  # Sesuaikan dengan kredensial database Anda
                save_prediction_to_db('Holt-Winters',start_date, end_date, item_name, hw_forecast, required_stock, date_range, conn)
                conn.close()

                # Tampilkan tabel detail dan deskripsi
                st.subheader("Detail Prediksi Holt-Winters dan Stok yang Dibutuhkan")
                df_hw = pd.DataFrame({
                    'Tanggal': date_range,
                    'Prediksi Holt-Winters': hw_forecast,
                    'Stok yang Dibutuhkan': required_stock
                })
                st.write(df_hw)

                # Deskripsi per baris
                st.subheader("Deskripsi per Baris")
                for index, row in df_hw.iterrows():
                    st.write(f"Pada {row['Tanggal']}, prediksi stok Holt-Winters adalah {row['Prediksi Holt-Winters']} dan stok yang dibutuhkan adalah {row['Stok yang Dibutuhkan']}.")

# Jalankan aplikasi Streamlit
if __name__ == '__main__':
    show_halaman_prediksi()
