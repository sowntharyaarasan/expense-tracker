from datetime import datetime
import matplotlib.pyplot as plt
import sqlite3
import tkinter as tk
conn = sqlite3.connect("expenses.db")

cursor = conn.cursor()

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
def add_exp():
    category=input("Enter the category:")
    salary=int(input("Enter the income:"))
    amount=int(input("Enter the amount spent:"))
    date=datetime.now().strftime("%Y-%m-%d")
    cursor.execute(
    "INSERT INTO expenses(date, category, amount, salary) VALUES(?,?,?,?)",
    (date, category, amount, salary)
)

conn.commit()

print("Expense Added Successfully")
def view_exp():

    cursor.execute("SELECT * FROM expenses")

    data = cursor.fetchall()

    for row in data:
        print(row)
def tot_exp():

    cursor.execute("SELECT SUM(amount) FROM expenses")

    total = cursor.fetchone()[0]

    print("Total Expenses:", total)

def del_exp():

    cursor.execute("SELECT * FROM expenses")

    data = cursor.fetchall()

    for row in data:
        print(row)

    expense_id = int(input("Enter expense id to delete: "))

    cursor.execute(
        "DELETE FROM expenses WHERE id=?",
        (expense_id,)
    )

    conn.commit()

    print("Expense deleted successfully")
def category_summary():

    cursor.execute("""
    SELECT category, SUM(amount)
    FROM expenses
    GROUP BY category
    """)

    data = cursor.fetchall()

    print("\nCategory Summary")

    for row in data:
        print(row[0], ":", row[1])
def monthly_budget():

    budget = int(input("Enter Monthly Budget: "))

    cursor.execute("SELECT SUM(amount) FROM expenses")

    total = cursor.fetchone()[0]

    if total is None:
        total = 0

    remaining = budget - total

    print("Budget :", budget)

    print("Expenses :", total)

    print("Remaining :", remaining)

    if remaining < 0:
        print("Budget Exceeded!")
def search_exp():

    search = input("Enter category to search: ")

    cursor.execute(
        "SELECT * FROM expenses WHERE category=?",
        (search,)
    )

    data = cursor.fetchall()

    if data:
        for row in data:
            print(row)
    else:
        print("No records found")
def update_exp():

    cursor.execute("SELECT * FROM expenses")

    data = cursor.fetchall()

    for row in data:
        print(row)

    expense_id = int(input("Enter expense id: "))

    new_amount = int(input("Enter new amount: "))

    cursor.execute(
        "UPDATE expenses SET amount=? WHERE id=?",
        (new_amount, expense_id)
    )

    conn.commit()

    print("Expense updated successfully")
def monthly_report():

    cursor.execute("SELECT SUM(amount) FROM expenses")

    total = cursor.fetchone()[0]

    cursor.execute("""
    SELECT category, SUM(amount)
    FROM expenses
    GROUP BY category
    """)

    summary = cursor.fetchall()

    print("===== Monthly Report =====")

    print("Total Expenses:", total)

    print("\nCategory Summary")

    for row in summary:
        print(row[0], ":", row[1])
def pie_chart():

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

    plt.pie(amounts, labels=categories, autopct="%1.1f%%")

    plt.title("Expense Distribution")

    plt.show()
def export_report():

    cursor.execute("SELECT SUM(amount) FROM expenses")

    total = cursor.fetchone()[0]

    cursor.execute("""
    SELECT category, SUM(amount)
    FROM expenses
    GROUP BY category
    """)

    summary = cursor.fetchall()

    report = open("report.txt", "w")

    report.write("===== Monthly Report =====\n\n")

    report.write(f"Total Expenses : {total}\n\n")

    report.write("Category Summary\n")

    for row in summary:
        report.write(f"{row[0]} : {row[1]}\n")

    report.close()

    print("Report exported successfully")

conn.close()
