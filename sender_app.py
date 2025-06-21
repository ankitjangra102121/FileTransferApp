import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import os

class SenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Share Sender (Windows)")
        self.root.geometry("500x300")

        self.folder_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Idle")
        self.tunnel_url = ""

        tk.Label(root, text="Select Folder to Share:").pack(pady=5)
        tk.Entry(root, textvariable=self.folder_var, width=50).pack(pady=5)
        tk.Button(root, text="Browse", command=self.browse_folder).pack(pady=5)

        tk.Button(root, text="Start Sharing", command=self.start_sharing).pack(pady=10)
        tk.Label(root, textvariable=self.status_var, fg="blue").pack(pady=5)

        self.url_box = tk.Text(root, height=2, width=60)
        self.url_box.pack(pady=5)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)

    def start_sharing(self):
        folder = self.folder_var.get()
        if not os.path.isdir(folder):
            messagebox.showerror("Error", "Invalid folder path")
            return

        threading.Thread(target=self.start_server_and_tunnel, args=(folder,), daemon=True).start()
        self.status_var.set("Starting server and tunnel...")

    def start_server_and_tunnel(self, folder):
        os.chdir(folder)
        http_proc = subprocess.Popen(["python", "-m", "http.server", "8000"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        try:
            tunnel_proc = subprocess.Popen(["cloudflared.exe", "tunnel", "--url", "http://localhost:8000"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for line in tunnel_proc.stdout:
                if "trycloudflare.com" in line:
                    self.tunnel_url = line.strip()
                    self.url_box.delete("1.0", tk.END)
                    self.url_box.insert(tk.END, self.tunnel_url)
                    self.status_var.set("Sharing Active!")
                    break
            tunnel_proc.wait()
        finally:
            http_proc.terminate()

if __name__ == "__main__":
    root = tk.Tk()
    app = SenderApp(root)
    root.mainloop()
