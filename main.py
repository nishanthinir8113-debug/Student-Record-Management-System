import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DB_NAME = "students.db"


class StudentRecordApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Record Management System")
        self.root.geometry("1000x620")
        self.root.minsize(850, 540)
        self.root.configure(bg="#f3f6fb")

        self.connection = sqlite3.connect(DB_NAME)
        self.create_table()

        title = tk.Label(
            root, text="STUDENT RECORD MANAGEMENT SYSTEM",
            font=("Arial", 19, "bold"), bg="#17365d", fg="white", pady=16
        )
        title.pack(fill="x")

        form = tk.LabelFrame(
            root, text="Student Details", font=("Arial", 11, "bold"),
            bg="#f3f6fb", padx=14, pady=12
        )
        form.pack(fill="x", padx=18, pady=(16, 8))

        self.student_id = tk.StringVar()
        self.name = tk.StringVar()
        self.department = tk.StringVar()
        self.year = tk.StringVar()
        self.email = tk.StringVar()

        fields = [
            ("Student ID", self.student_id, 0, 0),
            ("Full Name", self.name, 0, 2),
            ("Department", self.department, 1, 0),
            ("Year", self.year, 1, 2),
            ("Email", self.email, 2, 0),
        ]

        for label_text, variable, row, col in fields:
            tk.Label(form, text=label_text, bg="#f3f6fb", font=("Arial", 10)).grid(
                row=row, column=col, sticky="w", padx=(4, 8), pady=7
            )
            entry = ttk.Entry(form, textvariable=variable, width=30)
            entry.grid(row=row, column=col + 1, sticky="ew", padx=(0, 18), pady=7)

        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        buttons = tk.Frame(root, bg="#f3f6fb")
        buttons.pack(fill="x", padx=18, pady=7)

        ttk.Button(buttons, text="Add Student", command=self.add_student).pack(side="left", padx=5)
        ttk.Button(buttons, text="Update Selected", command=self.update_student).pack(side="left", padx=5)
        ttk.Button(buttons, text="Delete Selected", command=self.delete_student).pack(side="left", padx=5)
        ttk.Button(buttons, text="Clear Fields", command=self.clear_fields).pack(side="left", padx=5)

        search_frame = tk.Frame(root, bg="#f3f6fb")
        search_frame.pack(fill="x", padx=22, pady=(8, 5))
        tk.Label(search_frame, text="Search by ID or name:", bg="#f3f6fb",
                 font=("Arial", 10)).pack(side="left", padx=(0, 8))
        self.search_text = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_text, width=32)
        search_entry.pack(side="left", padx=(0, 8))
        ttk.Button(search_frame, text="Search", command=self.search_students).pack(side="left", padx=4)
        ttk.Button(search_frame, text="Show All", command=self.load_students).pack(side="left", padx=4)

        table_frame = tk.Frame(root, bg="#f3f6fb")
        table_frame.pack(fill="both", expand=True, padx=18, pady=(5, 14))

        columns = ("student_id", "name", "department", "year", "email")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        headings = {
            "student_id": "Student ID",
            "name": "Full Name",
            "department": "Department",
            "year": "Year",
            "email": "Email",
        }
        widths = {"student_id": 100, "name": 200, "department": 160, "year": 70, "email": 250}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.select_record)

        self.status = tk.Label(root, text="Ready", anchor="w", bg="#dce6f1",
                               fg="#17365d", padx=12, pady=5)
        self.status.pack(fill="x", side="bottom")

        self.load_students()

    def create_table(self):
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                year TEXT NOT NULL,
                email TEXT NOT NULL
            )
        """)
        self.connection.commit()

    def add_student(self):
        values = (
            self.student_id.get().strip(),
            self.name.get().strip(),
            self.department.get().strip(),
            self.year.get().strip(),
            self.email.get().strip(),
        )
        if not all(values):
            messagebox.showwarning("Missing Details", "Please fill in all fields.")
            return
        try:
            self.connection.execute(
                "INSERT INTO students VALUES (?, ?, ?, ?, ?)", values
            )
            self.connection.commit()
            self.load_students()
            self.clear_fields()
            self.status.config(text="Student record added successfully.")
            messagebox.showinfo("Success", "Student record added successfully.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate ID", "This Student ID already exists.")

    def load_students(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = self.connection.execute(
            "SELECT student_id, name, department, year, email FROM students ORDER BY student_id"
        ).fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)
        self.status.config(text=f"Total student records: {len(rows)}")

    def select_record(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        for variable, value in zip(
            (self.student_id, self.name, self.department, self.year, self.email), values
        ):
            variable.set(value)

    def update_student(self):
        values = (
            self.name.get().strip(),
            self.department.get().strip(),
            self.year.get().strip(),
            self.email.get().strip(),
            self.student_id.get().strip(),
        )
        if not all(values):
            messagebox.showwarning("Missing Details", "Select a record and fill in all fields.")
            return
        cursor = self.connection.execute(
            "UPDATE students SET name=?, department=?, year=?, email=? WHERE student_id=?",
            values
        )
        self.connection.commit()
        if cursor.rowcount == 0:
            messagebox.showwarning("Not Found", "No record found with this Student ID.")
        else:
            self.load_students()
            self.status.config(text="Student record updated successfully.")
            messagebox.showinfo("Success", "Student record updated successfully.")

    def delete_student(self):
        student_id = self.student_id.get().strip()
        if not student_id:
            messagebox.showwarning("Select Record", "Select a record to delete.")
            return
        confirm = messagebox.askyesno("Confirm Delete", f"Delete student ID {student_id}?")
        if confirm:
            cursor = self.connection.execute(
                "DELETE FROM students WHERE student_id=?", (student_id,)
            )
            self.connection.commit()
            self.load_students()
            self.clear_fields()
            if cursor.rowcount:
                self.status.config(text="Student record deleted.")
            else:
                messagebox.showwarning("Not Found", "No record found with this Student ID.")

    def search_students(self):
        term = self.search_text.get().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = self.connection.execute(
            """SELECT student_id, name, department, year, email FROM students
               WHERE student_id LIKE ? OR name LIKE ? ORDER BY student_id""",
            (f"%{term}%", f"%{term}%")
        ).fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)
        self.status.config(text=f"Search results: {len(rows)}")

    def clear_fields(self):
        for variable in (self.student_id, self.name, self.department, self.year, self.email):
            variable.set("")
        self.tree.selection_remove(self.tree.selection())

    def close(self):
        self.connection.close()
        self.root.destroy()


if __name__ == "__main__":
    window = tk.Tk()
    app = StudentRecordApp(window)
    window.protocol("WM_DELETE_WINDOW", app.close)
    window.mainloop()
