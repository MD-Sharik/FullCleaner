from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from ttkbootstrap import Style
from ttkbootstrap.widgets import Checkbutton
import threading
import time

# Import your cleanup modules
import TempCleaning as tc
import Temp32Cleaning as tc32
import Recycle as rc
import Browser as bs

class MainScreen(Tk):
    def __init__(self):
        super().__init__()
        self.title("FullCleaner by MDSHARIK")
        self.geometry("1024x768")
        self.configure(bg="#2b2b2b")
        self.resizable(False, False)

        style = Style(theme="darkly")  # Ensure 'darkly' theme is available

        self.selected_scan = StringVar(value="")
        self.scan_running = False

        

        # Load and place images
        Label(self, text="Select Scan Type", font=("Segoe UI", 10),
              foreground="gray", background="#2b2b2b").place(x=100, y=10)
        self.full_img = PhotoImage(file="full.png").subsample(2, 2)
        self.custom_img = PhotoImage(file="custom.png").subsample(2, 2)

        img_frame = Frame(self, bg="#2b2b2b")
        img_frame.place(relx=0.5, y=50, anchor="n")

        self.full_label = Label(img_frame, image=self.full_img, bg="#2b2b2b", bd=5, relief="flat")
        self.full_label.config(highlightbackground="#2b2b2b", highlightthickness=2, bd=2)
        self.full_label.pack(side=LEFT, padx=40)
        self.full_label.bind("<Button-1>", lambda e: self.select_scan("full"))

        self.custom_label = Label(img_frame, image=self.custom_img, bg="#2b2b2b", bd=5, relief="flat")
        self.custom_label.config(highlightbackground="#2b2b2b", highlightthickness=2, bd=2)
        self.custom_label.pack(side=LEFT, padx=40)
        self.custom_label.bind("<Button-1>", lambda e: self.select_scan("custom"))

        # Checkboxes
        Label(self, text="Tasks", font=("Segoe UI", 10),
              foreground="gray", background="#2b2b2b").place(x=100, y=320)
        self.options = [
            ("Recycle Bin", rc.RecycleBin),
            ("Temp", tc.TempCleaning),
            ("Temp32", tc32.Temp32Cleaning),
            ("Edge", bs.edgeCleanup),
            ("Firefox", bs.firefoxCleanup),
            ("Chrome", bs.chromeCleanup),
            ("Brave", bs.braveCleanup),
            ("Opera", bs.operaCleanup),
        ]
        self.checkbox_vars = []
        # Adjusted placement for checkbuttons
        for idx, (opt, _) in enumerate(self.options):
            var = IntVar()
            chk = Checkbutton(self, text=opt, variable=var, bootstyle="success-round-toggle")
            chk.place(x=100 + (idx % 4) * 220, y=360 + (idx // 4) * 40)
            self.checkbox_vars.append((var, chk))
            for var, chk in self.checkbox_vars:
                var.set(1)
                chk.config(state=DISABLED)


        # Progress section
        Label(self, text="Progress", font=("Segoe UI", 10), foreground="white", background="#2b2b2b").place(x=100, y=460)
        self.progress = ttk.Progressbar(self, length=800, mode="determinate")
        self.progress.place(x=100, y=490)

        self.progress_percent = Label(self, text="", font=("Segoe UI", 10), background="#2b2b2b", foreground="white")
        self.progress_percent.place(x=860, y=460)

        # Console logger
        self.console = ScrolledText(self, height=6, bg="#1e1e1e", fg="white", insertbackground="white", font=("Segoe UI", 10))
        self.console.place(x=100, y=530, width=800)

        # Scan Button
        self.scan_btn = Button(self, text="Run Scan", command=self.start_scan)
        self.scan_btn.place(relx=0.5, y=740, anchor="center")

    def log(self, message):
        self.console.insert(END, message + "\n")
        self.console.see(END)

    def select_scan(self, scan_type):
        self.selected_scan.set(scan_type)

        if scan_type == "full":
            self.full_label.config(highlightbackground="lime", highlightthickness=2, bd=2)
            self.custom_label.config(highlightbackground="#2b2b2b", highlightthickness=2, bd=2)
            for var, chk in self.checkbox_vars:
                var.set(1)
                chk.config(state=DISABLED)
            
        else:
            self.custom_label.config(highlightbackground="lime", highlightthickness=2, bd=2)
            self.full_label.config(highlightbackground="#2b2b2b", highlightthickness=2, bd=2)

            for var, chk in self.checkbox_vars:
                var.set(0)
                chk.config(state=NORMAL)

    def start_scan(self):
        if self.selected_scan.get() == "":
            self.log("⚠️ Please select a scan mode first!")
            return

        if not self.scan_running:
            self.scan_running = True
            self.scan_btn.config(text="Running Scan", state=DISABLED)
            self.progress["value"] = 0
            self.progress_percent.config(text="0%")
            self.console.delete("1.0", END)
            threading.Thread(target=self.run_scan_progress).start()

    def run_scan_progress(self):
        selected_tasks = [func for (var, _), (_, func) in zip(self.checkbox_vars, self.options) if var.get()]

        total_tasks = len(selected_tasks)
        if total_tasks == 0:
            self.log("⚠️ No tasks selected.")
            self.scan_btn.config(text="Run Scan", state=NORMAL)
            self.scan_running = False
            return

        progress_increment = 100 / total_tasks

        for i, task in enumerate(selected_tasks, start=1):
            task_name = self.options[[func for _, func in self.options].index(task)][0]
            self.log(f"🔄 Running {task_name} cleanup...")
            task()
            self.progress["value"] = i * progress_increment
            self.progress_percent.config(text=f"{int(i * progress_increment)}%")
            self.update_idletasks()
            time.sleep(0.5)  # Simulate time taken for each task

        self.progress["value"] = 100
        self.progress_percent.config(text="100%")
        self.log("✅ Scan complete! Your PC feels lighter already 😉")
        self.scan_btn.config(text="Run Scan", state=NORMAL)
        self.scan_running = False

if __name__ == "__main__":
    app = MainScreen()
    app.mainloop()
