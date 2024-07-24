import streamlit as st
import mysql.connector
import pandas as pd
from io import BytesIO
from streamlit_option_menu import option_menu

# Function to create MySQL connection
def create_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Your MySQL password
        database="db_forecasting"  # Your database name
    )
    return conn

# Function to fetch data from a table
def fetch_data(query, conn):
    return pd.read_sql(query, conn)

def get_data_forecasting(conn):
    query = "SELECT * FROM forecasting"
    return fetch_data(query, conn)

def get_data_history_model(conn):
    query = "SELECT * FROM history_model"
    return fetch_data(query, conn)

def get_data_transaksi(conn):
    query = "SELECT * FROM transaksi"
    return fetch_data(query, conn)

def get_data_users(conn):
    query = "SELECT * FROM users"
    return fetch_data(query, conn)

# Function to convert DataFrame to Excel
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    processed_data = output.getvalue()
    return processed_data

# Function to provide download link for Excel file
def download_excel(df, filename):
    excel_data = to_excel(df)
    st.download_button(label='Download Excel', data=excel_data, file_name=filename, mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# Function to show the report page
def show_halaman_laporan():
    st.title("Report Page")

    # Create a menu for different reports
    selected_report = option_menu(
        menu_title=None,
        options=["Forecasting", "History Model", "Transaksi", "Users"],
        icons=["graph-up-arrow", "history", "transactions", "users"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
    )

    conn = create_connection()

    if selected_report == "Forecasting":
        df_forecasting = get_data_forecasting(conn)
        st.subheader("Forecasting Data")
        st.dataframe(df_forecasting)
        download_excel(df_forecasting, 'forecasting_data.xlsx')

    elif selected_report == "History Model":
        df_history_model = get_data_history_model(conn)
        st.subheader("History Model Data")
        st.dataframe(df_history_model)
        download_excel(df_history_model, 'history_model_data.xlsx')

    elif selected_report == "Transaksi":
        df_transaksi = get_data_transaksi(conn)
        st.subheader("Transaksi Data")
        st.dataframe(df_transaksi)
        download_excel(df_transaksi, 'transaksi_data.xlsx')

    elif selected_report == "Users":
        df_users = get_data_users(conn)
        st.subheader("Users Data")
        st.dataframe(df_users)
        download_excel(df_users, 'users_data.xlsx')

    conn.close()

# Run the Streamlit app
if __name__ == "__main__":
    show_halaman_laporan()
