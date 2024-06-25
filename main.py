import tkinter as tk
from gui import BotfishingApp

if __name__ == "__main__":
    root = tk.Tk()
    app = BotfishingApp(root)
    app.grid()
    root.mainloop()
