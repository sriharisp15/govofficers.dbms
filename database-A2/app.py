import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# ─── DB CONNECTION ─────────────────────────────────────────────
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Srihari1557",
        database="govt_db"
    )

# ─── SMART CONDITION PARSER ────────────────────────────────────
# Type >50000, <30, >=40000, <=25, =100, or just 50000 in any numeric field
# Text fields do LIKE %value%
def parse_condition(col, val, is_numeric=False):
    val = val.strip()
    if not val:
        return None, None
    if is_numeric:
        if val.startswith(">="):
            return f"{col} >= %s", val[2:].strip()
        elif val.startswith("<="):
            return f"{col} <= %s", val[2:].strip()
        elif val.startswith(">"):
            return f"{col} > %s", val[1:].strip()
        elif val.startswith("<"):
            return f"{col} < %s", val[1:].strip()
        elif val.startswith("="):
            return f"{col} = %s", val[1:].strip()
        else:
            return f"{col} = %s", val
    else:
        return f"{col} LIKE %s", f"%{val}%"

def build_query(base_query, field_map):
    conditions = []
    values = []
    for col, val, is_numeric in field_map:
        cond, v = parse_condition(col, val, is_numeric)
        if cond:
            conditions.append(cond)
            values.append(v)
    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)
    return base_query, values

# ─── MAIN WINDOW ───────────────────────────────────────────────
root = tk.Tk()
root.title("Government Database System")
root.geometry("950x680")
root.resizable(True, True)

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# ═══════════════════════════════════════════════════════════════
# TAB 1 — OFFICERS
# ═══════════════════════════════════════════════════════════════
tab1 = tk.Frame(notebook, bg="#f0f0f0")
notebook.add(tab1, text="  👮 Officers  ")

fields1 = ["Officer ID", "Name", "Department", "Designation", "Salary", "City", "Age"]
entries1 = {}

input_frame1 = tk.Frame(tab1, bg="#f0f0f0")
input_frame1.pack(pady=10, padx=10, anchor="w")

for i, field in enumerate(fields1):
    tk.Label(input_frame1, text=field, bg="#f0f0f0", width=12, anchor="w",
             font=("Arial", 10)).grid(row=i, column=0, pady=3, sticky="w")
    e = tk.Entry(input_frame1, width=25, font=("Arial", 10))
    e.grid(row=i, column=1, pady=3, padx=5)
    entries1[field] = e

def clear_officers():
    for e in entries1.values():
        e.delete(0, tk.END)

def load_tree1(rows):
    tree1.delete(*tree1.get_children())
    for row in rows:
        tree1.insert("", "end", values=row)

