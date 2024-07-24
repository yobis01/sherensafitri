import streamlit as st
import mysql.connector
import pandas as pd
from mysql.connector import Error
import base64

# Function to create MySQL connection
def create_connection():
    conn = None
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # Isi dengan password MySQL Anda
            database="db_forecasting"  # Ganti dengan nama database Anda
        )
        st.success("Connected to MySQL database")
    except Error as e:
        st.error(f"Error connecting to MySQL database: {e}")
    return conn

# Function to fetch transactions from MySQL database with filter options
def view_all_transactions(conn, bulan=None, tahun=None):
    try:
        query = "SELECT * FROM transaksi"

        if bulan and tahun:
            query += f" WHERE MONTH(TGL_TRANSAKSI) = {bulan} AND YEAR(TGL_TRANSAKSI) = {tahun}"

        df = pd.read_sql(query, conn)

        # Convert TGL_TRANSAKSI to datetime
        df['TGL_TRANSAKSI'] = pd.to_datetime(df['TGL_TRANSAKSI'], format='%Y-%m-%d')

        # Group by TGL_TRANSAKSI and NAMA_BARANG and calculate stock balance
        df['JUMLAH_STOK'] = df.groupby(['TGL_TRANSAKSI', 'NAMA_BARANG'])['QTY_KIRIM'].cumsum()

        return df
    except Error as e:
        st.error(f"Error fetching transactions: {e}")
        return None

