import streamlit as st
import mysql.connector
import csv
import pandas as pd
from datetime import datetime
from dateutil import parser

# Function to connect to the database
def connect_to_database():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # Your MySQL password
            database="db_forecasting"  # Your database name
        )
        return conn
    except mysql.connector.Error as e:
        st.error(f"Failed to connect to database: {e}")
        return None

# Fungsi data_exists diperbarui sesuai dengan contoh di atas
def data_exists(conn, tanggal, nama_barang):
    cursor = conn.cursor()
    query = "SELECT COUNT(*) FROM forecasting WHERE TGL_TRANSAKSI = %s AND NAMA_BARANG = %s"
    cursor.execute(query, (tanggal, nama_barang))
    count = cursor.fetchone()[0]
    return count > 0

# Function to export data to CSV
def export_to_csv(data):
    with open('data_barang.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)
    st.success("Data successfully exported to data_barang.csv")

# Function to add new data
def add_data(tanggal, stok_barang):
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor()
        query = "INSERT INTO forecasting (TGL_TRANSAKSI, NAMA_BARANG, JUMLAH_STOK) VALUES (%s, %s, %s)"
        cursor.execute(query, (tanggal, 'Barang Default', stok_barang))  # Example for NAMA_BARANG
        conn.commit()
        st.success("Data added successfully!")
        conn.close()

# Function to display all data
def show_all_data():
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor()
        query = "SELECT * FROM forecasting"
        cursor.execute(query)
        result = cursor.fetchall()
        
        # Sidebar filters
        selected_month = st.sidebar.selectbox("Filter Month:", ["All"] + [str(i) for i in range(1, 13)])
        years = [str(row[0].year) for row in result]
        selected_year = st.sidebar.selectbox("Filter Year:", ["All"] + list(set(years)))
        
        # Display data in a table using st.table()
        st.write('<style> table { width: 100%; border-collapse: collapse; } th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; } tr:hover { background-color: #f2f2f2; } th { background-color: #4CAF50; color: white; } </style>', unsafe_allow_html=True)
        table_data = [["TGL_TRANSAKSI", "NAMA_BARANG", "JUMLAH_STOK"]]
        for row in result:
            if (selected_month == "All" or str(row[0].month) == selected_month) and (selected_year == "All" or str(row[0].year) == selected_year):
                table_data.append([row[0], row[1], row[2]])
        st.table(table_data)

        # Button to export data to CSV
        if st.button("Export to CSV"):
            export_to_csv(table_data)
            
        conn.close()

# Function to update data based on date
def update_data(tanggal, stok_barang):
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor()
        
        # Retrieve current data before update
        query_select = "SELECT * FROM forecasting WHERE TGL_TRANSAKSI = %s"
        cursor.execute(query_select, (tanggal,))
        current_data = cursor.fetchone()
        
        if current_data:
            st.write(f"Previous data: TGL_TRANSAKSI {current_data[0]}, JUMLAH_STOK {current_data[2]}")
        
            # Perform the update
            query_update = "UPDATE forecasting SET JUMLAH_STOK = %s WHERE TGL_TRANSAKSI = %s"
            cursor.execute(query_update, (stok_barang, tanggal))
            conn.commit()
            st.success("Data updated successfully!")
        else:
            st.error(f"No data found for date {tanggal}")
        
        conn.close()

# Function to delete data based on date
def delete_data(tanggal):
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor()
        query = "DELETE FROM forecasting WHERE TGL_TRANSAKSI = %s"
        cursor.execute(query, (tanggal,))
        conn.commit()
        st.success("Data deleted successfully!")
        conn.close()

def add_data_from_csv(file):
    try:
        conn = connect_to_database()
        if conn:
            cursor = conn.cursor()
            data = pd.read_csv(file)
            added_count = 0
            for _, row in data.iterrows():
                try:
                    tanggal = parser.parse(row['TGL_TRANSAKSI']).date()  # Parsing the date
                except ValueError:
                    st.error(f"Invalid date format for row: {row}")
                    continue
                
                stok_barang = row['JUMLAH_STOK']
                nama_barang = row['NAMA_BARANG']  # Assuming 'NAMA_BARANG' is a column in your CSV
                
                # Check if data already exists for the given date and product name
                if not data_exists(conn, tanggal, nama_barang):
                    query = "INSERT INTO forecasting (TGL_TRANSAKSI, NAMA_BARANG, JUMLAH_STOK) VALUES (%s, %s, %s)"
                    cursor.execute(query, (tanggal, nama_barang, stok_barang))
                    added_count += 1
            
            conn.commit()
            st.success(f"{added_count} data from CSV added successfully!")
            conn.close()
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Main program
def show_halaman_datastok():
    st.title("Stock Data")
    
    # CRUD operations selection
    st.sidebar.title("CRUD Operations")
    operation = st.sidebar.radio("", ["Add Data", "Show Data", "Update Data", "Delete Data"])

    if operation == "Add Data":
        st.header("Add New Data")
        tanggal = st.date_input("Date:")
        stok_barang = st.number_input("Stock:")
        if st.button("Add"):
            add_data(tanggal, stok_barang)

        st.header("Add Data from CSV")
        uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
        if uploaded_file is not None:
            if st.button("Add Data from CSV"):
                add_data_from_csv(uploaded_file)

    elif operation == "Show Data":
        show_all_data()

    elif operation == "Update Data":
        st.header("Update Data")
        tanggal = st.date_input("Date to update:")
        stok_barang = st.number_input("New Stock:")
        if st.button("Update"):
            update_data(tanggal, stok_barang)

    elif operation == "Delete Data":
        st.header("Delete Data")
        tanggal = st.date_input("Date to delete:")
        if st.button("Delete"):
            delete_data(tanggal)

# Running the Streamlit application
if __name__ == "__main__":
    show_halaman_datastok()
