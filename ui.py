import threading
from logging import getLogger
from time import sleep

from customtkinter import CTk, CTkButton, CTkFont, CTkFrame, CTkLabel

import file_handler
from snowrunner import SRCommands
from snowrunner.SRHack import test_pointers


class GUI:
    _instance = None

    def __init__(self):
        if GUI._instance:
            return GUI._instance
        self.logger = getLogger("GUI.Main")
        GUI._instance = self
        self.tk: CTk = CTk()
        self.tk.geometry("400x400")
        self.tk.resizable(False, False)
        self.tk.grid()
        self.tk.title("Twitch SR Commands")
        self.memory_frame: GUI.Snowrunner = self.Snowrunner(main=self.tk)
        self.exit_button: CTkButton = CTkButton(width=300, height=25, master=self.tk, text="Exit", command=self.tk.quit)
        self.exit_button.place(relx=0.5, rely=0.7, anchor="center")
        self.tk.mainloop()

    class Snowrunner:
        def __init__(self, main):
            self.main = main
            self.logger = getLogger("GUI.MemoryFrame")
            self.header_text: str = "Memory checks"
            self.text_positive: str = "Loading ..."
            self.frame = CTkFrame(master=self.main, corner_radius=8, width=350, fg_color=None, height=200, border_width=2)
            self.frame.place(relx=0.05, rely=0.05)
            self.header = CTkLabel(master=self.frame, text=self.header_text, font=CTkFont(family=None, size=20))
            self.header.place(relx=0.5, y=10, anchor="n")
            self.memory_label = CTkLabel(master=self.frame, text=self.text_positive, font=CTkFont(family=None, size=16), justify="left")
            self.memory_label.place(relx=0.5, rely=0.2, anchor="n")
            self.save_button: CTkButton = CTkButton(
                width=300,
                height=25,
                master=self.frame,
                text="Save Fuel Data",
                command=lambda: file_handler.write_to_file(SRCommands.fuel_stats, "fuel_stats.json"),
            )
            self.save_button.place(relx=0.5, rely=0.6, anchor="center")
            self.load_button: CTkButton = CTkButton(
                width=300,
                height=25,
                master=self.frame,
                text="Load Fuel Data",
                command=SRCommands.load_fuel_stats,
            )
            self.load_button.place(relx=0.5, rely=0.8, anchor="center")

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
                    self.logger.debug("Program closed.")
                    break


if __name__ == "__main__":
    GUI()
