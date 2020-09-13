import math
import tkinter.filedialog
import tkinter as tk
from tkinter import ttk
import threading
import time
import serial
import pyscreenshot

# Global variable
from settings import s
# Different frames in different modules
from commandFrame import CommandFrame
from graphFrame import GraphFrame
from usbFrame import USBFrame

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("The Uwester")

        # Menu
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save Image",command=self.save_img)
        filemenu.add_command(label="Quit",command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.config(menu=menubar)

        # Add modules
        self.graph = GraphFrame(self)
        self.cmd = CommandFrame(self)
        self.usb = USBFrame(self)

        # Placement
        self.graph.grid(row=0, column=0, sticky=tk.W)
        self.cmd.grid(row=1, column=0, pady=1, sticky=tk.W)
        self.usb.grid(row=2, column=0, sticky=tk.W)

        # Start separate thread to read from MCU
        self.start_read()

    def save_img(self):
        filename = tk.filedialog.asksaveasfilename(title="Save File",
            filetypes = (("png files","*.png"),("all files","*.*")),
            defaultextension=".png")
        if filename:
            x=self.winfo_rootx()
            y=self.winfo_rooty()
            x1=x+self.winfo_width()
            y1=y+self.winfo_height()
            time.sleep(0.5) # So that popup has time to close
            pyscreenshot.grab(bbox=(x,y,x1,y1)).save(filename)

    def get_frequency(self):
        return self.cmd.tuned_freq

    def start_read(self):
        # Start a new thread and read values
        tr = threading.Thread(target = self.read, args = ())
        tr.setDaemon(True)
        tr.start()

    def initialize(self):
        self.graph.paused = True
        time.sleep(1)
        # Init frequency current value in GUI
        print("init freq...")
        self.cmd.to_uwester()
        # Init time/div to current value in GUI
        print("init time...")
        self.graph.to_uwester()
        # Display values again
        self.graph.paused = False

    def read(self): # function called from separate thread

        # wait for main thread to open serial connection
        while not s.is_open:
            time.sleep(0.1)

        # Toggle needed because of reasons on OS X - Yosemite
        s.close()
        s.open()

        # remove potential stuff in buffer
        s.reset_input_buffer()

        # start to read
        while True:
            if(s.is_open):
                # IMPORTANT: s.readline() reads until newline char is received
                try:
                    str = s.readline().decode('ascii').split(" ")
                    # creates a string list ex:
                    # ["frequency_ok", "\r\n"]
                    # ["time_ok", "\r\n"]
                    # ["123", "234", ...,  "\r\n"]
                    if (str[0] == "frequency_ok"):
                        print("frequency_ok")
                        self.cmd.freq_value_label.config(bg="green")
                    elif (str[0] == "time_ok"):
                        print("time_ok")
                        self.graph.time_choice.config(bg="green")
                    elif (not self.graph.paused):
                        str = str[:-1:] # remove "\r\n"
                        values = list(map(int, str)) # convert string to int
                        self.calc_vpp(values)
                        self.graph.can.delete("read_values") # clear previous plot
                        self.graph.x = 0
                        for i in range(0, len(values)-1, 2):
                            try:
                                # option to filter out channel in GUI
                                if self.graph.channel_select.get() == 1:
                                    y1 = values[i]/4095 * self.graph.height
                                    self.graph.plot(y1, 0)
                                elif self.graph.channel_select.get() == 2:
                                    y2 = values[i+1]/4095 * self.graph.height
                                    self.graph.plot(0, y2)
                                else:
                                    y1 = values[i]/4095 * self.graph.height
                                    y2 = values[i+1]/4095 * self.graph.height
                                    self.graph.plot(y1, y2)
                            except:
                                print("error in read()")

                except serial.SerialException:
                    # in case cable hot-unplugged
                    print("Check cable connection, shutting down application")
                    self.quit()
                except:
                    print("Error reading from MCU")

    def calc_vpp(self, l):
        # separate channel 1 from channel 2
        ch1 = l[::2]
        ch2 = l[1::2]
        # calculate vpp
        #print("Vpp ch1:", round((max(ch1)-min(ch1))/4095*8, 2))
        #print("Vpp ch2:", round((max(ch2)-min(ch2))/4095*8, 2))
        vppch1 = round((max(ch1)-min(ch1))/4095*8, 2)
        vppch2 = round((max(ch2)-min(ch2))/4095*8, 2)
        self.graph.update_vpp((vppch1, vppch2))

if __name__ == '__main__':
    app = App()
    app.mainloop()
    # Close serial connection
    s.close()
