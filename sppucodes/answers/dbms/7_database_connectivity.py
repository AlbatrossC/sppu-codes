'''
Run this in mysql workbench:

CREATE DATABASE school;

USE school;

CREATE TABLE students (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    age INT
);

INSERT INTO students (id, name, age)
VALUES (1, 'Alice', 20),
       (2, 'Bob', 22); 
'''

# AND THEN RUN THIS PYTHON FILE

import tkinter as tk
from tkinter import messagebox
import mysql.connector

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="school"
    )

def add_student():
    con = connect_db()
    cur = con.cursor()
    cur.execute("INSERT INTO students VALUES(%s, %s, %s)",
                (id_entry.get(), name_entry.get(), age_entry.get()))
    con.commit()
    messagebox.showinfo("Added", "Student Added!")
    con.close()
    
def update_student():
    con = connect_db()
    cur = con.cursor()
    cur.execute("UPDATE students SET name=%s, age=%s WHERE id=%s",
                (name_entry.get(), age_entry.get(), id_entry.get()))
    con.commit()
    messagebox.showinfo("Updated", "Student Updated!")
    con.close()

def delete_student():
    con = connect_db()
    cur = con.cursor()
    cur.execute("DELETE FROM students WHERE id=%s", (id_entry.get(),))
    con.commit()
    messagebox.showinfo("Deleted", "Student Deleted!")
    con.close()

def view_students():
    con = connect_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM students")
    rows = cur.fetchall()
    con.close()

    output_box.delete(1.0, tk.END)
    output = "ID\tName\tAge\n-----------------------------\n"
    for r in rows:
        output += str(r[0]) + "\t" + str(r[1]) + "\t" + str(r[2]) + "\n"

    output_box.insert(tk.END, output)


root = tk.Tk()
root.title("Student DB")

tk.Label(root, text='ID').pack()
id_entry = tk.Entry(root)
id_entry.pack()

tk.Label(root, text="Name").pack()
name_entry = tk.Entry(root)
name_entry.pack()

tk.Label(root, text="Age").pack()
age_entry = tk.Entry(root)
age_entry.pack()

tk.Button(root, text="Add", command=add_student).pack()
tk.Button(root, text="Update", command=update_student).pack()
tk.Button(root, text="Delete", command=delete_student).pack()
tk.Button(root, text="View", command=view_students).pack()

output_box = tk.Text(root, height=8, width=30)
output_box.pack()

root.mainloop()