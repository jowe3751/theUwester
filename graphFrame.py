import tkinter as tk
from tkinter import ttk
import threading
from settings import s

class GraphFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, borderwidth = 1, relief = "solid")

        # To access frequency from commandFrame
        self.uwester = parent

        # Time per div in seconds
        self.timedivs = [0.000005, 0.00001, 0.00002, 0.00005, 0.0001,
                    0.0002, 0.0005, 0.001, 0.002, 0.005,
                    0.01, 0.02, 0.05]

        # Corresponding values shown in GUI
        self.timedivs_text = ["5us", "10us", "20us", "50us", "100us",
                    "200us", "500us", "1ms", "2ms", "5ms",
                    "10ms", "20ms", "50ms"]

        # Calculated values for ADC timer periods by MCU using a 80 MHz clock
        self.periods = [x*800000//1 for x in self.timedivs]
        self.period_index = 7 # MCU is initialized to 1ms after reset
        self.width = 900
        self.height = 300
        self.paused = False # Program may be paused to ease measurements
        self.x = 0 # x-pos on canvas
        self.increment = 1 # Standard increment, may be changed later by program
        self.y_last = [0, 0] # Two input channels
        self.time_text = tk.StringVar() # Ex. "1ms"
        self.time_text.set(str(self.timedivs_text[7])) # Display to user
        self.offset = tk.IntVar()
        # Measurement values
        self.volt = tk.StringVar()
        self.time = tk.StringVar()
        self.phi = tk.StringVar()
        self.vppch1 = tk.StringVar()
        self.vppch2 = tk.StringVar()
        self.volt.set("")
        self.time.set("")
        self.phi.set("")
        self.vppch1.set("")
        self.vppch2.set("")
        self.channel_select = tk.IntVar() # 1, 2 or 3 (Both)

        # Canvas
        self.can = tk.Canvas(self, highlightthickness=0, borderwidth=0,
            width = self.width, height = self.height+1, bg = '#000000')
        # Draw vertical guide lines
        for x in range(0, 1000, 100):
            self.can.create_line(x, 0, x, self.height, fill='#808080')
            for xx in range(20, 100, 20):
                self.can.create_line(x+xx, self.height/2-2, x+xx,
                    self.height/2+2, fill='#808080')
        # Draw horizontal guide line
        self.can.create_line(0, self.height/2, self.width, self.height/2,
                                fill='#808080')

        # Offset frame
        offset_frm = tk.Frame(self, borderwidth=1, relief="solid")
        offset_label = ttk.Label(offset_frm, text="Offset:  ")
        offset_slider = tk.Scale(offset_frm, orient=tk.HORIZONTAL, from_=0,
                            to=100, length=200, resolution=1,
                            variable=self.offset)
        offset_label.grid(row = 0, column = 0, padx=5)
        offset_slider.grid(row = 0, column = 1, sticky=(tk.W))

        # Pause/resume frame
        pause_frm = tk.Frame(self, borderwidth=1, relief="solid")
        self.button_start = tk.Button(pause_frm, text="Start",
            command=self.resume, state=tk.DISABLED)
        self.button_pause = tk.Button(pause_frm, text="Pause",
            command=self.pause)
        self.button_start.grid(row=0, column=0)
        self.button_pause.grid(row=0, column=1)

        # Time/Div frame
        time_frm = tk.Frame(self, borderwidth=1, relief="solid")
        time_button_left = tk.Button(time_frm, text="<", command=self.time_decrease)
        time_button_right = tk.Button(time_frm, text=">", command=self.time_increase)
        time_label = ttk.Label(time_frm, text="Time/Div: ")
        self.time_choice = tk.Label(time_frm, textvariable=self.time_text,
                                    width=5, fg="white")
        self.time_choice.config(bg="red")
        time_button = tk.Button(time_frm, text="Change Resolution",
            command=self.to_uwester)
        time_label.grid(row = 0, column = 0, padx=5, pady=5)
        time_button_left.grid(row = 0, column = 1)
        time_button_right.grid(row = 0, column = 2)
        self.time_choice.grid(row = 0,  column = 3, padx=5, pady=5)
        time_button.grid(row=0, column=4, padx=5)

        # Measurement frame
        measure_frm = tk.Frame(self, borderwidth=1, relief="solid")
        measure_header_label = tk.Label(measure_frm,font = "verdana 8 bold", text="MEASUREMENTS");
        measure_volt_label = tk.Label(measure_frm, text="Voltage: ");
        measure_dt_label = tk.Label(measure_frm, text="dt: ");
        measure_phi_label = tk.Label(measure_frm, text="phs: ");
        measure_vppch1_label = tk.Label(measure_frm, text="Vpp CH1: ");
        measure_vppch2_label = tk.Label(measure_frm, text="Vpp CH2: ");
        measure_volt_value = tk.Label(measure_frm, width=10, textvariable=self.volt);
        measure_dt_value = tk.Label(measure_frm, width=10, textvariable=self.time);
        measure_phi_value = tk.Label(measure_frm, width=10, textvariable=self.phi);
        measure_vppch1_value = tk.Label(measure_frm, width=10, textvariable=self.vppch1);
        measure_vppch2_value = tk.Label(measure_frm, width=10, textvariable=self.vppch2);
        measure_header_label.grid(row=0, column=0, columnspan=2)
        measure_volt_label.grid(row=1, column=0, sticky=(tk.W))
        measure_volt_value.grid(row=1, column=1, sticky=(tk.W))
        measure_dt_label.grid(row=2, column=0, sticky=(tk.W))
        measure_dt_value.grid(row=2, column=1, sticky=(tk.W))
        measure_phi_label.grid(row=3, column=0, sticky=(tk.W))
        measure_phi_value.grid(row=3, column=1, sticky=(tk.W))
        measure_vppch1_label.grid(row=4, column=0, sticky=(tk.W))
        measure_vppch1_value.grid(row=4, column=1, sticky=(tk.W))
        measure_vppch2_label.grid(row=5, column=0, sticky=(tk.W))
        measure_vppch2_value.grid(row=5, column=1, sticky=(tk.W))

        # Channel select frame
        chsel_frm = tk.Frame(self, borderwidth=1, relief="solid")
        r1 = tk.Radiobutton(chsel_frm, text="Ch1", variable=self.channel_select, value=1)
        r2 = tk.Radiobutton(chsel_frm, text="Ch2", variable=self.channel_select, value=2)
        r3 = tk.Radiobutton(chsel_frm, text="Both", variable=self.channel_select, value=3)
        r3.select() # Default choice
        r1.grid(row=0, column=0)
        r2.grid(row=1, column=0)
        r3.grid(row=2, column=0)

        #Placement
        self.can.grid(row=0, column=0, columnspan=5)
        offset_frm.grid(row=1, column=0, padx=5)
        pause_frm.grid(row=1, column=1)
        time_frm.grid(row=1, column=2)
        measure_frm.grid(row=1, column=3)
        chsel_frm.grid(row=1, column=4)

        # Bind mouse functions
        self.can.bind("<Button-1>", self.mouse_lh)
        self.can.bind("<Button-2>", self.mouse_rh) # For OSX
        self.can.bind("<Button-3>", self.mouse_rh) # Standard right click
        self.can.bind("<Button-4>", self.mouse_scrollup) # X11
        self.can.bind("<Button-5>", self.mouse_scrolldown) # X11
        self.can.bind("<MouseWheel>", self.mouse_scroll) # OSX & Windows
        self.can.bind("<Control-MouseWheel>", self.mouse_ctrl_scroll) # OSX & Windows
        self.can.bind("<Control-Button-4>", self.mouse_ctrl_scrollup) # X11
        self.can.bind("<Control-Button-5>", self.mouse_ctrl_scrolldown) # X11
        # Init vars for measurements
        # First click measures voltage, second click measures time
        # between x1 and x2
        self.clickedOnce = False
        self.clickedTwice = False
        self.x1 = 0
        self.x2 = 0

    def plot(self, *args):
        palette = ['#FFFF00','#00BFFF']
        if self.x < self.width + self.offset.get():
            for (channel, y) in enumerate(args):
                y = args[channel]
                if self.x == 0:
                    self.y_last[channel] = y

                if y > 0:
                    self.can.create_line(self.x - self.increment - self.offset.get(),
                        self.height - self.y_last[channel],
                        self.x - self.offset.get(),
                        self.height - y,
                        fill = palette[channel], tags="read_values")
                    self.y_last[channel] = y

            self.x = self.x + self.increment

    def resume(self):
        self.button_start.config(state=tk.DISABLED)
        self.button_pause.config(state=tk.NORMAL)
        self.paused = False

    def pause(self):
        self.button_start.config(state=tk.NORMAL)
        self.button_pause.config(state=tk.DISABLED)
        self.paused = True

    def time_decrease(self):
        if self.period_index > 0:
            self.period_index -= 1
        self.time_text.set(str(self.timedivs_text[self.period_index]))
        self.time_choice.config(bg="red")

    def time_increase(self):
        if self.period_index < len(self.periods)-1:
            self.period_index += 1
        self.time_text.set(str(self.timedivs_text[self.period_index]))
        self.time_choice.config(bg="red")

    def mouse_lh(self, event):
        if self.clickedOnce == False:
            self.time.set("")
            self.phi.set("")
            self.can.delete("x1") # clear previous measurement
            self.can.delete("x2") # clear previous measurement
            self.x1 = event.x
            self.volt_measure = event.y
            # redraw first vertical line
            self.can.create_line(self.x1, 0, self.x1, self.height,
                fill='#FF0000', tags="x1")
            self.calculate_volt()
            self.clickedOnce = True
            self.clickedTwice = False

        elif self.clickedOnce == True:
            self.can.delete("volt") # clear previous measurement
            self.volt.set(" ")
            self.x2 = event.x
            self.can.create_line(self.x2, 0, self.x2, self.height,
                fill='#FF0000', tags="x2")
            self.clickedOnce = False
            self.clickedTwice = True
            self.calculate_dt()

    def mouse_rh(self, event):
        self.can.delete("x1", "x2", "volt") # clear previous measurement
        self.volt.set("")
        self.time.set("")
        self.phi.set("")
        self.clickedOnce = False
        self.clickedTwice = False

    def mouse_scrollup(self, event):
        if self.clickedOnce == True:
            self.x1 -= 1
            self.can.delete("x1") # clear previous measurement
            self.can.create_line(self.x1, 0, self.x1, self.height,
                fill='#FF0000', tags="x1")
        elif self.clickedTwice == True:
            self.x2 -= 1
            self.can.delete("x2") # clear previous measurement
            self.can.create_line(self.x2, 0, self.x2, self.height,
            fill='#FF0000', tags="x2")
            self.calculate_dt()

    def mouse_scrolldown(self, event):
        if self.clickedOnce == True:
            self.x1 += 1
            self.can.delete("x1") # clear previous measurement
            self.can.create_line(self.x1, 0, self.x1, self.height,
                fill='#FF0000', tags="x1")
        elif self.clickedTwice == True:
            self.x2 += 1
            self.can.delete("x2") # clear previous measurement
            self.can.create_line(self.x2, 0, self.x2, self.height,
            fill='#FF0000', tags="x2")
            self.calculate_dt()

    def mouse_scroll(self, event):
        if self.clickedOnce == True:
            if(event.delta > 0): # scroll up
                self.x1 -= 1
            else: #scroll down
                self.x1 += 1
            self.can.delete("x1") # clear previous measurement
            self.can.create_line(self.x1, 0, self.x1, self.height,
                fill='#FF0000', tags="x1")
        elif self.clickedTwice == True:
            if(event.delta > 0): # scroll up
                self.x2 -= 1
            else: # scroll down
                self.x2 += 1
            self.can.delete("x2") # clear previous measurement
            self.can.create_line(self.x2, 0, self.x2, self.height,
                fill='#FF0000', tags="x2")
            self.calculate_dt()

    def mouse_ctrl_scroll(self, event):
        if self.clickedOnce == True:
            if(event.delta > 0): # scroll up
                self.volt_measure -= 1
            else:
                self.volt_measure += 1
            self.calculate_volt()

    def mouse_ctrl_scrollup(self, event):
        if self.clickedOnce == True:
            self.volt_measure -= 1
            self.calculate_volt()

    def mouse_ctrl_scrolldown(self, event):
        if self.clickedOnce == True:
            self.volt_measure += 1
            self.calculate_volt()

    def calculate_volt(self):
        # Translate from 0V - 3.3V --> -4V - +4V
        volt_val = self.volt_measure - self.height / 2
        volt_val = volt_val * - 4 / (self.height//2)
        volt_val = round(volt_val, 2)
        self.volt.set(str(volt_val) + " v")
        # redraw vertical line 1
        self.can.delete("volt") # clear previous measurement
        self.can.create_line(0, self.volt_measure, self.width, self.volt_measure,
        fill='#FF0000', tags="volt")


    def calculate_dt(self):
        dt = self.x1-self.x2
        dt = dt * self.timedivs[self.period_index] / 100
        disp = abs(dt * 1000) # to ms
        disp = round(disp, 5)
        frequency = self.uwester.get_frequency()
        #ang = 360 * f * dt
        phi = 360 * frequency * dt
        phi = round(phi, 2)
        self.phi.set(str(phi) + " deg")
        if disp < 1: # present as us
            disp *= 1000
            disp = round(disp, 5)
            self.time.set(str(disp) + " us")
        else:
            self.time.set(str(disp) + " ms")

    def update_vpp(self, vpp_values):
        ch1, ch2 = vpp_values
        self.vppch1.set(str(ch1) + " V")
        self.vppch2.set(str(ch2) + " V")

    def to_uwester(self):
        self.time_choice.config(bg="red")
        self.increment = 1
        period_to_send = self.periods[self.period_index]
        # if less than 20us
        if(self.period_index < 2):
            # thats too fast for ADC so:
            # send 20us to MCU
            period_to_send = self.periods[2]
            # and fix resolution in software instead
            if self.period_index == 1:
                self.increment = 2
            elif self.period_index == 0:
                self.increment = 4
            # Simplified
            # self.increment = 4 - 2 * self.period_index
        # Send the multiplier
        try:
            s.write(b'TIME')
            s.write(b'%d' % period_to_send)
        except:
            print("Unable to send")