def view_officers():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT officer_id, name, department, designation, salary, city, age FROM officers")
        load_tree1(cursor.fetchall())
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def smart_search():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        field_map = [
            ("officer_id",  entries1["Officer ID"].get(),  True),
            ("name",        entries1["Name"].get(),        False),
            ("department",  entries1["Department"].get(),  False),
            ("designation", entries1["Designation"].get(), False),
            ("salary",      entries1["Salary"].get(),      True),
            ("city",        entries1["City"].get(),        False),
            ("age",         entries1["Age"].get(),         True),
        ]
        base = "SELECT officer_id, name, department, designation, salary, city, age FROM officers"
        query, values = build_query(base, field_map)
        cursor.execute(query, values)
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            messagebox.showinfo("No Results", "No records found!")
        load_tree1(rows)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def add_officer():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO officers (officer_id, name, department, designation, salary, city, age)
                          VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                       (entries1["Officer ID"].get(), entries1["Name"].get(),
                        entries1["Department"].get(), entries1["Designation"].get(),
                        entries1["Salary"].get(), entries1["City"].get(),
                        entries1["Age"].get()))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Officer added!")
        view_officers()
        clear_officers()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def update_officer():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""UPDATE officers SET name=%s, department=%s, designation=%s,
                          salary=%s, city=%s, age=%s WHERE officer_id=%s""",
                       (entries1["Name"].get(), entries1["Department"].get(),
                        entries1["Designation"].get(), entries1["Salary"].get(),
                        entries1["City"].get(), entries1["Age"].get(),
                        entries1["Officer ID"].get()))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Officer updated!")
        view_officers()
        clear_officers()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def remove_officer():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM officers WHERE officer_id=%s",
                       (entries1["Officer ID"].get(),))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Officer removed!")
        view_officers()
        clear_officers()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def select_officer(event):
    try:
        selected = tree1.focus()
        values = tree1.item(selected, "values")
        clear_officers()
        keys = ["Officer ID", "Name", "Department", "Designation", "Salary", "City", "Age"]
        for i, key in enumerate(keys):
            entries1[key].insert(0, values[i])
    except:
        pass

btn_frame1 = tk.Frame(tab1, bg="#f0f0f0")
btn_frame1.pack(pady=5)

for text, cmd in [("Add", add_officer), ("View", view_officers),
                  ("Search", smart_search), ("Update", update_officer),
                  ("Remove", remove_officer), ("Reset", clear_officers)]:
    tk.Button(btn_frame1, text=text, command=cmd, width=10,
              font=("Arial", 10), relief="raised", bg="#e0e0e0").pack(side="left", padx=5)

tree_frame1 = tk.Frame(tab1)
tree_frame1.pack(fill="both", expand=True, padx=10, pady=5)

cols1 = ("ID", "Name", "Department", "Designation", "Salary", "City", "Age")
tree1 = ttk.Treeview(tree_frame1, columns=cols1, show="headings", height=10)
for col in cols1:
    tree1.heading(col, text=col)
    tree1.column(col, width=120, anchor="center")

scroll1y = ttk.Scrollbar(tree_frame1, orient="vertical", command=tree1.yview)
scroll1x = ttk.Scrollbar(tree_frame1, orient="horizontal", command=tree1.xview)
tree1.configure(yscrollcommand=scroll1y.set, xscrollcommand=scroll1x.set)
scroll1y.pack(side="right", fill="y")
scroll1x.pack(side="bottom", fill="x")
tree1.pack(fill="both", expand=True)
tree1.bind("<ButtonRelease-1>", select_officer)

tk.Label(tab1,
         text="💡 Tip: Salary='>50000' | Age='<30' | Officer ID=16 | Department=Police + Salary='>50000'",
         bg="#f0f0f0", fg="#555", font=("Arial", 9, "italic")).pack(pady=2)

# ═══════════════════════════════════════════════════════════════
# TAB 2 — DEPARTMENTS
# ═══════════════════════════════════════════════════════════════
tab2 = tk.Frame(notebook, bg="#f0f0f0")
notebook.add(tab2, text="  🏢 Departments  ")

fields2 = ["Dept ID", "Dept Name", "Location", "Head Name", "Budget"]
entries2 = {}

input_frame2 = tk.Frame(tab2, bg="#f0f0f0")
input_frame2.pack(pady=10, padx=10, anchor="w")

for i, field in enumerate(fields2):
    tk.Label(input_frame2, text=field, bg="#f0f0f0", width=12, anchor="w",
             font=("Arial", 10)).grid(row=i, column=0, pady=3, sticky="w")
    e = tk.Entry(input_frame2, width=25, font=("Arial", 10))
    e.grid(row=i, column=1, pady=3, padx=5)
    entries2[field] = e

def clear_dept():
    for e in entries2.values():
        e.delete(0, tk.END)

def view_dept():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM departments")
        rows = cursor.fetchall()
        conn.close()
        tree2.delete(*tree2.get_children())
        for row in rows:
            tree2.insert("", "end", values=row)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def search_dept():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        field_map = [
            ("dept_id",   entries2["Dept ID"].get(),   True),
            ("dept_name", entries2["Dept Name"].get(), False),
            ("location",  entries2["Location"].get(),  False),
            ("head_name", entries2["Head Name"].get(), False),
            ("budget",    entries2["Budget"].get(),    True),
        ]
        base = "SELECT * FROM departments"
        query, values = build_query(base, field_map)
        cursor.execute(query, values)
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            messagebox.showinfo("No Results", "No records found!")
        tree2.delete(*tree2.get_children())
        for row in rows:
            tree2.insert("", "end", values=row)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def update_dept():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""UPDATE departments SET dept_name=%s, location=%s,
                          head_name=%s, budget=%s WHERE dept_id=%s""",
                       (entries2["Dept Name"].get(), entries2["Location"].get(),
                        entries2["Head Name"].get(), entries2["Budget"].get(),
                        entries2["Dept ID"].get()))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Department updated!")
        view_dept()
        clear_dept()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def select_dept(event):
    try:
        selected = tree2.focus()
        values = tree2.item(selected, "values")
        clear_dept()
        keys = ["Dept ID", "Dept Name", "Location", "Head Name", "Budget"]
        for i, key in enumerate(keys):
            entries2[key].insert(0, values[i])
    except:
        pass

btn_frame2 = tk.Frame(tab2, bg="#f0f0f0")
btn_frame2.pack(pady=5)

for text, cmd in [("View", view_dept), ("Search", search_dept),
                  ("Update", update_dept), ("Reset", clear_dept)]:
    tk.Button(btn_frame2, text=text, command=cmd, width=10,
              font=("Arial", 10), relief="raised", bg="#e0e0e0").pack(side="left", padx=5)

tree_frame2 = tk.Frame(tab2)
tree_frame2.pack(fill="both", expand=True, padx=10, pady=5)

