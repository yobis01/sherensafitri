import streamlit as st
import mysql.connector
from mysql.connector import Error
import subprocess

# Fungsi untuk membuat koneksi ke database MySQL
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='db_forecasting'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        st.error(f"Error saat menghubungkan ke MySQL: {e}")
        return None

# Fungsi untuk memeriksa kredensial pengguna
def check_credentials(username, password):
    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Query untuk memeriksa username dan password
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        
        cursor.close()
        connection.close()
        return user
    except Error as e:
        st.error(f"Error: {e}")
        return None

# Fungsi untuk mendaftarkan pengguna baru
def register_user(username, password, level_akses):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        
        # Query untuk mendaftarkan pengguna baru
        query = "INSERT INTO users (username, password, level_akses) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, password, level_akses))
        connection.commit()
        
        cursor.close()
        connection.close()
        return True
    except Error as e:
        st.error(f"Error: {e}")
        return False

# Fungsi utama untuk aplikasi Streamlit
def main():
    st.image('./Gambar/LogoKarya.png', width=200)
    st.title("Tentang CV. Karya Anak Bangsa")
    st.markdown("<p style='font-size: 18px; text-align: justify;'>CV. Karya Anak Bangsa merupakan badan usaha yang bergerak dibidang pemasaran online yang berada di bawah naungan PT. Dialogue Garmindo Utama dan tergabung sebagai perusahaan distributor dalam Dialogue Management Group. CV. Karya Anak Bangsa didirikan pada tanggal 01 Oktober 2021 yang berada di Jl. Moh Toha No.86 , Kel. Pelindung Hewan , Kec. Astana Anyar , Kota Bandung , Jawa Barat , 40243.</p>", unsafe_allow_html=True)

   
    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        st.sidebar.subheader("Login")

        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")

        if st.sidebar.button("Login"):
            user = check_credentials(username, password)
            if user:
                st.sidebar.success(f"Berhasil login sebagai: {user['username']} ({user['level_akses']})")
                
                # Redirect ke script yang tepat berdasarkan level_akses
                if user['level_akses'] == 'Admin':
                    st.write("Mengarahkan ke halaman Admin...")
                    subprocess.run(['streamlit', 'run', 'admin.py'])
                    st.stop()
                elif user['level_akses'] == 'Manager':
                    st.write("Mengarahkan ke halaman Manager...")
                    subprocess.run(['streamlit', 'run', 'Manager.py'])
                    st.stop()
                elif user['level_akses'] == 'KepalaGudang':
                    st.write("Mengarahkan ke halaman Kepala Gudang...")
                    subprocess.run(['streamlit', 'run', 'kepala_gudang.py'])
                    st.stop()
                else:
                    st.error("Level akses tidak dikenali!")

            else:
                st.error("Username atau password salah")

    elif choice == "Register":
        st.sidebar.subheader("Registrasi")

        new_username = st.sidebar.text_input("Username Baru")
        new_password = st.sidebar.text_input("Password Baru", type="password")
        level_akses = st.sidebar.selectbox("Level Akses", ["Admin", "Manager", "KepalaGudang"])

        if st.sidebar.button("Register"):
            if register_user(new_username, new_password, level_akses):
                st.sidebar.success("Pengguna berhasil terdaftar")
            else:
                st.sidebar.error("Gagal mendaftarkan pengguna")

if __name__ == '__main__':
    main()
