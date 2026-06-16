import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

# ---------------- DATABASE ----------------
conn = sqlite3.connect("expenses.db", check_same_thread=False)
cursor = conn.cursor()

# USERS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# DEFAULT ADMIN
cursor.execute("""
INSERT OR IGNORE INTO users(username, password)
VALUES('admin', 'admin123')
""")

# EXPENSE TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    date TEXT,
    category TEXT,
    amount INTEGER,
    salary INTEGER
)
""")

conn.commit()

# ---------------- SESSION INIT ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None


# ---------------- LOGIN / REGISTER PAGE ----------------
def auth_page():

    st.title("🔐 Personal Finance Tracker - Login System")

    option = st.radio("Choose Option", ["Login", "Register"], key="auth")

    # ---------------- LOGIN ----------------
    if option == "Login":
        st.subheader("Login")

        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            cursor.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, password)
            )
            user = cursor.fetchone()

            if user:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login Successful")
                st.rerun()
            else:
                st.error("Invalid username or password")

    # ---------------- REGISTER ----------------
    else:
        st.subheader("Register")

        new_user = st.text_input("New Username", key="reg_user")
        new_pass = st.text_input("New Password", type="password", key="reg_pass")

        if st.button("Register"):
            try:
                cursor.execute(
                    "INSERT INTO users(username, password) VALUES (?, ?)",
                    (new_user, new_pass)
                )
                conn.commit()
                st.success("Registration successful! Please login.")
            except sqlite3.IntegrityError:
                st.error("Username already exists")

    st.stop()


# ---------------- MAIN APP ----------------
def main_app():

    st.sidebar.write(f"👤 Logged in as: {st.session_state.username}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

    menu = st.sidebar.selectbox(
        "Menu",
        [
            "Add Expense",
            "View Expenses",
            "Total Expenses",
            "Delete Expense",
            "Category Summary",
            "Monthly Budget",
            "Search Expense",
            "Update Expense",
            "Monthly Report",
            "Pie Chart",
            "Export Report"
        ]
    )

    # ---------------- ADD EXPENSE ----------------
    if menu == "Add Expense":
        st.subheader("Add Expense")

        category = st.text_input("Category")
        amount = st.number_input("Amount", min_value=0)
        salary = st.number_input("Salary", min_value=0)

        if st.button("Save Expense"):
            date = datetime.now().strftime("%Y-%m-%d")

            cursor.execute("""
                INSERT INTO expenses(username, date, category, amount, salary)
                VALUES (?, ?, ?, ?, ?)
            """, (st.session_state.username, date, category, amount, salary))

            conn.commit()
            st.success("Expense added")

    # ---------------- VIEW ----------------
    elif menu == "View Expenses":
        st.subheader("All Expenses")

        cursor.execute("""
            SELECT * FROM expenses WHERE username=?
        """, (st.session_state.username,))

        df = pd.DataFrame(
            cursor.fetchall(),
            columns=["ID", "Username", "Date", "Category", "Amount", "Salary"]
        )

        st.dataframe(df)

    # ---------------- TOTAL ----------------
    elif menu == "Total Expenses":
        cursor.execute("""
            SELECT SUM(amount) FROM expenses WHERE username=?
        """, (st.session_state.username,))

        total = cursor.fetchone()[0] or 0
        st.subheader(f"Total Expenses: {total}")

    # ---------------- CATEGORY ----------------
    elif menu == "Category Summary":
        cursor.execute("""
            SELECT category, SUM(amount)
            FROM expenses
            WHERE username=?
            GROUP BY category
        """, (st.session_state.username,))

        st.subheader("Category Summary")

        for row in cursor.fetchall():
            st.write(f"{row[0]} : {row[1]}")

    # ---------------- DELETE ----------------
    elif menu == "Delete Expense":
        st.subheader("Delete Expense")

        exp_id = st.number_input("Expense ID", step=1)

        if st.button("Delete"):
            cursor.execute("""
                DELETE FROM expenses
                WHERE id=? AND username=?
            """, (exp_id, st.session_state.username))

            conn.commit()
            st.success("Deleted")

    # ---------------- BUDGET ----------------
    elif menu == "Monthly Budget":
        budget = st.number_input("Budget")

        cursor.execute("""
            SELECT SUM(amount) FROM expenses WHERE username=?
        """, (st.session_state.username,))

        total = cursor.fetchone()[0] or 0

        remaining = budget - total

        st.write("Budget:", budget)
        st.write("Spent:", total)
        st.write("Remaining:", remaining)

        if remaining < 0:
            st.error("Budget exceeded!")

    # ---------------- SEARCH ----------------
    elif menu == "Search Expense":
        search = st.text_input("Category")

        if st.button("Search"):
            cursor.execute("""
                SELECT * FROM expenses
                WHERE category=? AND username=?
            """, (search, st.session_state.username))

            st.write(cursor.fetchall())

    # ---------------- UPDATE ----------------
    elif menu == "Update Expense":
        exp_id = st.number_input("Expense ID", step=1)
        new_amount = st.number_input("New Amount")

        if st.button("Update"):
            cursor.execute("""
                UPDATE expenses
                SET amount=?
                WHERE id=? AND username=?
            """, (new_amount, exp_id, st.session_state.username))

            conn.commit()
            st.success("Updated")

    # ---------------- REPORT ----------------
    elif menu == "Monthly Report":
        cursor.execute("""
            SELECT SUM(amount) FROM expenses WHERE username=?
        """, (st.session_state.username,))

        total = cursor.fetchone()[0] or 0
        st.subheader(f"Total: {total}")

        cursor.execute("""
            SELECT category, SUM(amount)
            FROM expenses
            WHERE username=?
            GROUP BY category
        """, (st.session_state.username,))

        for row in cursor.fetchall():
            st.write(row)

    # ---------------- PIE CHART ----------------
    elif menu == "Pie Chart":
        cursor.execute("""
            SELECT category, SUM(amount)
            FROM expenses
            WHERE username=?
            GROUP BY category
        """, (st.session_state.username,))

        data = cursor.fetchall()

        if data:
            labels = [x[0] for x in data]
            values = [x[1] for x in data]

            fig, ax = plt.subplots()
            ax.pie(values, labels=labels, autopct="%1.1f%%")
            st.pyplot(fig)

    # ---------------- EXPORT ----------------
    elif menu == "Export Report":
        cursor.execute("""
            SELECT category, SUM(amount)
            FROM expenses
            WHERE username=?
            GROUP BY category
        """, (st.session_state.username,))

        data = cursor.fetchall()

        with open("report.txt", "w") as f:
            f.write("Monthly Report\n\n")
            for row in data:
                f.write(f"{row[0]} : {row[1]}\n")

        st.success("Report exported")


# ---------------- APP FLOW ----------------
if not st.session_state.logged_in:
    auth_page()
else:
    main_app()