cols2 = ("Dept ID", "Dept Name", "Location", "Head Name", "Budget")
tree2 = ttk.Treeview(tree_frame2, columns=cols2, show="headings", height=10)
for col in cols2:
    tree2.heading(col, text=col)
    tree2.column(col, width=150, anchor="center")

scroll2 = ttk.Scrollbar(tree_frame2, orient="vertical", command=tree2.yview)
tree2.configure(yscrollcommand=scroll2.set)
scroll2.pack(side="right", fill="y")
tree2.pack(fill="both", expand=True)
tree2.bind("<ButtonRelease-1>", select_dept)

tk.Label(tab2,
         text="💡 Tip: Budget='>3000000' | Budget='<=2500000' | Dept ID=1",
         bg="#f0f0f0", fg="#555", font=("Arial", 9, "italic")).pack(pady=2)

# ═══════════════════════════════════════════════════════════════
# TAB 3 — SALARIES
# ═══════════════════════════════════════════════════════════════
tab3 = tk.Frame(notebook, bg="#f0f0f0")
notebook.add(tab3, text="  💰 Salaries  ")

fields3 = ["Salary ID", "Officer ID", "Basic Salary", "Deductions", "Net Salary"]
entries3 = {}

input_frame3 = tk.Frame(tab3, bg="#f0f0f0")
input_frame3.pack(pady=10, padx=10, anchor="w")

for i, field in enumerate(fields3):
    tk.Label(input_frame3, text=field, bg="#f0f0f0", width=12, anchor="w",
             font=("Arial", 10)).grid(row=i, column=0, pady=3, sticky="w")
    e = tk.Entry(input_frame3, width=25, font=("Arial", 10))
    e.grid(row=i, column=1, pady=3, padx=5)
    entries3[field] = e

def clear_salary():
    for e in entries3.values():
        e.delete(0, tk.END)

