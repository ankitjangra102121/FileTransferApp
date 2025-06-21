import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import requests
import os
import time

class ReceiverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Receiver")
        self.root.geometry("500x300")

        self.url_var = tk.StringVar()
        self.folder_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Idle")

        tk.Label(root, text="Sender URL (e.g., https://xxxx.trycloudflare.com):").pack(pady=5)
        tk.Entry(root, textvariable=self.url_var, width=50).pack(pady=5)

        tk.Label(root, text="Destination Folder:").pack(pady=5)
        tk.Entry(root, textvariable=self.folder_var, width=50).pack(pady=5)
        tk.Button(root, text="Browse", command=self.browse_folder).pack(pady=5)

        tk.Button(root, text="Start Downloading", command=self.start_downloading).pack(pady=10)
        tk.Label(root, textvariable=self.status_var, fg="blue").pack(pady=5)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)

    def start_downloading(self):
        url = self.url_var.get().strip()
        folder = self.folder_var.get().strip()

        if not url or not folder:
            messagebox.showerror("Error", "Please provide both URL and folder")
            return

        threading.Thread(target=self.download_loop, args=(url, folder), daemon=True).start()
        self.status_var.set("Downloading started (checks every 30 mins)...")

    def download_loop(self, url, folder):
        while True:
            try:
                page = requests.get(url).text
                filenames = [line.split('href=\"')[1].split('\"')[0] for line in page.splitlines() if 'href=\"' in line and line.endswith('</a>')]
                for filename in filenames:
                    if filename == "../":
                        continue
                    file_url = url + "/" + filename
                    local_file = os.path.join(folder, filename)
                    if not os.path.exists(local_file):
                        with open(local_file, "wb") as f:
                            f.write(requests.get(file_url).content)
                self.status_var.set("Checked and downloaded new files.")
            except Exception as e:
                self.status_var.set(f"Error: {e}")

            time.sleep(1800)  # 30 minutes

if __name__ == "__main__":
    root = tk.Tk()
    app = ReceiverApp(root)
    root.mainloop()
