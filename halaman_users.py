import streamlit as st
import mysql.connector
import pandas as pd
from io import BytesIO

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

# Function to create MySQL connection
def create_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="db_forecasting"
    )
    return conn

def add_user(conn, username, password, level_akses):
    try:
        cursor = conn.cursor()
        sql = "INSERT INTO users (username, password, level_akses) VALUES (%s, %s, %s)"
        val = (username, password, level_akses)
        cursor.execute(sql, val)
        conn.commit()
        return cursor.lastrowid
    except mysql.connector.Error as e:
        st.error(f"Error adding user: {e}")
        return None

def view_all_users(conn):
    try:
        query = "SELECT * FROM users"
        df = pd.read_sql(query, conn)
        return df
    except mysql.connector.Error as e:
        st.error(f"Error fetching users: {e}")
        return None

def get_data_users(conn, id_users):
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE id_users=%s"
        cursor.execute(query, (id_users,))
        user = cursor.fetchone()
        cursor.close()
        return user
    except mysql.connector.Error as e:
        st.error(f"Error getting user: {e}")
        return None

def update_user(conn, id_users, username, password, level_akses):
    try:
        cursor = conn.cursor()
        sql = "UPDATE users SET username=%s, password=%s, level_akses=%s WHERE id=%s"
        val = (username, password, level_akses, id_users)
        cursor.execute(sql, val)
        conn.commit()
        return True
    except mysql.connector.Error as e:
        st.error(f"Error updating user: {e}")
        return False

def delete_user(conn, id_users):
    try:
        cursor = conn.cursor()
        sql = "DELETE FROM users WHERE id_users=%s"
        val = (id_users,)
        cursor.execute(sql, val)
        conn.commit()
        return True
    except mysql.connector.Error as e:
        st.error(f"Error deleting user: {e}")
        return False

def show_halaman_users():
    # Create MySQL connection
    conn = create_connection()

    menu = ["View Users", "Add User", "Update User", "Delete User"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "View Users":
        st.subheader("View Users")
        df = view_all_users(conn)
        if df is not None:
            st.dataframe(df)
            
            # Add download button
            download_excel(df, 'users.xlsx')
        else:
            st.warning("No users found.")

    elif choice == "Add User":
        st.subheader("Add User")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        level_akses = st.selectbox("Level Akses", ["Admin", "Manager", "KepalaGudang"])

        if st.button("Add User"):
            if username and password:
                if add_user(conn, username, password, level_akses):
                    st.success("User added successfully")
                else:
                    st.error("Failed to add user")
            else:
                st.warning("Username and password are required")

    elif choice == "Update User":
        st.subheader("Update User")
        id_users = st.number_input("ID User to Update", min_value=1)
        result = get_data_users(conn, id_users)
        if result:
            st.write(result)
            username = st.text_input("Username", result['username'])
            password = st.text_input("Password", result['password'], type="password")
            # Define options and index based on available options
            level_akses_options = ["Admin", "Manager", "KepalaGudang"]
            index_level_akses = level_akses_options.index(result['level_akses']) if result['level_akses'] in level_akses_options else 0
            level_akses = st.selectbox("Level Akses", level_akses_options, index=index_level_akses)

            if st.button("Update User"):
                if update_user(conn, id_users, username, password, level_akses):
                    st.success("User updated successfully")
                else:
                    st.error("Failed to update user")
        else:
            st.warning("User not found")

    elif choice == "Delete User":
        st.subheader("Delete User")
        id_users = st.number_input("ID User to Delete", min_value=1)

        if st.button("Delete User"):
            if delete_user(conn, id_users):
                st.success("User deleted successfully")
            else:
                st.error("Failed to delete user")

    conn.close()

# Main program
if __name__ == "__main__":
    show_halaman_users()
