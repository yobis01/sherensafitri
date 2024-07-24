import streamlit as st
import mysql.connector

# Fungsi untuk melakukan koneksi ke database
def connect_to_database():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db_forecasting"
        )
        return conn
    except mysql.connector.Error as e:
        st.error(f"Gagal terhubung ke database: {e}")
        return None

# Fungsi untuk melakukan login
def login(username, password):
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor()
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()
        if result:
            st.session_state.logged_in = True
            st.session_state.user_level = result[3]  # Kolom level_akses
            return True
        else:
            return False

# Fungsi untuk menampilkan halaman login
def show_login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        if login(username, password):
            st.success("Login berhasil!")
            # Hapus form login
            st.empty()
            return True
        else:
            st.error("Username atau password salah.")
            return False

# Fungsi untuk menampilkan tombol logout
def show_logout_button():
    st.button("Logout")

# Main program
def main():
    st.session_state.logged_in = False
    st.session_state.user_level = None

    # Tampilkan halaman login jika user belum login
    if not st.session_state.logged_in:
        st.session_state.logged_in = show_login_page()

    # Tampilkan tombol logout jika user sudah login
    if st.session_state.logged_in:
        show_logout_button()

if __name__ == "__main__":
    main()
