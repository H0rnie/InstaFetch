import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
import instaloader
import pandas as pd
import time

class InstaFetchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Fetch Tool")
        self.create_widgets()

    def create_widgets(self):
        self.label_username = ttk.Label(self.root, text="Instagram Username:")
        self.label_username.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        self.entry_username = ttk.Entry(self.root)
        self.entry_username.grid(row=0, column=1, padx=10, pady=10)

        self.label_password = ttk.Label(self.root, text="Instagram Password:")
        self.label_password.grid(row=1, column=0, padx=10, pady=10, sticky="e")

        self.entry_password = ttk.Entry(self.root, show="*")
        self.entry_password.grid(row=1, column=1, padx=10, pady=10)

        self.fetch_button = ttk.Button(self.root, text="Fetch Followers", command=self.fetch_followers)
        self.fetch_button.grid(row=2, column=0, columnspan=2, pady=20)

        self.style = ttk.Style()
        self.style.configure("TProgressbar",
                             thickness=30,
                             troughcolor="#d9d9d9",
                             bordercolor="#4e4e4e",
                             lightcolor="#4e4e4e",
                             darkcolor="#4e4e4e",
                             troughrelief="flat")

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100, style="TProgressbar")
        self.progress_bar.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")

    def fetch_followers(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        self.fetch_and_save_followers(username, password)

    def fetch_and_save_followers(self, username, password):
        loader = instaloader.Instaloader()

        try:
            loader.context.login(username, password)
        except instaloader.exceptions.TwoFactorAuthRequiredException as e:
            two_factor_code = self.prompt_for_two_factor_code()
            if not two_factor_code:
                messagebox.showerror("Error", "Two-factor authentication code not provided. Aborting.")
                return
            loader.context.two_factor_login(two_factor_code)
        except instaloader.exceptions.InvalidArgumentException as e:
            messagebox.showerror("Error", "Invalid username or password. Please check your credentials and try again.")
            return

        profile = instaloader.Profile.from_username(loader.context, username)

        try:
            self.show_progress_bar()
            followers = [follower.username for follower in profile.get_followers()]
        except instaloader.exceptions.ConnectionException as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")
            return
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            return
        finally:
            self.hide_progress_bar()
            loader.close()

        followers_df = pd.DataFrame({"Followers": followers})
        file_name = f"{username}_{time.strftime('%Y%m%d_%H%M%S')}.xlsx"
        followers_df.to_excel(file_name, index=False)
        messagebox.showinfo("Info", f"Followers list saved to {file_name}")

    def prompt_for_two_factor_code(self):
        return simpledialog.askstring("Two-Factor Authentication", "Enter the two-factor authentication code:")

    def show_progress_bar(self):
        self.progress_bar.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")

    def hide_progress_bar(self):
        self.progress_bar.grid_forget()

root = tk.Tk()
app = InstaFetchGUI(root)
root.mainloop()
