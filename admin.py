import streamlit as st
from streamlit_option_menu import option_menu
import halaman_utama
import halaman_prediksi
import halaman_users
import halaman_datastok
import halaman_datatransaksi
import halaman_laporan
import halaman_trainingmodel

def main():
    st.image('./Gambar/LogoKarya.png', width=200)
    # Menu utama
    selected = option_menu(
        menu_title=None,  # required
        options=["Home","Data Users", "Data Barang", "Training Model", "Data Prediksi", "Laporan"],  # required
        icons=["house", "graph-up-arrow","box", "box", "file-earmark-bar-graph", "file-earmark-check"],  # optional
        menu_icon="cast",  # optional
        default_index=0,  # optional
        orientation="horizontal",
    )

    # Tampilkan halaman sesuai pilihan di menu utama
    if selected == "Home":
        halaman_utama.show_halaman_utama()
    elif selected == "Data Users":
        halaman_users.show_halaman_users()
    elif selected == "Data Prediksi":
        halaman_prediksi.show_halaman_prediksi()
    elif selected == "Data Barang":
        # Dropdown tambahan untuk sub-menu Data Barang
        sub_selected = option_menu(
            menu_title="Pilih Sub Menu",  # required
            options=["Data Stok", "Data Transaksi"],  # required
            icons=["file-earmark", "file-earmark-plus"],  # optional
            menu_icon="cast",  # optional
            default_index=0,  # optional
            orientation="vertical",
        )
        if sub_selected == "Data Stok":
            halaman_datastok.show_halaman_datastok()
        elif sub_selected == "Data Transaksi":
            halaman_datatransaksi.show_halaman_datatransaksi()
       
        
    elif selected == "Laporan":
        halaman_laporan.show_halaman_laporan()
    elif selected == "Training Model":
        halaman_trainingmodel.show_halaman_trainingmodel()

if __name__ == "__main__":
    main()
