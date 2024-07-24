import streamlit as st
import mysql.connector
from mysql.connector import Error

# Fungsi untuk menghubungkan ke database MySQL
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',  # Ganti dengan host MySQL Anda
            user='root',  # Ganti dengan user MySQL Anda
            password='',  # Ganti dengan password MySQL Anda
            database='db_forecasting'  # Ganti dengan nama database Anda
        )
        if connection.is_connected():
            st.success("Connected to MySQL Database")
            return connection
    except Error as e:
        st.error(f"Error while connecting to MySQL: {e}")
        return None

def main():
    st.title("Test MySQL Connection")

    connection = create_connection()

    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if tables:
                st.write("Tables in the database:")
                for table in tables:
                    st.write(table)
            else:
                st.warning("No tables found in the database.")
            
            cursor.close()
        except Error as e:
            st.error(f"Error while fetching tables: {e}")
        finally:
            connection.close()
    else:
        st.error("Failed to connect to the database.")

if __name__ == '__main__':
    main()
