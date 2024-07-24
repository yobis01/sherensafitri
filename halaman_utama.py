import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import os
import json
from mysql.connector import Error

# Function to create MySQL connection
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

# Function to fetch data from a table
def fetch_data(query, conn):
    return pd.read_sql(query, conn)

# Function to show the statistics dashboard
def show_halaman_utama():
   

    # Buat koneksi MySQL
    conn = create_connection('localhost', 'root', '', 'db_forecasting')  # Update with your database credentials

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM prediction_results")
        results = cursor.fetchall()

        for result in results:
            st.subheader(f"Prediction Result: {result['model_type']}")
            st.write(f"Start Date: {result['start_date']}")
            st.write(f"End Date: {result['end_date']}")
            st.write(f"Created At: {result['created_at']}")

            # Read forecast and required_stock as JSON strings
            forecast_data = json.loads(result['forecast'])
            required_stock_data = json.loads(result['required_stock'])

            # Convert JSON data to DataFrames
            forecast_df = pd.DataFrame(forecast_data, columns=['Date', 'Forecast'])
            required_stock_df = pd.DataFrame(required_stock_data, columns=['Date', 'Required Stock'])

            # Set 'Date' as index
            forecast_df['Date'] = pd.to_datetime(forecast_df['Date'])
            forecast_df.set_index('Date', inplace=True)

            required_stock_df['Date'] = pd.to_datetime(required_stock_df['Date'])
            required_stock_df.set_index('Date', inplace=True)

            # Concatenate DataFrames
            combined_df = pd.concat([forecast_df, required_stock_df], axis=1)

            st.write(combined_df)

            # Display plot
            image_path = result['image_path']
            if os.path.exists(image_path):
                st.image(image_path, caption=f"{result['model_type']} Forecast Plot")
            else:
                st.warning("Image not found.")
    except Error as e:
        st.error(f"Kesalahan saat mengambil data dari database: {e}")
    finally:
        conn.close()

# Run the Streamlit app
if __name__ == "__main__":
    show_halaman_utama()
