import tkinter as tk
from tkinter import ttk
# Global variable
from settings import s

class CommandFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, borderwidth = 1, relief="solid")
        self.tuned_freq = 1000; # 1kHz should be what MCU outputs after reset

        self.freq_val_1 = tk.IntVar()
        self.freq_val_1.set(1) # Place slider at 1kHz
        self.freq_val_2 = tk.IntVar()
        self.freq_val_3 = tk.IntVar()
        self.freq_value_label = tk.Label(self, fg="white")
        self.freq_value_label.config(text = "1000 Hz")
        self.freq_value_label.config(bg="green")
        freq_label_1 = ttk.Label(self, text="Frequency (1000):")
        freq_label_2 = ttk.Label(self, text="Frequency (100):")
        freq_label_3 = ttk.Label(self, text="Frequency (1):")
        slider_1 = tk.Scale(self, orient=tk.HORIZONTAL,
            from_=0, to=99, length=400, resolution=1,
            variable=self.freq_val_1, command=self.to_label)
        slider_2 = tk.Scale(self, orient=tk.HORIZONTAL,
            from_=0, to=9, length=400, resolution=1,
            variable=self.freq_val_2, command=self.to_label)
        slider_3 = tk.Scale(self, orient=tk.HORIZONTAL,
            from_=0, to=100, length=400, resolution=1,
            variable=self.freq_val_3, command=self.to_label)
        button = tk.Button(self, text="Request Frequency",
            command=self.to_uwester)

        # Led light controls (put in separate frame)
        led_frame = tk.Frame(self, borderwidth=1, relief="solid")
        led_btn_on = tk.Button(led_frame, text="LED ON", command=self.led_on)
        led_btn_off = tk.Button(led_frame, text="LED OFF", command=self.led_off)
        led_btn_on.grid(row=0, column=0, sticky=tk.W)
        led_btn_off.grid(row=0, column=1, sticky=tk.W)

        # Placement
        freq_label_1.grid(row=0, column=0, sticky=(tk.W))
        freq_label_2.grid(row=1, column=0, sticky=(tk.W))
        freq_label_3.grid(row=2, column=0, sticky=(tk.W))
        slider_1.grid(row=0, column=1, sticky=(tk.W))
        slider_2.grid(row=1, column=1, sticky=(tk.W))
        slider_3.grid(row=2, column=1, sticky=(tk.W))
        self.freq_value_label.grid(row=0,column=2, sticky="W, S", padx=10)
        button.grid(row=1, column=2, sticky="W, N", padx=10)
        led_frame.grid(row=3, column=0, padx=5, pady=5)

    def to_label(self, val):
        self.tuned_freq = self.freq_val_1.get() * 1000 + \
                            self.freq_val_2.get() * 100 + \
                            self.freq_val_3.get()
        self.freq_value_label.config(text = str(self.tuned_freq) + " Hz")
        # If no reply from MCU this will remain red, otherwise
        # immediately become green
        self.freq_value_label.config(bg="red")

    def to_uwester(self):
        # Send the frequency to microcontroller
        # Sends two messages, one to indicate that we are sending a frequency
        # the other to specify what frequency
        try:
            s.write(b'FREQ')
            s.write(b'%d' % self.tuned_freq)
        except:
            print("Unable to send")

    def led_on(self):
        s.write(b'LD2 ON')

    def led_off(self):
        s.write(b'LD2 OFF')
