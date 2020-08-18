import tkinter as tk
from tkinter import ttk
from settings import s
import serial.tools.list_ports as lp

class USBFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, borderwidth = 1, relief = "solid")
        # To store the list of ports
        self.file_list = []

        # Widgets
        self.listbox_usb = tk.Listbox(self, selectmode ='single',
            width = 60, height = 5)
        but_scan = tk.Button(self, text = 'Scan', command = self.scan)
        but_select = tk.Button(self, text = 'Select', command = self.select)
        self.labelText = tk.StringVar()
        # Label not visible until selection is made
        self.con_label = tk.Label(self, textvariable=self.labelText, fg="white")

        # Placement
        self.listbox_usb.grid(row = 0, column = 0,padx = 5, pady = 5, columnspan = 3)
        but_scan.grid(row = 1, column = 0, padx =5, pady = 5, sticky = tk.W)
        but_select.grid(row = 1, column = 1, padx = 5, pady = 5, sticky = tk.W)
        self.con_label.grid(row = 1, column = 2, padx = 5, pady = 5, sticky = tk.W)

    def scan(self):
        self.listbox_usb.delete(0,tk.END)
        self.file_list = lp.comports()
        for fl in self.file_list:
            self.listbox_usb.insert(tk.END, fl)

    def select(self):
        index = self.listbox_usb.curselection()[0] # a tuple is returned
        serial_port = self.file_list[index]
        print("You have selected: " + serial_port.device)
        self.labelText.set(serial_port.device)
        try:
            s.port = serial_port.device
            s.open()
        except:
            # Indicate that something went wrong
            # Label is now shown (in red)
            self.con_label.config(bg="red")
        if(s.is_open):
            print(s.name + " open")
            # Label is now shown (in green)
            self.con_label.config(bg="green")
