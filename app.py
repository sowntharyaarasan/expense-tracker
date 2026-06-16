import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect("expenses.db")

cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

conn.commit()
cursor.execute("""
INSERT OR IGNORE INTO users(username,password)
VALUES('admin','admin123')
""")

conn.commit()
cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    category TEXT,
    amount INTEGER,
    salary INTEGER
)
""")

conn.commit()

st.title("Personal Finance Tracker")
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if not st.session_state.logged_in:

    st.subheader("Login")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()

        if user:

            st.session_state.logged_in = True

            st.success("Login Successful")

            st.rerun()

        else:

            st.error("Invalid Username or Password")

    st.stop()

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

# ADD EXPENSE
if menu == "Add Expense":

    st.subheader("Add Expense")

    category = st.text_input("Enter Category")

    amount = st.number_input("Enter Amount")

    salary = st.number_input("Enter Salary")

    if st.button("Save Expense"):

        date = datetime.now().strftime("%Y-%m-%d")

        cursor.execute(
            "INSERT INTO expenses(date, category, amount, salary) VALUES(?,?,?,?)",
            (date, category, amount, salary)
        )

        conn.commit()

        st.success("Expense Added Successfully")


# VIEW EXPENSES
elif menu == "View Expenses":

    st.subheader("All Expenses")

    cursor.execute("SELECT * FROM expenses")

    data = cursor.fetchall()

    df = pd.DataFrame(
        data,
        columns=["ID", "Date", "Category", "Amount", "Salary"]
    )

    st.dataframe(df)


# TOTAL EXPENSES
elif menu == "Total Expenses":

    cursor.execute("SELECT SUM(amount) FROM expenses")

    total = cursor.fetchone()[0]

    st.subheader(f"Total Expenses: {total}")


# CATEGORY SUMMARY
elif menu == "Category Summary":

    cursor.execute("""
    SELECT category, SUM(amount)
    FROM expenses
    GROUP BY category
    """)

    data = cursor.fetchall()

    st.subheader("Category Summary")

    for row in data:
        st.write(f"{row[0]} : {row[1]}")


# DELETE EXPENSE
elif menu == "Delete Expense":

    st.subheader("Delete Expense")

    expense_id = st.number_input(
        "Enter Expense ID",
        step=1
    )

    if st.button("Delete"):

        cursor.execute(
            "DELETE FROM expenses WHERE id=?",
            (expense_id,)
        )

        conn.commit()

        st.success("Expense Deleted Successfully")


# MONTHLY BUDGET
elif menu == "Monthly Budget":

    budget = st.number_input("Enter Budget")

    cursor.execute("SELECT SUM(amount) FROM expenses")

    total = cursor.fetchone()[0]

    if total is None:
        total = 0

    remaining = budget - total

    st.write("Budget :", budget)

    st.write("Expenses :", total)

    st.write("Remaining :", remaining)

    if remaining < 0:
        st.error("Budget Exceeded!")


# SEARCH EXPENSE
elif menu == "Search Expense":

    search = st.text_input("Enter Category")

    if st.button("Search"):

        cursor.execute(
            "SELECT * FROM expenses WHERE category=?",
            (search,)
        )

        data = cursor.fetchall()

        st.write(data)


# UPDATE EXPENSE
elif menu == "Update Expense":

    expense_id = st.number_input(
        "Enter Expense ID",
        step=1
    )

    new_amount = st.number_input("Enter New Amount")

    if st.button("Update"):

        cursor.execute(
            "UPDATE expenses SET amount=? WHERE id=?",
            (new_amount, expense_id)
        )

        conn.commit()

        st.success("Expense Updated")


# MONTHLY REPORT
elif menu == "Monthly Report":

    cursor.execute("SELECT SUM(amount) FROM expenses")

    total = cursor.fetchone()[0]

    st.subheader(f"Total Expenses : {total}")

    cursor.execute("""
    SELECT category, SUM(amount)
    FROM expenses
    GROUP BY category
    """)

    data = cursor.fetchall()

    for row in data:
        st.write(f"{row[0]} : {row[1]}")


# PIE CHART
elif menu == "Pie Chart":

    cursor.execute("""
    SELECT category, SUM(amount)
    FROM expenses
    GROUP BY category
    """)

    data = cursor.fetchall()

    categories = []
    amounts = []

    for row in data:
        categories.append(row[0])
        amounts.append(row[1])

    fig, ax = plt.subplots()

    ax.pie(
        amounts,
        labels=categories,
        autopct="%1.1f%%"
    )

    st.pyplot(fig)


# EXPORT REPORT
elif menu == "Export Report":

    cursor.execute("SELECT SUM(amount) FROM expenses")

    total = cursor.fetchone()[0]

    cursor.execute("""
    SELECT category, SUM(amount)
    FROM expenses
    GROUP BY category
    """)

    data = cursor.fetchall()

    report = open("report.txt", "w")

    report.write("Monthly Report\n\n")

    report.write(f"Total Expenses : {total}\n\n")

    for row in data:
        report.write(f"{row[0]} : {row[1]}\n")

    report.close()

    st.success("Report Exported Successfully")