# Function to add transaction to MySQL database
def add_transaction(conn, data):
    try:
        cursor = conn.cursor()
        sql = """
        INSERT INTO transaksi (BLN, NO_INVOICE, TGL_TRANSAKSI, STORE, MARKETPLACE, NAMA_AKUN, NAMA_CUSTOMER, SUPPLIER, KODE_KIRIM, NAMA_BARANG, QTY_KIRIM, HARGA_JUAL, SUBSIDI_NILAI_BARANG, T_JUAL, DISKON_VOUCHER, DISKON, CASHBACK, PENJ_KOTOR, BATAL_BLN_SEBELUMNYA, PENJ_BERSIH_PPN, DO_UP_RE, TGL_BRG_KBL, KETERANGAN, ONGKIR_KONS, SERVICE_FEE, COMM_FEE_LAZ, CAMPAIGN_FEE, FREE_SHIPPING_MAX_FEE, SHIPPING_FEE_BY_SELLER, TOTAL_TERIMA, BIAYA_LAIN2, COURIER_ACTUAL_FREIGHT_FEE, PENALTY, PEND_LAIN2, NOMINAL_CAIR, KETERANGAN_CAIR, TGL_CAIR, EKSPEDISI, BI_EKS_NON_CASHLESS, SELISIH_EKSP, REMINDER_5_DAYS, TOP, JT, SELISIH, PPH23)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, data)
        conn.commit()
        return True
    except Error as e:
        st.error(f"Error adding transaction: {e}")
        return False

# Function to delete a transaction from MySQL database
def delete_transaction(conn, id_transaksi):
    try:
        cursor = conn.cursor()
        sql = "DELETE FROM transaksi WHERE id = %s"
        cursor.execute(sql, (id_transaksi,))
        conn.commit()
        return True
    except Error as e:
        st.error(f"Error deleting transaction: {e}")
        return False

# Function to update a transaction in MySQL database
def update_transaction(conn, id_transaksi, data):
    try:
        cursor = conn.cursor()
        sql = """
        UPDATE transaksi
        SET BLN = %s, NO_INVOICE = %s, TGL_TRANSAKSI = %s, STORE = %s, MARKETPLACE = %s, NAMA_AKUN = %s, NAMA_CUSTOMER = %s, SUPPLIER = %s, KODE_KIRIM = %s, NAMA_BARANG = %s, QTY_KIRIM = %s, HARGA_JUAL = %s, SUBSIDI_NILAI_BARANG = %s, T_JUAL = %s, DISKON_VOUCHER = %s, DISKON = %s, CASHBACK = %s, PENJ_KOTOR = %s, BATAL_BLN_SEBELUMNYA = %s, PENJ_BERSIH_PPN = %s, DO_UP_RE = %s, TGL_BRG_KBL = %s, KETERANGAN = %s, ONGKIR_KONS = %s, SERVICE_FEE = %s, COMM_FEE_LAZ = %s, CAMPAIGN_FEE = %s, FREE_SHIPPING_MAX_FEE = %s, SHIPPING_FEE_BY_SELLER = %s, TOTAL_TERIMA = %s, BIAYA_LAIN2 = %s, COURIER_ACTUAL_FREIGHT_FEE = %s, PENALTY = %s, PEND_LAIN2 = %s, NOMINAL_CAIR = %s, KETERANGAN_CAIR = %s, TGL_CAIR = %s, EKSPEDISI = %s, BI_EKS_NON_CASHLESS = %s, SELISIH_EKSP = %s, REMINDER_5_DAYS = %s, TOP = %s, JT = %s, SELISIH = %s, PPH23 = %s
        WHERE id = %s
        """
        cursor.execute(sql, data + (id_transaksi,))
        conn.commit()
        return True
    except Error as e:
        st.error(f"Error updating transaction: {e}")
        return False

# Function to handle Excel upload and process data
def handle_excel_upload(conn, uploaded_file):
    try:
        if uploaded_file is not None:
            # Read Excel file with explicit column names matching the database table columns
            columns = ["BLN", "NO_INVOICE", "TGL_TRANSAKSI", "STORE", "MARKETPLACE", "NAMA_AKUN", "NAMA_CUSTOMER", "SUPPLIER", "KODE_KIRIM", "NAMA_BARANG", "QTY_KIRIM", "HARGA_JUAL", "SUBSIDI_NILAI_BARANG", "T_JUAL", "DISKON_VOUCHER", "DISKON", "CASHBACK", "PENJ_KOTOR", "BATAL_BLN_SEBELUMNYA", "PENJ_BERSIH_PPN", "DO_UP_RE", "TGL_BRG_KBL", "KETERANGAN", "ONGKIR_KONS", "SERVICE_FEE", "COMM_FEE_LAZ", "CAMPAIGN_FEE", "FREE_SHIPPING_MAX_FEE", "SHIPPING_FEE_BY_SELLER", "TOTAL_TERIMA", "BIAYA_LAIN2", "COURIER_ACTUAL_FREIGHT_FEE", "PENALTY", "PEND_LAIN2", "NOMINAL_CAIR", "KETERANGAN_CAIR", "TGL_CAIR", "EKSPEDISI", "BI_EKS_NON_CASHLESS", "SELISIH_EKSP", "REMINDER_5_DAYS", "TOP", "JT", "SELISIH", "PPH23"]
            excel_data = pd.read_excel(uploaded_file, sheet_name='Sheet1', names=columns)

            # Replace NaN values with 0
            excel_data.fillna(0, inplace=True)

            # Iterate over rows in the DataFrame and add each row as a transaction
            for index, row in excel_data.iterrows():
                data = tuple(row)
                add_transaction(conn, data)

            st.success("Transactions from Excel file added successfully")
    except Exception as e:
        st.error(f"Error processing Excel file: {e}")

# Function to filter stock information by product name
def filter_stock_by_product(df, product_name):
    try:
        filtered_df = df[df['NAMA_BARANG'] == product_name]
        return filtered_df
    except Exception as e:
        st.error(f"Error filtering stock information: {e}")
        return None

# Function to display transaction management page using Streamlit
def show_halaman_datatransaksi():
    conn = create_connection()
    if conn is not None:
        menu = ["View Transactions", "View All Data", "Add Transaction", "Update Transaction", "Delete Transaction"]
        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "View Transactions":
            st.subheader("View Transactions")

            # Fetch distinct months and years from the database
            try:
                query = "SELECT DISTINCT MONTH(TGL_TRANSAKSI) AS BULAN, YEAR(TGL_TRANSAKSI) AS TAHUN FROM transaksi ORDER BY TAHUN DESC, BULAN DESC"
                distinct_dates = pd.read_sql(query, conn)
                distinct_months = distinct_dates['BULAN'].tolist()
                distinct_years = distinct_dates['TAHUN'].tolist()

                bulan = st.sidebar.selectbox("Select Month", distinct_months, key='bulan')
                tahun = st.sidebar.selectbox("Enter Year", distinct_years, key='tahun')

                df = view_all_transactions(conn, bulan, tahun)
                if df is not None:
                    st.dataframe(df)
                    
                    # Filter by product name
                    product_names = df['NAMA_BARANG'].unique().tolist()
                    selected_product = st.sidebar.selectbox("Select Product", product_names)
                    filtered_df = filter_stock_by_product(df, selected_product)

                    # Calculate and display stock information outside the table
                    st.subheader("Stock Information")
                    stock_info = filtered_df.groupby(['TGL_TRANSAKSI', 'NAMA_BARANG'])['JUMLAH_STOK'].last().reset_index()

                    # Create a complete date range
                    date_range = pd.date_range(start=df['TGL_TRANSAKSI'].min(), end=df['TGL_TRANSAKSI'].max(), freq='D')
                    complete_df = pd.DataFrame(date_range, columns=['TGL_TRANSAKSI'])
                    complete_df['NAMA_BARANG'] = selected_product
                    complete_df = pd.merge(complete_df, stock_info, on=['TGL_TRANSAKSI', 'NAMA_BARANG'], how='left')
                    complete_df['JUMLAH_STOK'].fillna(0, inplace=True)

                    st.write(complete_df)
                    
                    # Add download link for stock info CSV
                    st.subheader("Download Stock Information")
                    csv = complete_df.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="stock_info.csv">Download CSV</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    
                else:
                    st.warning("No transactions found.")

            except Error as e:
                st.error(f"Error fetching distinct months and years: {e}")

        elif choice == "View All Data":
                st.subheader("View All Data")
                df = view_all_transactions(conn)
                if df is not None:
                    st.dataframe(df)
                    
                    # Filter by product name
                    product_names = df['NAMA_BARANG'].unique().tolist()
                    selected_product = st.sidebar.selectbox("Select Product", product_names)
                    filtered_df = filter_stock_by_product(df, selected_product)

                    # Calculate and display stock information outside the table
                    st.subheader("Stock Information")
                    stock_info = filtered_df.groupby(['TGL_TRANSAKSI', 'NAMA_BARANG'])['JUMLAH_STOK'].last().reset_index()

                    # Create a complete date range
                    date_range = pd.date_range(start=df['TGL_TRANSAKSI'].min(), end=df['TGL_TRANSAKSI'].max(), freq='D')
                    complete_df = pd.DataFrame(date_range, columns=['TGL_TRANSAKSI'])
                    complete_df['NAMA_BARANG'] = selected_product
                    complete_df = pd.merge(complete_df, stock_info, on=['TGL_TRANSAKSI', 'NAMA_BARANG'], how='left')
                    complete_df['JUMLAH_STOK'].fillna(0, inplace=True)

                    st.write(complete_df)
                    
                    # Add download link for stock info CSV
                    st.subheader("Download Stock Information")
                    csv = complete_df.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="stock_info.csv">Download CSV</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    
                else:
                    st.warning("No transactions found.")

        elif choice == "Add Transaction":
                st.subheader("Add Transaction")
                uploaded_file = st.file_uploader("Upload Excel File", type=['xlsx', 'xls'])
                if uploaded_file is not None:
                    handle_excel_upload(conn, uploaded_file)

        elif choice == "Update Transaction":
                st.subheader("Update Transaction")
                id_transaksi = st.number_input("ID Transaction to Update", min_value=1)
                # Implement update form here

                if st.button("Update Transaction"):
                    data = tuple()  # Replace with data from update form
                    if update_transaction(conn, id_transaksi, data):
                        st.success("Transaction updated successfully")

        elif choice == "Delete Transaction":
                st.subheader("Delete Transaction")
                id_transaksi = st.number_input("ID Transaction to Delete", min_value=1)

                if st.button("Delete Transaction"):
                    if delete_transaction(conn, id_transaksi):
                        st.success("Transaction deleted successfully")

        conn.close()

if __name__ == "__main__":
    show_halaman_datatransaksi()

           
