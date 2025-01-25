import tkinter as tk
from tkinter import messagebox
import db
import variables as v
from hashlib import sha256


def register_window():
    def register():
        login = str(login_entry.get())
        nickname = str(nickname_entry.get())
        password = str(sha256(password_entry.get().encode("utf-8")).hexdigest())
        password_repeat = str(
            sha256(password_repeat_entry.get().encode("utf-8")).hexdigest()
        )
        print(password)
        print(password_repeat)
        if not login or not nickname or not password or not password_repeat:
            messagebox.showerror("Error", "All fields are required!")
            return

        if password != password_repeat:
            messagebox.showerror("Error", "Passwords do not match!")
            return

        res = db.db.reg(login, password, nickname)
        if res:
            v.nickname = nickname
            v.password = password
            v.username = login
            v.update_auth_data()
            v.update_user_data()
            messagebox.showinfo(
                "Success", f"User '{nickname}' registered successfully!"
            )
            v.AUTHED = True
        else:
            messagebox.showerror("Error", "Something went wrong :(")

        reg_window.destroy()

    reg_window = tk.Tk()
    reg_window.title("Register")
    reg_window.geometry("400x400")

    # Метки и поля ввода
    tk.Label(reg_window, text="Login:").pack(pady=5)
    login_entry = tk.Entry(reg_window, width=30)
    login_entry.pack(pady=5)

    tk.Label(reg_window, text="Nickname:").pack(pady=5)
    nickname_entry = tk.Entry(reg_window, width=30)
    nickname_entry.pack(pady=5)

    tk.Label(reg_window, text="Password:").pack(pady=5)
    password_entry = tk.Entry(reg_window, show="*", width=30)
    password_entry.pack(pady=5)

    tk.Label(reg_window, text="Repeat Password:").pack(pady=5)
    password_repeat_entry = tk.Entry(reg_window, show="*", width=30)
    password_repeat_entry.pack(pady=5)

    register_button = tk.Button(reg_window, text="Register", command=register)
    register_button.pack(pady=20)

    reg_window.mainloop()


# Окно входа
def login_window():
    def login():
        login = str(login_entry.get())
        password = str(sha256(password_entry.get().encode("utf-8")).hexdigest())

        if not login or not password:
            messagebox.showerror("Error", "All fields are required!")
            return
        if db.db.auth(login, password):
            nickname = db.db.get_nickname(login)
            if nickname:
                v.nickname = nickname
            else:
                v.nickname = "Player"
            v.username = login
            v.password = password
            v.update_auth_data()
            v.AUTHED = True
            v.update_user_data()
            messagebox.showinfo("Success", "Login successful!")
            v.AUTHED = True
            login_window.destroy()
        else:
            messagebox.showerror("Error", "Invalid login or password!")

    login_window = tk.Tk()
    login_window.title("Login")
    login_window.geometry("400x300")

    # Метки и поля ввода
    tk.Label(login_window, text="Login:").pack(pady=5)
    login_entry = tk.Entry(login_window, width=30)
    login_entry.pack(pady=5)

    tk.Label(login_window, text="Password:").pack(pady=5)
    password_entry = tk.Entry(login_window, show="*", width=30)
    password_entry.pack(pady=5)

    login_button = tk.Button(login_window, text="Login", command=login)
    login_button.pack(pady=20)

    login_window.mainloop()
