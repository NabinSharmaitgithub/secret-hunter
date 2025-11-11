import tkinter as tk
from tkinter import filedialog, messagebox
from secret_hunter.scanner import scan_directory
from secret_hunter.remediation import generate_report
from secret_hunter.fetcher import fetch_source
from secret_hunter.auth_check import confirm_authorization
from argparse import Namespace

class SecretHunterGUI:
    def __init__(self, master):
        self.master = master
        master.title("Secret Hunter")

        # Authorization Frame
        self.auth_frame = tk.Frame(master)
        self.auth_frame.pack(pady=10)
        self.auth_label = tk.Label(self.auth_frame, text="Type 'I AUTHORIZE' to enable scanning features:")
        self.auth_label.pack()
        self.auth_entry = tk.Entry(self.auth_frame, width=50)
        self.auth_entry.pack()
        self.auth_button = tk.Button(self.auth_frame, text="Confirm Authorization", command=self.check_authorization)
        self.auth_button.pack()
        
        # Main controls frame (initially disabled)
        self.controls_frame = tk.Frame(master)
        self.controls_frame.pack(pady=10)

        self.target_label = tk.Label(self.controls_frame, text="Target Path:")
        self.target_label.pack()
        self.target_entry = tk.Entry(self.controls_frame, width=50, state=tk.DISABLED)
        self.target_entry.pack()
        self.browse_button = tk.Button(self.controls_frame, text="Browse", command=self.browse_target, state=tk.DISABLED)
        self.browse_button.pack()
        self.scan_button = tk.Button(self.controls_frame, text="Scan", command=self.scan, state=tk.DISABLED)
        self.scan_button.pack()

        self.source_url_label = tk.Label(self.controls_frame, text="Source URL:")
        self.source_url_label.pack()
        self.source_url_entry = tk.Entry(self.controls_frame, width=50, state=tk.DISABLED)
        self.source_url_entry.pack()
        self.fetch_scan_button = tk.Button(self.controls_frame, text="Fetch & Scan", command=self.fetch_and_scan, state=tk.DISABLED)
        self.fetch_scan_button.pack()

    def check_authorization(self):
        if self.auth_entry.get().strip() == "I AUTHORIZE":
            messagebox.showinfo("Authorized", "Authorization confirmed. You may now proceed.")
            self.enable_controls()
        else:
            messagebox.showerror("Authorization Failed", "You must type 'I AUTHORIZE' to proceed.")

    def enable_controls(self):
        self.target_entry.config(state=tk.NORMAL)
        self.browse_button.config(state=tk.NORMAL)
        self.scan_button.config(state=tk.NORMAL)
        self.source_url_entry.config(state=tk.NORMAL)
        self.fetch_scan_button.config(state=tk.NORMAL)
        # Disable the authorization section
        self.auth_entry.config(state=tk.DISABLED)
        self.auth_button.config(state=tk.DISABLED)

    def browse_target(self):
        target_path = filedialog.askdirectory()
        self.target_entry.delete(0, tk.END)
        self.target_entry.insert(0, target_path)

    def scan(self):
        target_path = self.target_entry.get()
        if not target_path:
            messagebox.showerror("Error", "Please select a target path.")
            return

        args = Namespace(target=target_path, rules="rules.yml", whitelist=None, no_decompile=False, max_depth=10, output="report.json")
        findings = scan_directory(args.target, args.rules, args.whitelist, args.no_decompile, args.max_depth)
        generate_report(findings, args.output)
        messagebox.showinfo("Success", f"Scan complete. Report saved to {args.output}")

    def fetch_and_scan(self):
        source_url = self.source_url_entry.get()
        if not source_url:
            messagebox.showerror("Error", "Please enter a source URL.")
            return

        # Explicitly show the authorization and license prompt for fetch operations
        if not messagebox.askokcancel("Confirm License Check", "The tool will now fetch the source and may prompt you in the console to confirm the license. Please check your terminal."):
            return

        args = Namespace(source_url=source_url, source_type="auto", branch=None, tag=None, cache_dir=".cache", max_download_size=100, timeout=60, verify_license=True, rules="rules.yml", whitelist=None, no_decompile=False, max_depth=10, output="report.json")
        try:
            target_path = fetch_source(args)
            if target_path:
                findings = scan_directory(target_path, args.rules, args.whitelist, args.no_decompile, args.max_depth)
                generate_report(findings, args.output)
                messagebox.showinfo("Success", f"Scan complete. Report saved to {args.output}")
            else:
                messagebox.showerror("Error", "Failed to fetch source. Check the console for details.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

def main():
    root = tk.Tk()
    gui = SecretHunterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
