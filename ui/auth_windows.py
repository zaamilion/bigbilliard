import tkinter as tk
from tkinter import ttk, messagebox
import network.db as db
import game.variables as v
from hashlib import sha256

# Конфигурация стилей
DARK_BG = "#2d2d2d"
MEDIUM_BG = "#373737"
LIGHT_BG = "#404040"
TEXT_COLOR = "#ffffff"
ACCENT_COLOR = "#4a9cff"
ENTRY_BG = "#333333"
FONT_NAME = "Segoe UI"


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
    reg_window.geometry("400x500")
    reg_window.configure(bg=DARK_BG)
    reg_window.resizable(False, False)

    # Заголовок
    header = tk.Frame(reg_window, bg=DARK_BG)
    header.pack(pady=20)
    tk.Label(
        header,
        text="Create Account",
        font=(FONT_NAME, 16, "bold"),
        bg=DARK_BG,
        fg=TEXT_COLOR,
    ).pack()

    # Основная форма
    form_frame = tk.Frame(reg_window, bg=DARK_BG)
    form_frame.pack(padx=40, pady=20)

    def create_entry(parent, label):
        frame = tk.Frame(parent, bg=DARK_BG)
        tk.Label(
            frame, text=label, font=(FONT_NAME, 10), bg=DARK_BG, fg=TEXT_COLOR
        ).pack(anchor="w")
        entry = tk.Entry(
            frame,
            width=25,
            bg=ENTRY_BG,
            fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
            relief="flat",
            font=(FONT_NAME, 10),
        )
        entry.pack(pady=(0, 15))
        return frame, entry

    # Поля ввода
    login_frame, login_entry = create_entry(form_frame, "Login")
    login_frame.pack(fill="x")

    nickname_frame, nickname_entry = create_entry(form_frame, "Nickname")
    nickname_frame.pack(fill="x")

    password_frame, password_entry = create_entry(form_frame, "Password")
    password_entry.configure(show="*")
    password_frame.pack(fill="x")

    password_repeat_frame, password_repeat_entry = create_entry(
        form_frame, "Repeat Password"
    )
    password_repeat_entry.configure(show="*")
    password_repeat_frame.pack(fill="x")

    # Стильная кнопка
    register_btn = tk.Button(
        form_frame,
        text="Register",
        command=register,
        bg=ACCENT_COLOR,
        fg=TEXT_COLOR,
        font=(FONT_NAME, 10, "bold"),
        activebackground=ACCENT_COLOR,
        activeforeground=TEXT_COLOR,
        relief="flat",
        padx=20,
        pady=8,
        borderwidth=0,
        cursor="hand2",
    )
    register_btn.pack(pady=15)

    # Эффекты при наведении
    register_btn.bind("<Enter>", lambda e: register_btn.configure(bg="#6ab0ff"))
    register_btn.bind("<Leave>", lambda e: register_btn.configure(bg=ACCENT_COLOR))

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
    login_window.geometry("400x400")
    login_window.configure(bg=DARK_BG)
    login_window.resizable(False, False)

    # Заголовок
    header = tk.Frame(login_window, bg=DARK_BG)
    header.pack(pady=30)
    tk.Label(
        header,
        text="Welcome Back",
        font=(FONT_NAME, 16, "bold"),
        bg=DARK_BG,
        fg=TEXT_COLOR,
    ).pack()

    # Основная форма
    form_frame = tk.Frame(login_window, bg=DARK_BG)
    form_frame.pack(padx=40, pady=20)

    def create_entry(parent, label):
        frame = tk.Frame(parent, bg=DARK_BG)
        tk.Label(
            frame, text=label, font=(FONT_NAME, 10), bg=DARK_BG, fg=TEXT_COLOR
        ).pack(anchor="w")
        entry = tk.Entry(
            frame,
            width=25,
            bg=ENTRY_BG,
            fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
            relief="flat",
            font=(FONT_NAME, 10),
        )
        entry.pack(pady=(0, 15))
        return frame, entry

    # Поля ввода
    login_frame, login_entry = create_entry(form_frame, "Login")
    login_frame.pack(fill="x")

    password_frame, password_entry = create_entry(form_frame, "Password")
    password_entry.configure(show="*")
    password_frame.pack(fill="x")

    # Стильная кнопка
    login_btn = tk.Button(
        form_frame,
        text="Login",
        command=login,
        bg=ACCENT_COLOR,
        fg=TEXT_COLOR,
        font=(FONT_NAME, 10, "bold"),
        activebackground=ACCENT_COLOR,
        activeforeground=TEXT_COLOR,
        relief="flat",
        padx=20,
        pady=8,
        borderwidth=0,
        cursor="hand2",
    )
    login_btn.pack(pady=15)

    # Эффекты при наведении
    login_btn.bind("<Enter>", lambda e: login_btn.configure(bg="#6ab0ff"))
    login_btn.bind("<Leave>", lambda e: login_btn.configure(bg=ACCENT_COLOR))

    login_window.mainloop()
