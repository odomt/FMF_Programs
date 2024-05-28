from tkinter import *
import customtkinter
from labjack import ljm

customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"


class TimerApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Timer")
        self.geometry("200x225")
        self.resizable(False, False)

        # setup for LabJack
        self.handle = ljm.openS("T7", "ANY", "ANY")  # Any device, Any connection, Any identifier
        info = ljm.getHandleInfo(self.handle)  # (Device Type, Connection Type, Serial Number)
        print("Opened LabJack: (" + str(info[0]) + ", " + str(info[1]) + ", " + str(info[2]) + ")")
        self.valve_state = 0  # Output state = low (0 = low, 1 = high)
        print("State = " + str(self.valve_state) + " or 'closed'")

        # create frame for GUI
        self.frame_timer = customtkinter.CTkFrame(self)

        # create labels
        self.label_timer_on = customtkinter.CTkLabel(self.frame_timer, text="On Timer:", width=50)
        self.label_timer_off = customtkinter.CTkLabel(self.frame_timer, text="Off Timer:", width=50)
        self.label_reps = customtkinter.CTkLabel(self.frame_timer, text="Reps Left:", width=50)
        self.label_output_ID = customtkinter.CTkLabel(self.frame_timer, text="Valve ID:", width=50)
        self.label_timer_on_counter = customtkinter.CTkLabel(self.frame_timer, text="#", width=50)
        self.label_timer_off_counter = customtkinter.CTkLabel(self.frame_timer, text="#", width=50)
        self.label_reps_counter = customtkinter.CTkLabel(self.frame_timer, text="#", width=50)
        self.label_output = customtkinter.CTkLabel(self.frame_timer, text="#", width=50)
        self.label_status = customtkinter.CTkLabel(self.frame_timer, text="Waiting...", width=50)

        # create variables
        self.time_on = StringVar()  # set on timer
        self.time_off = StringVar()  # set off timer
        self.reps = StringVar()  # set reps
        self.output_ID = StringVar()  # set ID
        self.time_on_counter = IntVar()  # dynamic time on counter
        self.time_off_counter = IntVar()  # dynamic time off counter
        self.reps_counter = IntVar()  # calculated total rep time, including opened and closed valve states

        # assign values to variables
        self.time_on.set("10")  # hard-coded default on timer
        self.time_off.set("5")  # hard-coded default off timer
        self.reps.set("5")  # hard-coded default number of reps
        self.output_ID.set("FIO0")  # hard-coded default LabJack output ID
        print("Valve set to LabJack ID: " + self.output_ID.get())

        # create user input entry fields
        self.entry_timer_on = customtkinter.CTkEntry(self.frame_timer,  # user entry field for on timer
                                                     textvariable=self.time_on, width=50)
        self.entry_timer_off = customtkinter.CTkEntry(self.frame_timer,  # user entry field for off timer
                                                      textvariable=self.time_off, width=50)
        self.entry_reps = customtkinter.CTkEntry(self.frame_timer,  # user entry field for number of reps
                                                 textvariable=self.reps, width=50)
        self.entry_output_ID = customtkinter.CTkEntry(self.frame_timer,  # user entry field for LabJack output ID
                                                      textvariable=self.output_ID, width=50)

        # create buttons
        self.button_start = customtkinter.CTkButton(self.frame_timer, text="Start",  # starts program
                                                    command=lambda: self.timer())

        # widget placements within GUI
        self.frame_timer.pack(padx=5, pady=5, fill="both", expand=True)
        self.label_timer_on.grid(row=0, column=0, padx=(15, 0))
        self.label_timer_on_counter.grid(row=0, column=1)
        self.entry_timer_on.grid(row=0, column=2)
        self.label_timer_off.grid(row=1, column=0, padx=(15, 0))
        self.label_timer_off_counter.grid(row=1, column=1)
        self.entry_timer_off.grid(row=1, column=2)
        self.label_reps.grid(row=2, column=0, padx=(15, 0))
        self.label_reps_counter.grid(row=2, column=1)
        self.entry_reps.grid(row=2, column=2)
        self.label_output_ID.grid(row=3, column=0, padx=(15, 0))
        self.label_output.grid(row=3, column=1)
        self.entry_output_ID.grid(row=3, column=2)
        self.button_start.grid(row=4, column=0, columnspan=3, pady=15, padx=(25, 10))
        self.label_status.grid(row=5, column=0, columnspan=3, padx=(25, 10))

    # function to provide overall rep counter
    def timer(self):
        self.time_on_counter.set(int(self.entry_timer_on.get()))  # binds time on entry field to def value
        self.time_off_counter.set(int(self.entry_timer_off.get()))  # binds time off entry field to def value
        self.reps_counter.set(int(self.entry_reps.get()))  # binds number of reps entry field to def value
        self.output_ID.set(self.entry_output_ID.get())  # binds number of reps entry field to def value
        self.label_status.configure(text="Running", text_color="yellow")
        print(self.output_ID.get() + " valve opening!")
        self.time_on_countdown_timer()

    # function to count down the on timer for each rep
    def time_on_countdown_timer(self):
        self.valve_state = 1
        ljm.eWriteName(self.handle, self.output_ID.get(), self.valve_state)
        self.label_output.configure(text="Open", text_color="green")
        if self.time_on_counter.get() < 1:
            print(self.output_ID.get() + " valve closing!")
            self.time_off_countdown_timer()
        else:
            self.time_on_counter.set(self.time_on_counter.get() - 1)
            print("On Timer:", self.time_on_counter.get())
            self.label_timer_on_counter.configure(text="%d" % self.time_on_counter.get())
            self.label_timer_off_counter.configure(text="%d" % self.time_off_counter.get())
            self.label_reps_counter.configure(text="%d" % self.reps_counter.get())
            self.after(1000, self.time_on_countdown_timer)
        return

    # function to count down the off timer for each rep
    def time_off_countdown_timer(self):
        self.valve_state = 0
        ljm.eWriteName(self.handle, self.output_ID.get(), self.valve_state)
        self.label_output.configure(text="Closed", text_color="red")
        if self.time_off_counter.get() < 1:
            print(self.output_ID.get() + " valve opening!")
            self.rep_countdown()
        else:
            self.time_off_counter.set(self.time_off_counter.get() - 1)
            print("Off Timer:", self.time_off_counter.get())
            self.label_timer_off_counter.configure(text="%d" % self.time_off_counter.get())
            self.label_reps_counter.configure(text="%d" % self.reps_counter.get())
            self.after(1000, self.time_off_countdown_timer)
        return

    # function to count down the repetitions
    def rep_countdown(self):
        if self.reps_counter.get() < 2:
            print("Done!")
            self.label_status.configure(text="Done!", text_color="green")
            self.reps_counter.set(self.reps_counter.get() - 1)
            self.label_reps_counter.configure(text="%d" % self.reps_counter.get())
            # ljm.close(self.handle)
            # self.destroy()
            return
        else:
            self.time_on_counter.set(self.entry_timer_on.get())
            self.time_off_counter.set(self.entry_timer_off.get())
            self.reps_counter.set(self.reps_counter.get() - 1)
            print("Reps Remaining: ", self.reps_counter.get())
            self.label_reps_counter.configure(text="%d" % self.reps_counter.get())
            self.time_on_countdown_timer()
            return


if __name__ == "__main__":
    app = TimerApp()
    app.mainloop()
