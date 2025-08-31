import tkinter as tk
from tkinter import messagebox
import sqlite3

# ---------- Database Setup ----------
conn = sqlite3.connect("flights.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS flights(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flight_no TEXT,
    origin TEXT,
    destination TEXT,
    seats INTEGER
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS bookings(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    flight_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(flight_id) REFERENCES flights(id)
)
""")
conn.commit()


# ---------- Functions ----------
def register_user():
    username = entry_username.get()
    password = entry_password.get()
    if username and password:
        try:
            cur.execute("INSERT INTO users(username,password) VALUES(?,?)", (username,password))
            conn.commit()
            messagebox.showinfo("Success","User registered successfully!")
        except:
            messagebox.showerror("Error","Username already exists.")
    else:
        messagebox.showerror("Error","All fields required")

def login_user():
    username = entry_username.get()
    password = entry_password.get()
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password))
    user = cur.fetchone()
    if user:
        messagebox.showinfo("Welcome", f"Welcome {username}")
        login_win.destroy()
        main_menu(user[0])   # pass user_id
    else:
        messagebox.showerror("Error","Invalid login")

def add_flight():
    fno = entry_fno.get()
    origin = entry_origin.get()
    dest = entry_dest.get()
    seats = entry_seats.get()
    if fno and origin and dest and seats.isdigit():
        cur.execute("INSERT INTO flights(flight_no,origin,destination,seats) VALUES(?,?,?,?)",
                    (fno, origin, dest, int(seats)))
        conn.commit()
        messagebox.showinfo("Success","Flight added successfully")
    else:
        messagebox.showerror("Error","Please enter valid data")

def search_flights(user_id):
    win = tk.Toplevel(root)
    win.title("Available Flights")
    win.config(bg="#f0f8ff")

    tk.Label(win,text="Origin", bg="#f0f8ff", font=("Arial",12,"bold")).grid(row=0,column=0,padx=5,pady=5)
    tk.Label(win,text="Destination", bg="#f0f8ff", font=("Arial",12,"bold")).grid(row=0,column=1,padx=5,pady=5)
    ent_o = tk.Entry(win,font=("Arial",12))
    ent_d = tk.Entry(win,font=("Arial",12))
    ent_o.grid(row=0,column=2,padx=5)
    ent_d.grid(row=0,column=3,padx=5)
    
    frame = tk.Frame(win,bg="#f0f8ff")
    frame.grid(row=2,column=0,columnspan=5,pady=10)

    def do_search():
        for widget in frame.winfo_children():
            widget.destroy()
        o = ent_o.get()
        d = ent_d.get()
        cur.execute("SELECT * FROM flights WHERE origin=? AND destination=?", (o,d))
        results = cur.fetchall()
        r = 0
        for flight in results:
            tk.Label(frame,text=f"{flight[1]}: {flight[2]} -> {flight[3]} | Seats: {flight[4]}",
                     font=("Arial",11),bg="#f0f8ff").grid(row=r,column=0,padx=5,pady=5)
            tk.Button(frame,text="Book",font=("Arial",10,"bold"),bg="#4682b4",fg="white",
                      command=lambda f=flight: book_flight(user_id,f[0])).grid(row=r,column=1,padx=5)
            r += 1

    tk.Button(win,text="Search",font=("Arial",11,"bold"),bg="#4682b4",fg="white",
              command=do_search).grid(row=0,column=4,padx=10)


def book_flight(user_id, flight_id):
    cur.execute("SELECT seats FROM flights WHERE id=?", (flight_id,))
    seats = cur.fetchone()[0]
    if seats > 0:
        cur.execute("INSERT INTO bookings(user_id, flight_id) VALUES(?,?)",(user_id,flight_id))
        cur.execute("UPDATE flights SET seats=seats-1 WHERE id=?",(flight_id,))
        conn.commit()
        messagebox.showinfo("Success","Flight booked successfully!")
    else:
        messagebox.showerror("Error","No seats available")

def view_bookings(user_id):
    win = tk.Toplevel(root)
    win.title("My Bookings")
    win.config(bg="#f0f8ff")

    cur.execute("""
        SELECT flights.flight_no, flights.origin, flights.destination 
        FROM bookings
        JOIN flights ON bookings.flight_id = flights.id
        WHERE bookings.user_id=?
    """, (user_id,))
    results = cur.fetchall()
    for i, b in enumerate(results):
        tk.Label(win,text=f"{b[0]}: {b[1]} -> {b[2]}",font=("Arial",12),bg="#f0f8ff").grid(row=i,column=0,padx=5,pady=5)

def main_menu(user_id):
    win = tk.Toplevel(root)
    win.title("Main Menu")
    win.config(bg="#f0f8ff", padx=30, pady=30)

    tk.Label(win,text="✈ Flight Reservation System",font=("Arial",16,"bold"),bg="#f0f8ff",fg="#2f4f4f").pack(pady=15)
    tk.Button(win,text="➕ Add Flight (Admin)",command=flight_window,
              font=("Arial",12,"bold"),bg="#4682b4",fg="white",width=20).pack(pady=8)
    tk.Button(win,text="🔎 Search Flights",command=lambda: search_flights(user_id),
              font=("Arial",12,"bold"),bg="#4682b4",fg="white",width=20).pack(pady=8)
    tk.Button(win,text="📋 View My Bookings",command=lambda: view_bookings(user_id),
              font=("Arial",12,"bold"),bg="#4682b4",fg="white",width=20).pack(pady=8)

def flight_window():
    win = tk.Toplevel(root)
    win.title("Add Flight")
    win.config(bg="#f0f8ff", padx=20, pady=20)

    global entry_fno, entry_origin, entry_dest, entry_seats
    tk.Label(win,text="Flight No",font=("Arial",12),bg="#f0f8ff").grid(row=0,column=0,padx=5,pady=5,sticky="w")
    tk.Label(win,text="Origin",font=("Arial",12),bg="#f0f8ff").grid(row=1,column=0,padx=5,pady=5,sticky="w")
    tk.Label(win,text="Destination",font=("Arial",12),bg="#f0f8ff").grid(row=2,column=0,padx=5,pady=5,sticky="w")
    tk.Label(win,text="Seats",font=("Arial",12),bg="#f0f8ff").grid(row=3,column=0,padx=5,pady=5,sticky="w")

    entry_fno = tk.Entry(win,font=("Arial",12)); entry_origin = tk.Entry(win,font=("Arial",12))
    entry_dest = tk.Entry(win,font=("Arial",12)); entry_seats = tk.Entry(win,font=("Arial",12))
    entry_fno.grid(row=0,column=1,pady=5); entry_origin.grid(row=1,column=1,pady=5)
    entry_dest.grid(row=2,column=1,pady=5); entry_seats.grid(row=3,column=1,pady=5)

    tk.Button(win,text="Add Flight",command=add_flight,
              font=("Arial",12,"bold"),bg="#4682b4",fg="white").grid(row=4,column=0,columnspan=2,pady=10)


# ---------- Splash then Login ----------
def show_login():
    global login_win, entry_username, entry_password
    splash.destroy()
    login_win = tk.Toplevel(root)
    login_win.title("Login")
    login_win.config(bg="#f0f8ff", padx=30, pady=30)

    tk.Label(login_win,text="✈ Flight Reservation System",font=("Arial",16,"bold"),bg="#f0f8ff",fg="#2f4f4f").grid(row=0,column=0,columnspan=2,pady=10)

    tk.Label(login_win,text="Username",font=("Arial",12),bg="#f0f8ff").grid(row=1,column=0,padx=5,pady=5,sticky="w")
    tk.Label(login_win,text="Password",font=("Arial",12),bg="#f0f8ff").grid(row=2,column=0,padx=5,pady=5,sticky="w")

    entry_username = tk.Entry(login_win,font=("Arial",12))
    entry_password = tk.Entry(login_win, show="*",font=("Arial",12))
    entry_username.grid(row=1,column=1,pady=5)
    entry_password.grid(row=2,column=1,pady=5)

    tk.Button(login_win,text="Register",command=register_user,font=("Arial",12,"bold"),bg="#4682b4",fg="white",width=10).grid(row=3,column=0,pady=10)
    tk.Button(login_win,text="Login",command=login_user,font=("Arial",12,"bold"),bg="#2e8b57",fg="white",width=10).grid(row=3,column=1,pady=10)


root = tk.Tk()
root.withdraw()  # hide root until splash/login

splash = tk.Toplevel()
splash.title("Welcome")
splash.config(bg="#4682b4", padx=50, pady=40)
tk.Label(splash,text="✈ Flight Reservation System",font=("Arial",18,"bold"),bg="#4682b4",fg="white").pack(pady=20)
tk.Label(splash,text="Developed with Tkinter & SQLite",font=("Arial",12),bg="#4682b4",fg="white").pack(pady=10)

splash.after(2500, show_login)  # show login after 2.5 seconds

root.mainloop()
