import streamlit as st
from streamlit_option_menu import option_menu
import halaman_utama
import halaman_prediksi
import halaman_laporan

def main():
    # Menu utama
    selected = option_menu(
        menu_title=None,  # required
        options=["Home", "Data Prediksi",  "Laporan"],  # required
        icons=["house", "graph-up-arrow",  "file-earmark-bar-graph"],  # optional
        menu_icon="cast",  # optional
        default_index=0,  # optional
        orientation="horizontal",
    )

    # Tampilkan halaman sesuai pilihan di menu utama
    if selected == "Home":
        halaman_utama.show_halaman_utama()
    elif selected == "Data Prediksi":
        halaman_prediksi.show_halaman_prediksi()
        
    elif selected == "Laporan":
        halaman_laporan.show_halaman_laporan()

if __name__ == "__main__":
    main()
