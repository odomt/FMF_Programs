# TODO: accept filename input (e.g. x=850_y=0_z=30_n=40)
from tkinter import *
import customtkinter as ctk
from labjack import ljm
from datetime import datetime as dt
import os
import sys

ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class FastFID(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("FastFID Repetition Logger")
        self.geometry("325x350")
        self.resizable(False, False)

        # create frame for GUI
        self.grid_columnconfigure(0, weight=10)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=8)
        self.tabview_frame = ctk.CTkTabview(self)  # creates frame within main window with multiple tabs
        self.tabview_frame.grid(row=2, column=0, sticky="nsew")

        # setup for LabJack
        self.handle = ljm.openS("T7", "ANY", "ANY")  # Any device, Any connection, Any identifier
        info = ljm.getHandleInfo(self.handle)  # (Device Type, Connection Type, Serial Number)
        print("Opened LabJack: (" + str(info[0]) + ", " + str(info[1]) + ", " + str(info[2]) + ")")
        self.valve_state = 0  # Output state = low (0 = low, 1 = high)
        self.input_fastfid = "AIN2"
        self.f = None
        self.cwd = ""

        # configure timestamp variables
        self.date_format = "%Y-%m-%d"  # year-month-day
        self.timestamp_format = "%H:%M:%S.%f"  # hour:minute:second.microsecond
        # self.log_time_format = "%M:%S.%f"  # minute:second.microsecond

        self.app_start_timestamp = dt.now()  # get the current time to build a time-stamp
        self.app_start_date_str = self.app_start_timestamp.strftime(self.date_format)  # start date for logging
        self.app_start_time_str = self.app_start_timestamp.strftime(self.timestamp_format)  # start time for logging

        self.start_log_timestamp = None
        self.start_log_time_str = ""
        self.start_log_date_str = ""
        self.start_log_obj = None

        self.end_log_timestamp = None
        self.end_log_time_str = ""
        self.end_log_date_str = ""
        self.end_log_obj = None

        # MAIN WINDOW
        # - create labels
        self.label_status = ctk.CTkLabel(self, text="Waiting...")

        # - create buttons
        self.button_start = ctk.CTkButton(self, text="Start", hover_color="dark olive green", fg_color="olive drab",
                                          width=50, command=lambda: self.init_timer())
        self.button_quit = ctk.CTkButton(self, text="Quit", hover_color="dark red", fg_color="red", width=50,
                                         command=lambda: self.quit_program())

        # - widget placements within GUI
        self.button_start.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.button_quit.grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.label_status.grid(row=1, column=0, columnspan=3, padx=5, pady=5)
        self.tabview_frame.grid(row=2, column=0, columnspan=3,  padx=5, pady=5)

        # LOGGING TAB
        self.tabview_frame.add("View")

        # - create variables
        self.time_on = IntVar()  # set on timer
        self.time_off = IntVar()  # set off timer
        self.reps = IntVar()  # set reps
        self.rate_hz = IntVar()  # set log rate
        self.rate_ms = DoubleVar()
        self.rate_micro = DoubleVar()
        self.time_on_counter = IntVar()  # on timer counter
        self.time_off_counter = IntVar()  # off timer counter
        self.reps_counter = IntVar()  # reps counter
        self.input_ID = StringVar()  # set input ID
        self.output_ID = StringVar()  # set output ID
        self.filename = StringVar()  # set filename
        self.filepath = StringVar()  # set filepath
        self.log_start_time = StringVar()

        # - assign values to variables
        self.time_on.set(20)  # hard-coded default on timer
        self.time_off.set(10)  # hard-coded default off timer
        self.reps.set(40)  # hard-coded default number of reps
        self.rate_hz.set(20)  # hertz
        self.rate_ms.set((1 / self.rate_hz.get()) * 1000)  # milliseconds, 20Hz = 50ms = 0.050s
        self.rate_micro.set(self.rate_ms.get() * 1000)  # microseconds, 20Hz = 50000us
        self.input_ID.set("AIN0")  # hard-coded default LabJack input ID
        print("Input set to LabJack ID: " + self.input_ID.get())
        self.output_ID.set("FIO0")  # hard-coded default LabJack output ID
        print("Valve set to LabJack ID: " + self.output_ID.get())
        ljm.eWriteName(self.handle, self.output_ID.get(), self.valve_state)  # initialize program with valve closed
        print("State = " + str(self.valve_state) + " or 'closed'")
        self.filename.set("ff_data.csv")  # hard-coded default filename

        # - create labels
        self.label_input = ctk.CTkLabel(self.tabview_frame.tab("View"), text="Input:")
        self.label_input_value = ctk.CTkLabel(self.tabview_frame.tab("View"), text="-")
        self.label_time_on = ctk.CTkLabel(self.tabview_frame.tab("View"), text="On Timer:", width=50)
        self.label_time_on_counter = ctk.CTkLabel(self.tabview_frame.tab("View"), text="#", width=50)
        self.label_time_off = ctk.CTkLabel(self.tabview_frame.tab("View"), text="Off Timer:", width=50)
        self.label_time_off_counter = ctk.CTkLabel(self.tabview_frame.tab("View"), text="#", width=50)
        self.label_reps = ctk.CTkLabel(self.tabview_frame.tab("View"), text="Reps Left:", width=50)
        self.label_reps_counter = ctk.CTkLabel(self.tabview_frame.tab("View"), text="#", width=50)
        self.label_output = ctk.CTkLabel(self.tabview_frame.tab("View"), text="Valve Status:", width=50)
        self.label_output_status = ctk.CTkLabel(self.tabview_frame.tab("View"), text="-", width=50)
        self.label_log_filepath = ctk.CTkLabel(self.tabview_frame.tab("View"),
                                               text="Filepath:\n" + self.cwd + "\n" + self.filename.get())

        # - widget placements
        self.label_input.grid(row=0, column=0, columnspan=2, pady=5, padx=(80, 0), sticky="e")
        self.label_input_value.grid(row=0, column=2, pady=5, padx=(5, 0))
        self.label_output.grid(row=1, column=0, columnspan=2, pady=5, padx=(80, 0), sticky="e")
        self.label_output_status.grid(row=1, column=2, pady=5, padx=(5, 0))
        self.label_time_on.grid(row=2, column=0, columnspan=2, pady=5, padx=(80, 0), sticky="e")
        self.label_time_on_counter.grid(row=2, column=2, pady=5, padx=(5, 0))
        self.label_time_off.grid(row=3, column=0, columnspan=2, pady=5, padx=(80, 0), sticky="e")
        self.label_time_off_counter.grid(row=3, column=2, pady=5, padx=(5, 0))
        self.label_reps.grid(row=4, column=0, columnspan=2, pady=5, padx=(80, 0), sticky="e")
        self.label_reps_counter.grid(row=4, column=2, pady=5, padx=(5, 0))

        # SETUP TAB
        self.tabview_frame.add("Setup")

        # - create labels
        self.label_time_on_setup = ctk.CTkLabel(self.tabview_frame.tab("Setup"), text="Time On:")
        self.label_input_setup = ctk.CTkLabel(self.tabview_frame.tab("Setup"), text="DAQ Input:")
        self.label_time_off_setup = ctk.CTkLabel(self.tabview_frame.tab("Setup"), text="Time Off:")
        self.label_output_setup = ctk.CTkLabel(self.tabview_frame.tab("Setup"), text="DAQ Output:")
        self.label_reps_setup = ctk.CTkLabel(self.tabview_frame.tab("Setup"), text="Total Reps:")
        self.label_rate_setup = ctk.CTkLabel(self.tabview_frame.tab("Setup"), text="Rate (Hz):")
        self.label_filename = ctk.CTkLabel(self.tabview_frame.tab("Setup"), text="Data Filename:")

        # - create user input entry fields
        self.entry_time_on = ctk.CTkEntry(self.tabview_frame.tab("Setup"), textvariable=self.time_on, width=50)
        self.combobox_input = ctk.CTkComboBox(self.tabview_frame.tab("Setup"), width=80,
                                              values=["AIN0", "AIN1", "AIN2", "AIN3", "AIN0_EF_READ_A",
                                                      "AIN1_EF_READ_A", "AIN2_EF_READ_A", "AIN3_EF_READ_A"])
        self.entry_time_off = ctk.CTkEntry(self.tabview_frame.tab("Setup"), textvariable=self.time_off, width=50)
        self.combobox_output = ctk.CTkComboBox(self.tabview_frame.tab("Setup"), width=80,
                                               values=["FIO0", "FIO1", "FIO2", "FIO3"])
        self.entry_reps = ctk.CTkEntry(self.tabview_frame.tab("Setup"), textvariable=self.reps, width=50)
        self.entry_rate = ctk.CTkEntry(self.tabview_frame.tab("Setup"), textvariable=self.rate_hz, width=50)
        self.entry_filename = ctk.CTkEntry(self.tabview_frame.tab("Setup"), width=210, textvariable=self.filename)

        # - create buttons
        self.button_update = ctk.CTkButton(self.tabview_frame.tab("Setup"), text="Update", width=50,
                                           command=lambda: self.update_config())

        # - widget placements
        self.label_time_on_setup.grid(row=0, column=0, pady=5, padx=(10, 0), sticky="e")
        self.entry_time_on.grid(row=0, column=1, pady=5, padx=(5, 0))
        self.label_input_setup.grid(row=0, column=2, pady=5, padx=(10, 0), sticky="e")
        self.combobox_input.grid(row=0, column=3, pady=5, padx=(5, 0))
        self.label_time_off_setup.grid(row=1, column=0, pady=5, padx=(10, 0), sticky="e")
        self.entry_time_off.grid(row=1, column=1, pady=5, padx=(5, 0))
        self.label_output_setup.grid(row=1, column=2, pady=5, padx=(10, 0), sticky="e")
        self.combobox_output.grid(row=1, column=3, pady=5, padx=(5, 0))
        self.label_reps_setup.grid(row=2, column=0, pady=5, padx=(10, 0), sticky="e")
        self.entry_reps.grid(row=2, column=1, pady=5, padx=(5, 0))
        self.label_rate_setup.grid(row=2, column=2, pady=5, padx=(10, 0), sticky="e")
        self.entry_rate.grid(row=2, column=3, pady=5, padx=(5, 0))
        self.label_filename.grid(row=3, column=0, columnspan=4, pady=5, padx=(10, 0))
        self.entry_filename.grid(row=4, column=0, columnspan=4, pady=0, padx=(10, 0))
        self.button_update.grid(row=5, column=0, columnspan=4, pady=5, padx=(10, 0))

    # FUNCTIONS
    # overall repetition counter (complete timer on and timer off sequence)
    def init_timer(self):
        self.button_start.configure(state="disabled")
        self.time_on.set(self.entry_time_on.get())  # binds time on to entry value
        self.time_on_counter.set(self.entry_time_on.get())
        self.time_off.set(self.entry_time_off.get())  # binds time off to entry value
        self.time_off_counter.set(self.entry_time_off.get())
        self.reps.set(self.entry_reps.get())  # binds number of reps to entry value
        self.reps_counter.set(self.reps.get())
        self.input_ID.set(self.combobox_input.get())  # binds input ID to entry value
        self.output_ID.set(self.combobox_output.get())  # binds output ID to entry value
        self.label_status.configure(text="Running", text_color="yellow")

        self.start_log_timestamp = dt.now()  # get and format a timestamp
        self.start_log_date_str = self.start_log_timestamp.strftime(self.date_format)
        self.start_log_time_str = self.start_log_timestamp.strftime(self.timestamp_format)
        self.start_log_obj = dt.strptime(self.start_log_time_str, self.timestamp_format)
        self.f.write("%s\n%s\n\n\n\n" % (self.start_log_date_str, self.start_log_time_str))
        self.f.write("Time,Output (FIO#),Input (AIN#)\n")
        self.time_on_countdown_timer()
        self.log_input()

    # count down the on timer for each rep
    def time_on_countdown_timer(self):
        self.valve_state = 1
        ljm.eWriteName(self.handle, self.output_ID.get(), self.valve_state)
        self.label_output_status.configure(text="Open", text_color="green")
        if self.time_on_counter.get() < 1:
            self.time_off_countdown_timer()
        else:
            self.time_on_counter.set(self.time_on_counter.get() - 1)
            self.label_time_on_counter.configure(text="%d" % self.time_on_counter.get())
            self.label_time_off_counter.configure(text="%d" % self.time_off_counter.get())
            self.label_reps_counter.configure(text="%d" % self.reps_counter.get())
            self.after(1000, self.time_on_countdown_timer)
        return

    # count down the off timer for each rep
    def time_off_countdown_timer(self):
        self.valve_state = 0
        ljm.eWriteName(self.handle, self.output_ID.get(), self.valve_state)
        self.label_output_status.configure(text="Closed", text_color="red")
        if self.time_off_counter.get() < 1:
            self.rep_countdown()
        else:
            self.time_off_counter.set(self.time_off_counter.get() - 1)
            self.label_time_off_counter.configure(text="%d" % self.time_off_counter.get())
            self.label_reps_counter.configure(text="%d" % self.reps_counter.get())
            self.after(1000, self.time_off_countdown_timer)
        return

    # count down the repetitions
    def rep_countdown(self):
        if self.reps_counter.get() <= 1:
            self.label_status.configure(text="Done!", text_color="green")
            self.reps_counter.set(0)
            self.label_reps_counter.configure(text="%d" % self.reps_counter.get())
            self.end_log_timestamp = dt.now()  # get and format a timestamp
            self.end_log_date_str = self.end_log_timestamp.strftime(self.date_format)
            self.end_log_time_str = self.end_log_timestamp.strftime(self.timestamp_format)
            self.end_log_obj = dt.strptime(self.end_log_time_str, self.timestamp_format)
            total_duration = self.end_log_obj - self.start_log_obj
            total_elapsed_str = str(total_duration)
            print(total_elapsed_str)
            self.f.close()  # close the file
            self.button_start.configure(state="enabled")
            return
        else:
            self.time_on_counter.set(self.entry_time_on.get())
            self.time_off_counter.set(self.entry_time_off.get())
            self.reps_counter.set(self.reps_counter.get() - 1)
            self.label_reps_counter.configure(text="%d" % self.reps_counter.get())
            self.time_on_countdown_timer()
            return

    # log data for selected analog input and output
    def log_input(self):
        log_interval = int(self.rate_ms.get())
        new_timestamp = dt.now()
        new_timestamp_str = new_timestamp.strftime(self.timestamp_format)
        new_timestamp_obj = dt.strptime(new_timestamp_str, self.timestamp_format)
        total_elapsed = new_timestamp_obj - self.start_log_obj
        total_elapsed_str = str(total_elapsed)
        value = ljm.eReadName(self.handle, self.combobox_input.get())  # read AIN#
        self.f.write("%s, %f, %0.3f\n" % (total_elapsed_str, self.valve_state, value))  # write to file
        self.label_input_value.configure(text="%0.3f" % value)  # update GUI
        self.after(log_interval, self.log_input)  # refresh
        return

    # update filename and create file
    def update_config(self):
        # configure filename and filepath variables
        # self.cwd = os.getcwd() + "\\data"
        self.cwd = os.path.dirname(sys.executable) + "\\data"
        self.filename.set(self.entry_filename.get())
        self.filepath = os.path.join(self.cwd, self.filename.get())
        # open the log file
        self.f = open(self.filepath, 'w')

    # closes labjack connection and quits program
    def quit_program(self):
        self.valve_state = 0
        ljm.eWriteName(self.handle, self.output_ID.get(), self.valve_state)
        ljm.close(self.handle)
        self.f.close()
        self.destroy()


if __name__ == "__main__":
    app = FastFID()
    app.mainloop()
