import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import mss
from PIL import Image
import torch
import torchvision.transforms as transforms
from classifier import SimpleCNN  # Assuming you have a classifier defined in classifier.py
from utils import select_screen_region  # Import the select_screen_region function
import threading
import time

class BotfishingApp(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.master.title("Botfishing Assistant")

        # Initialize classifier
        self.model = SimpleCNN()
        self.model.load_state_dict(torch.load('cnn.pth'))  # Load your trained model
        self.model.eval()

        # GUI components
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.select_button = ttk.Button(self.main_frame, text="Select Window", command=self.select_window)
        self.select_button.grid(row=0, column=0, padx=5, pady=5)

        self.start_button = ttk.Button(self.main_frame, text="Start Botfishing", command=self.start_botfishing)
        self.start_button.grid(row=0, column=1, padx=5, pady=5)

        self.stop_button = ttk.Button(self.main_frame, text="Stop Botfishing", command=self.stop_botfishing, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=2, padx=5, pady=5)

        self.quit_button = ttk.Button(self.main_frame, text="Quit", command=self.quit_application)
        self.quit_button.grid(row=0, column=3, padx=5, pady=5)

        self.count_label = ttk.Label(self.main_frame, text="0")
        self.count_label.grid(row=2, column=0, columnspan=4, pady=10)

        self.prob = ttk.Label(self.main_frame, text="0")
        self.prob.grid(row=1, column=0, columnspan=4, pady=10)

        self.monitor = None  # To store the selected monitor or window
        self.running = False  # Flag to indicate botfishing status
        self.thread = None  # Thread for botfishing task
        self.key_press_count = 0  # Counter for key presses
        self.prob = None

    def select_window(self):
        self.monitor = select_screen_region()
        if self.monitor:
            print(f"Selected region: {self.monitor}")
        else:
            print("No region selected")

    def start_botfishing(self):
        time.sleep(10)
        if self.monitor is None:
            messagebox.showerror("Error", "Please select a window first.")
            return
        
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Start a new thread for botfishing
        self.thread = threading.Thread(target=self.botfishing_task)
        self.thread.start()

    def stop_botfishing(self):
        self.running = False
        self.stop_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)

    def botfishing_task(self):
        while self.running:
            monitor_coords = {
                "left": self.monitor[0],
                "top": self.monitor[1],
                "width": self.monitor[2] - self.monitor[0],
                "height": self.monitor[3] - self.monitor[1]
            }

            with mss.mss() as sct:
                screenshot = sct.grab(monitor_coords)
                img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
                img = self.preprocess_image(img)

            with torch.no_grad():
                output = self.model(img)
                prediction = output.item()

            if prediction > 0.5:
                pyautogui.press('.')  # Simulate a dot key press
                self.key_press_count += 1
                self.prob = prediction
                self.update_count_label()
                time.sleep(1)
                pyautogui.press('.')
                time.sleep(4)

    def preprocess_image(self, img):
        transform = transforms.Compose([
            transforms.Resize((64, 64)),
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,))
        ])
        img = transform(img).unsqueeze(0)
        return img

    def update_count_label(self):
        self.count_label.config(text=str(self.key_press_count))

    def update_prob_label(self):
        self.count_prob.config(text=str(self.prob))

    def quit_application(self):
        if self.running:
            self.running = False
            self.thread.join()  # Wait for the thread to finish
        self.master.quit()

