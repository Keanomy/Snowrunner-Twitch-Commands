import threading
from logging import getLogger
from test import test_pointers
from time import sleep

from customtkinter import CTk, CTkButton, CTkFont, CTkFrame, CTkLabel

logger = getLogger("GUI")


class GUI:
    _instance = None

    def __init__(self):
        if GUI._instance:
            return GUI._instance
        GUI._instance = self
        self.tk: CTk = CTk()
        self.tk.geometry("400x400")
        self.tk.resizable(False, False)
        self.tk.title("Twitch SR Commands")
        self.memory_frame: GUI.MemoryFrame = self.MemoryFrame(master=self.tk)
        self.button: CTkButton = CTkButton(width=300, height=50, master=self.tk, text="Exit", command=self.tk.quit)
        self.button.place(x=200, y=350, anchor="center")
        self.tk.mainloop()

    class MemoryFrame:
        def __init__(self, master):
            self.master = master
            self.header_text: str = "Memory checks"
            self.text_positive: str = "Loading ..."
            self.frame = CTkFrame(master=self.master, corner_radius=8, width=350, fg_color=None, height=50, border_width=2)
            self.frame.place(x=200, y=40, anchor="n")
            self.header = CTkLabel(master=self.master, text=self.header_text, font=CTkFont(family=None, size=20))
            self.header.place(relx=0.5, y=10, anchor="n")
            self.memory_label = CTkLabel(master=self.frame, text=self.text_positive, font=CTkFont(family=None, size=16), justify="left")
            self.memory_label.place(x=10, y=4)
            threading.Thread(target=self.update, daemon=True).start()

        def update(self):
            timeout: int = 10
            while True:
                success, failed, sr_running = test_pointers()
                if not sr_running:
                    self.text_positive: str = f"Snowrunner not runnning..."
                    sleep(timeout)
                    if timeout < 900:
                        timeout *= 2
                else:
                    self.text_positive: str = f"Successful:  {len(success)}\nFailed:      {len(failed)}"
                    timeout = 1
                    sleep(timeout)
                try:
                    self.memory_label.configure(text=self.text_positive)
                except RuntimeError:
                    logger.debug("Program closed.")
                    break