def view_salary():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM salaries")
        rows = cursor.fetchall()
        conn.close()
        tree3.delete(*tree3.get_children())
        for row in rows:
            tree3.insert("", "end", values=row)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def search_salary():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        field_map = [
            ("salary_id",    entries3["Salary ID"].get(),    True),
            ("officer_id",   entries3["Officer ID"].get(),   True),
            ("basic_salary", entries3["Basic Salary"].get(), True),
            ("deductions",   entries3["Deductions"].get(),   True),
            ("net_salary",   entries3["Net Salary"].get(),   True),
        ]
        base = "SELECT * FROM salaries"
        query, values = build_query(base, field_map)
        cursor.execute(query, values)
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            messagebox.showinfo("No Results", "No records found!")
        tree3.delete(*tree3.get_children())
        for row in rows:
            tree3.insert("", "end", values=row)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def update_salary():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""UPDATE salaries SET basic_salary=%s, deductions=%s,
                          net_salary=%s WHERE salary_id=%s""",
                       (entries3["Basic Salary"].get(), entries3["Deductions"].get(),
                        entries3["Net Salary"].get(), entries3["Salary ID"].get()))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Salary updated!")
        view_salary()
        clear_salary()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def select_salary(event):
    try:
        selected = tree3.focus()
        values = tree3.item(selected, "values")
        clear_salary()
        keys = ["Salary ID", "Officer ID", "Basic Salary", "Deductions", "Net Salary"]
        for i, key in enumerate(keys):
            entries3[key].insert(0, values[i])
    except:
        pass

btn_frame3 = tk.Frame(tab3, bg="#f0f0f0")
btn_frame3.pack(pady=5)

for text, cmd in [("View", view_salary), ("Search", search_salary),
                  ("Update", update_salary), ("Reset", clear_salary)]:
    tk.Button(btn_frame3, text=text, command=cmd, width=10,
              font=("Arial", 10), relief="raised", bg="#e0e0e0").pack(side="left", padx=5)

tree_frame3 = tk.Frame(tab3)
tree_frame3.pack(fill="both", expand=True, padx=10, pady=5)

cols3 = ("Salary ID", "Officer ID", "Basic Salary", "Deductions", "Net Salary")
tree3 = ttk.Treeview(tree_frame3, columns=cols3, show="headings", height=10)
for col in cols3:
    tree3.heading(col, text=col)
    tree3.column(col, width=150, anchor="center")

scroll3 = ttk.Scrollbar(tree_frame3, orient="vertical", command=tree3.yview)
tree3.configure(yscrollcommand=scroll3.set)
scroll3.pack(side="right", fill="y")
tree3.pack(fill="both", expand=True)
tree3.bind("<ButtonRelease-1>", select_salary)

tk.Label(tab3,
         text="💡 Tip: Basic Salary='>45000' | Deductions='<5000' | Net Salary='>=40000' | Officer ID=5",
         bg="#f0f0f0", fg="#555", font=("Arial", 9, "italic")).pack(pady=2)

# ═══════════════════════════════════════════════════════════════
# TAB 4 — FULL REPORT (All 3 Tables Joined)
# ═══════════════════════════════════════════════════════════════
tab4 = tk.Frame(notebook, bg="#f0f0f0")
notebook.add(tab4, text="  🔗 Full Report  ")

input_frame4 = tk.Frame(tab4, bg="#f0f0f0")
input_frame4.pack(pady=10, padx=10, anchor="w")

# Left column
left_fields  = [
    ("Officer ID",   "o.officer_id",   True),
    ("Name",         "o.name",         False),
    ("Designation",  "o.designation",  False),
    ("City",         "o.city",         False),
    ("Officer Salary","o.salary",      True),
]
# Right column
right_fields = [
    ("Department",   "d.dept_name",    False),
    ("Head Name",    "d.head_name",    False),
    ("Basic Salary", "s.basic_salary", True),
    ("Deductions",   "s.deductions",   True),
    ("Net Salary",   "s.net_salary",   True),
]

entries4      = {}
field_map4    = []

for i, (label, col, is_num) in enumerate(left_fields):
    tk.Label(input_frame4, text=label, bg="#f0f0f0", width=14, anchor="w",
             font=("Arial", 10)).grid(row=i, column=0, pady=3, sticky="w")
    e = tk.Entry(input_frame4, width=18, font=("Arial", 10))
    e.grid(row=i, column=1, pady=3, padx=5)
    entries4[label] = (e, col, is_num)

for i, (label, col, is_num) in enumerate(right_fields):
    tk.Label(input_frame4, text=label, bg="#f0f0f0", width=14, anchor="w",
             font=("Arial", 10)).grid(row=i, column=2, pady=3, sticky="w", padx=(15, 2))
    e = tk.Entry(input_frame4, width=18, font=("Arial", 10))
    e.grid(row=i, column=3, pady=3, padx=5)
    entries4[label] = (e, col, is_num)

def view_full():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""SELECT o.officer_id, o.name, o.designation, o.city, o.salary,
                                 d.dept_name, d.head_name,
                                 s.basic_salary, s.deductions, s.net_salary
                          FROM officers o
                          JOIN departments d ON o.dept_id = d.dept_id
                          JOIN salaries s ON o.officer_id = s.officer_id""")
        rows = cursor.fetchall()
        conn.close()
        tree4.delete(*tree4.get_children())
        for row in rows:
            tree4.insert("", "end", values=row)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def search_full():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        field_map = []
        for label, (e, col, is_num) in entries4.items():
            field_map.append((col, e.get(), is_num))

        base = """SELECT o.officer_id, o.name, o.designation, o.city, o.salary,
                         d.dept_name, d.head_name,
                         s.basic_salary, s.deductions, s.net_salary
                  FROM officers o
                  JOIN departments d ON o.dept_id = d.dept_id
                  JOIN salaries s ON o.officer_id = s.officer_id"""

        query, values = build_query(base, field_map)
        cursor.execute(query, values)
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            messagebox.showinfo("No Results", "No records found!")
        tree4.delete(*tree4.get_children())
        for row in rows:
            tree4.insert("", "end", values=row)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def clear_report():
    for label, (e, col, is_num) in entries4.items():
        e.delete(0, tk.END)

btn_frame4 = tk.Frame(tab4, bg="#f0f0f0")
btn_frame4.pack(pady=5)

for text, cmd in [("View All", view_full), ("Search", search_full),
                  ("Reset", lambda: [clear_report(), view_full()])]:
    tk.Button(btn_frame4, text=text, command=cmd, width=10,
              font=("Arial", 10), relief="raised", bg="#e0e0e0").pack(side="left", padx=5)

tree_frame4 = tk.Frame(tab4)
tree_frame4.pack(fill="both", expand=True, padx=10, pady=5)

cols4 = ("ID", "Name", "Designation", "City", "Officer Salary",
         "Department", "Head", "Basic Salary", "Deductions", "Net Salary")
tree4 = ttk.Treeview(tree_frame4, columns=cols4, show="headings", height=10)
for col in cols4:
    tree4.heading(col, text=col)
    tree4.column(col, width=110, anchor="center")

scroll4y = ttk.Scrollbar(tree_frame4, orient="vertical", command=tree4.yview)
scroll4x = ttk.Scrollbar(tree_frame4, orient="horizontal", command=tree4.xview)
tree4.configure(yscrollcommand=scroll4y.set, xscrollcommand=scroll4x.set)
scroll4y.pack(side="right", fill="y")
scroll4x.pack(side="bottom", fill="x")
tree4.pack(fill="both", expand=True)

tk.Label(tab4,
         text="💡 Tip: ANY field supports > < >= <= | Department=Police + Basic Salary='>50000' | Deductions='<5000'",
         bg="#f0f0f0", fg="#555", font=("Arial", 9, "italic")).pack(pady=2)

root.mainloop()