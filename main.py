# TODO: connect move function
# TODO: connect emergency stop function
# TODO: connect limits to move function
# TODO: change all ints to doubles/floats? (e.g. limits entries)
# TODO: [CLEANUP] use for loops to make multiple widgets
# TODO: [OPTIONAL] create 'home' sidebar button that moves in order of z, y, x or selected order
# TODO: [OPTIONAL] create 'set as home' sidebar button

import tkinter as tk  # package: allows import and use of tkinter GUI modules
from tkinter import *  # imports all of tkinter's modules
import customtkinter  # package: custom, pre-made theming applied to tkinter's GUI based on Windows 11
import csv  # package: reading and writing to CSV (comma separated values) files
# import warnings  # package: suppresses warnings that do not affect program functions
# from varname import argname, UsingExecWarning  # package: use an argument's name as a reference
import gclib

# suppresses warning from using argname in the move_axis and set_axis functions
# warnings.filterwarnings("ignore", category=UsingExecWarning)

# default themes for the program
customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

mwt_storage_reader = csv.reader(open('mwt_storage.csv', 'r'))
mwt_dict = {}
for mwt_storage_row in mwt_storage_reader:
    k, v = mwt_storage_row
    mwt_dict[k] = v
print(mwt_dict)

galil = gclib.py()


class MoveCarriage(customtkinter.CTk):

    def __init__(self):
        super().__init__()

        global mwt_dict

        try:
            print('gclib version:', galil.GVersion())  # prints installed gclib version
            galil.GOpen('COM2 --baud 19200')  # change to COM port used by carriage
            print(galil.GInfo())  # prints connection information for carriage

        # exception handler if try block of code does not work
        except gclib.GclibError as e:
            print('Unexpected GclibError:', e)

        # run this code if no exceptions are found in try block of code
        else:
            c = galil.GCommand
            c('SHA')  # sets servo motor "A" to x-axis
            c('DPA=' + str(float(mwt_dict['x_actual']) * 40))  # x-axis last stored position
            c('TPA')
            c('FLA=' + str(float(mwt_dict['x_fwd_limit']) * 40))  # x-axis last stored fwd limit
            c('BLA=' + str(float(mwt_dict['x_rev_limit']) * 40))  # x-axis last stored rev limit
            c('SPA=' + mwt_dict['sp_x'])  # x-axis speed, 2000 cts/sec
            c('ACA=' + mwt_dict['ac_x'])  # x-axis acceleration, 1024 cts/sec
            c('DCA=' + mwt_dict['dc_x'])  # x-axis deceleration, 1024 cts/sec
            c('KPA=' + mwt_dict['kp_x'])  # x-axis proportional Kp, 4
            c('KIA=' + mwt_dict['ki_x'])  # x-axis integral Ki, 0.008
            c('KDA=' + mwt_dict['kd_x'])  # x-axis derivative Kd, 500
            c('SHB')  # sets servo motor "B" to y-axis
            c('DPB=' + str(float(mwt_dict['y_actual']) * 40))  # y-axis last stored position
            c('FLB=' + str(float(mwt_dict['y_fwd_limit']) * 40))  # y-axis last stored fwd limit
            c('BLB=' + str(float(mwt_dict['y_rev_limit']) * 40))  # y-axis last stored rev limit
            c('SPB=' + mwt_dict['sp_y'])  # y-axis speed, 1500 cts/sec
            c('ACB=' + mwt_dict['ac_y'])  # y-axis acceleration, 1024 cts/sec
            c('DCB=' + mwt_dict['dc_y'])  # y-axis deceleration, 1024 cts/sec
            c('KPB=' + mwt_dict['kp_y'])  # y-axis proportional Kp, 4
            c('KIB=' + mwt_dict['ki_y'])  # y-axis integral Ki, 0.024
            c('KDB=' + mwt_dict['kd_y'])  # y-axis derivative Kd, 100
            c('SHC')  # sets servo motor "C" to z-axis
            c('DPC=' + str(float(mwt_dict['z_actual']) * 40))  # z-axis last stored position
            c('FLC=' + str(float(mwt_dict['z_fwd_limit']) * 40))  # z-axis last stored fwd limit
            c('BLC=' + str(float(mwt_dict['z_rev_limit']) * 40))  # z-axis last stored rev limit
            c('SPC=' + mwt_dict['sp_z'])  # z-axis speed, 300 cts/sec
            c('ACC=' + mwt_dict['ac_z'])  # z-axis acceleration, 1024 cts/sec
            c('DCC=' + mwt_dict['dc_z'])  # z-axis deceleration, 1024 cts/sec
            c('KPC=' + mwt_dict['kp_z'])  # z-axis proportional Kp, 4
            c('KIC=' + mwt_dict['ki_z'])  # z-axis integral Ki, 0.008
            c('KDC=' + mwt_dict['kd_z'])  # z-axis derivative Kd, 1000

        # - configure gui
        # -- configure window
        self.title("MWT Carriage")
        self.geometry(f"{360}x{900}")
        self.resizable(False, False)

        # -- configure grid layout (1x4)
        self.grid_columnconfigure(0, weight=5)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=7)
        self.grid_rowconfigure(3, weight=1)

        # - top widgets
        # -- create frame for top widgets
        self.frame_top = customtkinter.CTkFrame(self)
        self.frame_top.grid(row=0, column=0, sticky="nsew")

        # -- top labels
        self.label_title = customtkinter.CTkLabel(self.frame_top, text="MWT Carriage Controls",
                                                  font=customtkinter.CTkFont(size=20, weight="bold"))
        self.label_version = customtkinter.CTkLabel(self.frame_top, text="Version 20240201",
                                                    font=customtkinter.CTkFont(size=12, slant="italic"))
        self.label_appearance = customtkinter.CTkLabel(self.frame_top, text="Appearance Mode:", anchor="w")

        # -- top buttons
        self.button_stop = customtkinter.CTkButton(self.frame_top, text="Stop Carriage",
                                                   hover_color="dark red", fg_color="red", command=self.stop_carriage)
        self.button_quit = customtkinter.CTkButton(self.frame_top, text='Quit',
                                                   hover_color="dark red", fg_color="red", command=self.quit_carriage)
        # self.button_restore = customtkinter.CTkButton(self.frame_top, text='Restore Positions',
        #                                               command=self.restore_positions)

        # -- top menus
        self.menu_appearance = customtkinter.CTkOptionMenu(self.frame_top, values=["Light", "Dark", "System"],
                                                           command=self.change_appearance_mode_event)

        # -- program theme default values
        self.menu_appearance.set("System")

        # -- top widget positioning
        self.label_title.grid(row=0, column=0, columnspan=2, padx=(30, 0), pady=(10, 0))
        self.label_version.grid(row=1, column=0, columnspan=2, padx=(30, 0), sticky="n")
        self.label_appearance.grid(row=2, column=1, padx=(11, 0), pady=(0, 0), sticky="s")
        self.button_stop.grid(row=3, column=0, padx=(30, 0), pady=(0, 10))
        self.menu_appearance.grid(row=3, column=1, padx=(11, 0), pady=(0, 5), sticky="n")
        self.button_quit.grid(row=4, column=0, padx=(30, 0), pady=(0, 10))
        # self.button_start.grid(row=2, column=0, padx=20, pady=10)
        # self.button_restore.grid(row=4, column=0, padx=20, pady=10)

        # - CARRIAGE POSITION AND LIMITS CONTROLS
        # -- create frame for carriage position and limits controls
        self.tabview_position = customtkinter.CTkTabview(self)
        self.tabview_position.grid(row=1, column=0, columnspan=2, padx=5, sticky="nsew")

        # - CARRIAGE POSITION CONTROLS
        # -- create frame for carriage position controls
        self.tabview_position.add("Positions")

        # -- controls database values entry defaults
        self.entry_x_target_stored = tk.DoubleVar()
        self.entry_x_target_stored.set(0.0)
        self.entry_y_target_stored = tk.DoubleVar()
        self.entry_y_target_stored.set(0.0)
        self.entry_z_target_stored = tk.DoubleVar()
        self.entry_z_target_stored.set(0.0)
        self.x_actual_stored = tk.DoubleVar()
        self.x_actual_stored.set(mwt_dict['x_actual'])
        self.y_actual_stored = tk.DoubleVar()
        self.y_actual_stored.set(mwt_dict['y_actual'])
        self.z_actual_stored = tk.DoubleVar()
        self.z_actual_stored.set(mwt_dict['z_actual'])

        # -- controls labels
        self.label_carriage_position = customtkinter.CTkLabel(self.tabview_position.tab("Positions"),
                                                              text="Carriage Position", anchor="center",
                                                              font=customtkinter.CTkFont(size=16, weight="bold"))
        self.label_target = customtkinter.CTkLabel(self.tabview_position.tab("Positions"), text="Target",
                                                   anchor="center")
        self.label_actual = customtkinter.CTkLabel(self.tabview_position.tab("Positions"), text="Actual",
                                                   anchor="center")
        self.label_x = customtkinter.CTkLabel(self.tabview_position.tab("Positions"), text="X", anchor="w")
        self.label_y = customtkinter.CTkLabel(self.tabview_position.tab("Positions"), text="Y", anchor="w")
        self.label_z = customtkinter.CTkLabel(self.tabview_position.tab("Positions"), text="Z", anchor="w")
        self.label_x_actual = customtkinter.CTkLabel(self.tabview_position.tab("Positions"),
                                                     text=(str(self.x_actual_stored.get())))
        self.label_y_actual = customtkinter.CTkLabel(self.tabview_position.tab("Positions"),
                                                     text=(str(self.y_actual_stored.get())))
        self.label_z_actual = customtkinter.CTkLabel(self.tabview_position.tab("Positions"),
                                                     text=(str(self.z_actual_stored.get())))

        # -- controls entry fields
        self.entry_x_target = customtkinter.CTkEntry(self.tabview_position.tab("Positions"), width=70,
                                                     textvariable=self.entry_x_target_stored)
        self.entry_x_target.configure(justify="center")
        # self.entry_x_target.bind("<Return>", lambda _: self.move_axis(self.entry_x_target_stored,
        #                                                               self.entry_x_limit_fwd_stored,
        #                                                               self.entry_x_limit_rev_stored))
        self.entry_y_target = customtkinter.CTkEntry(self.tabview_position.tab("Positions"), width=70,
                                                     textvariable=self.entry_y_target_stored)
        self.entry_y_target.configure(justify="center")
        # self.entry_y_target.bind("<Return>", lambda _: self.move_axis(self.entry_y_target_stored,
        #                                                               self.entry_y_limit_fwd_stored,
        #                                                               self.entry_y_limit_rev_stored))
        self.entry_z_target = customtkinter.CTkEntry(self.tabview_position.tab("Positions"), width=70,
                                                     textvariable=self.entry_z_target_stored)
        self.entry_z_target.configure(justify="center")
        # self.entry_z_target.bind("<Return>", lambda _: self.move_axis(self.entry_z_target_stored,
        #                                                               self.entry_z_limit_fwd_stored,
        #                                                               self.entry_z_limit_rev_stored))

        # -- controls buttons
        self.button_move_x = customtkinter.CTkButton(self.tabview_position.tab("Positions"), text='Move',
                                                     hover_color="dark green", fg_color="forest green", border_width=2,
                                                     width=70, text_color=("gray10", "#DCE4EE"),
                                                     command=lambda: self.move_axis("X", self.entry_x_target.get(),
                                                                                    self.entry_x_limit_fwd_stored,
                                                                                    self.entry_x_limit_rev_stored))
        self.button_set_x = customtkinter.CTkButton(self.tabview_position.tab("Positions"), text='Set Axis',
                                                    fg_color="transparent", border_width=2, width=70,
                                                    text_color=("gray10", "#DCE4EE"),
                                                    command=lambda: self.set_axis("X", self.entry_x_target.get()))
        self.button_move_y = customtkinter.CTkButton(self.tabview_position.tab("Positions"), text='Move',
                                                     hover_color="dark green", fg_color="forest green", border_width=2,
                                                     width=70, text_color=("gray10", "#DCE4EE"),
                                                     command=lambda: self.move_axis("Y", self.entry_y_target.get(),
                                                                                    self.entry_y_limit_fwd_stored,
                                                                                    self.entry_y_limit_rev_stored))
        self.button_set_y = customtkinter.CTkButton(self.tabview_position.tab("Positions"), text='Set Axis',
                                                    fg_color="transparent", border_width=2, width=70,
                                                    text_color=("gray10", "#DCE4EE"),
                                                    command=lambda: self.set_axis("Y", self.entry_y_target.get()))
        self.button_move_z = customtkinter.CTkButton(self.tabview_position.tab("Positions"), text='Move',
                                                     hover_color="dark green", fg_color="forest green", border_width=2,
                                                     width=70, text_color=("gray10", "#DCE4EE"),
                                                     command=lambda: self.move_axis("Z", self.entry_z_target.get(),
                                                                                    self.entry_z_limit_fwd_stored,
                                                                                    self.entry_z_limit_rev_stored))
        self.button_set_z = customtkinter.CTkButton(self.tabview_position.tab("Positions"), text='Set Axis',
                                                    fg_color="transparent", border_width=2, width=70,
                                                    text_color=("gray10", "#DCE4EE"),
                                                    command=lambda: self.set_axis("Z", self.entry_z_target.get()))

        # -- controls widgets positioning
        self.label_carriage_position.grid(row=0, column=0, columnspan=5, pady=(10, 0), sticky="nsew")
        self.label_target.grid(row=1, column=1, padx=(10, 0), pady=(5, 0), sticky="nsew")
        self.label_actual.grid(row=1, column=2, padx=(10, 0), pady=(5, 0), sticky="nsew")
        self.label_x.grid(row=2, column=0, padx=(15, 0), pady=(5, 0), sticky="nsew")
        self.label_y.grid(row=3, column=0, padx=(15, 0), pady=(10, 0), sticky="nsew")
        self.label_z.grid(row=4, column=0, padx=(15, 0), pady=(10, 5), sticky="nsew")
        self.entry_x_target.grid(row=2, column=1, padx=(5, 0), pady=(5, 0), sticky="nsew")
        self.label_x_actual.grid(row=2, column=2, padx=(20, 5), pady=(5, 0), sticky="nsew")
        self.entry_y_target.grid(row=3, column=1, padx=(5, 0), pady=(10, 0), sticky="nsew")
        self.label_y_actual.grid(row=3, column=2, padx=(20, 5), pady=(10, 0), sticky="nsew")
        self.entry_z_target.grid(row=4, column=1, padx=(5, 0), pady=(10, 5), sticky="nsew")
        self.label_z_actual.grid(row=4, column=2, padx=(20, 5), pady=(10, 5), sticky="nsew")
        self.button_move_x.grid(row=2, column=3, padx=(10, 0), pady=(5, 0), sticky="nsew")
        self.button_set_x.grid(row=2, column=4, padx=(10, 10), pady=(5, 0), sticky="nsew")
        self.button_move_y.grid(row=3, column=3, padx=(10, 0), pady=(10, 0), sticky="nsew")
        self.button_set_y.grid(row=3, column=4, padx=(10, 10), pady=(10, 0), sticky="nsew")
        self.button_move_z.grid(row=4, column=3, padx=(10, 0), pady=(10, 5), sticky="nsew")
        self.button_set_z.grid(row=4, column=4, padx=(10, 10), pady=(10, 5), sticky="nsew")

        # - SOFTWARE LIMITS CONTROLS
        # -- create frame for software limits
        self.tabview_position.add("Limits")

        # -- limits database values entry defaults
        self.entry_x_limit_fwd_stored = tk.IntVar()
        self.entry_x_limit_fwd_stored.set(mwt_dict['x_fwd_limit'])
        self.entry_x_limit_rev_stored = tk.IntVar()
        self.entry_x_limit_rev_stored.set(mwt_dict['x_rev_limit'])
        self.entry_y_limit_fwd_stored = tk.IntVar()
        self.entry_y_limit_fwd_stored.set(mwt_dict['y_fwd_limit'])
        self.entry_y_limit_rev_stored = tk.IntVar()
        self.entry_y_limit_rev_stored.set(mwt_dict['y_rev_limit'])
        self.entry_z_limit_fwd_stored = tk.IntVar()
        self.entry_z_limit_fwd_stored.set(mwt_dict['z_fwd_limit'])
        self.entry_z_limit_rev_stored = tk.IntVar()
        self.entry_z_limit_rev_stored.set(mwt_dict['z_rev_limit'])
        self.checkbox_unlock_limits_status = IntVar()

        # -- limits labels
        self.label_software_limits = customtkinter.CTkLabel(self.tabview_position.tab("Limits"), text="Software Limits",
                                                            anchor="center",
                                                            font=customtkinter.CTkFont(size=16, weight="bold"))
        self.label_forward = customtkinter.CTkLabel(self.tabview_position.tab("Limits"), text="Forward",
                                                    anchor="center")
        self.label_reverse = customtkinter.CTkLabel(self.tabview_position.tab("Limits"), text="Reverse",
                                                    anchor="center")
        self.label_x_limits = customtkinter.CTkLabel(self.tabview_position.tab("Limits"), text="X", anchor="center")
        self.label_y_limits = customtkinter.CTkLabel(self.tabview_position.tab("Limits"), text="Y", anchor="center")
        self.label_z_limits = customtkinter.CTkLabel(self.tabview_position.tab("Limits"), text="Z", anchor="center")

        # -- limits entry fields
        self.entry_x_limit_fwd = customtkinter.CTkEntry(self.tabview_position.tab("Limits"), width=70,
                                                        textvariable=self.entry_x_limit_fwd_stored)
        self.entry_x_limit_fwd.configure(justify="center")
        self.entry_x_limit_rev = customtkinter.CTkEntry(self.tabview_position.tab("Limits"), width=70,
                                                        textvariable=self.entry_x_limit_rev_stored)
        self.entry_x_limit_rev.configure(justify="center")
        self.entry_y_limit_fwd = customtkinter.CTkEntry(self.tabview_position.tab("Limits"), width=70,
                                                        textvariable=self.entry_y_limit_fwd_stored)
        self.entry_y_limit_fwd.configure(justify="center")
        self.entry_y_limit_rev = customtkinter.CTkEntry(self.tabview_position.tab("Limits"), width=70,
                                                        textvariable=self.entry_y_limit_rev_stored)
        self.entry_y_limit_rev.configure(justify="center")
        self.entry_z_limit_fwd = customtkinter.CTkEntry(self.tabview_position.tab("Limits"), width=70,
                                                        textvariable=self.entry_z_limit_fwd_stored)
        self.entry_z_limit_fwd.configure(justify="center")
        self.entry_z_limit_rev = customtkinter.CTkEntry(self.tabview_position.tab("Limits"), width=70,
                                                        textvariable=self.entry_z_limit_rev_stored)
        self.entry_z_limit_rev.configure(justify="center")

        # -- limits buttons and checkbox
        self.checkbox_unlock_limits = customtkinter.CTkCheckBox(self.tabview_position.tab("Limits"), text="", onvalue=1,
                                                                offvalue=0, variable=self.checkbox_unlock_limits_status,
                                                                command=self.enable_button_set_limits)
        self.button_set_limits = customtkinter.CTkButton(self.tabview_position.tab("Limits"), text='Set All Limits',
                                                         fg_color="transparent", border_width=2, width=90,
                                                         text_color=("gray10", "#DCE4EE"), state="disabled",
                                                         command=self.set_limits)
        self.button_recall_limits = customtkinter.CTkButton(self.tabview_position.tab("Limits"), text='Recall Limits',
                                                            fg_color="transparent", border_width=2, width=20,
                                                            text_color=("gray10", "#DCE4EE"),
                                                            command=self.recall_limits)

        # -- limits widgets positioning
        self.label_software_limits.grid(row=0, column=0, columnspan=4, padx=(20, 0), pady=(10, 0), sticky="nsew")
        self.label_forward.grid(row=1, column=1, padx=(10, 0), pady=(5, 0), sticky="nsew")
        self.label_reverse.grid(row=1, column=2, padx=(5, 0), pady=(5, 0), sticky="nsew")
        self.label_x_limits.grid(row=2, column=0, padx=(20, 0), pady=(5, 0), sticky="nsew")
        self.label_y_limits.grid(row=3, column=0, padx=(20, 0), pady=(5, 0), sticky="nsew")
        self.label_z_limits.grid(row=4, column=0, padx=(20, 0), pady=(5, 5), sticky="nsew")
        self.entry_x_limit_fwd.grid(row=2, column=1, padx=(5, 0), pady=(5, 0), sticky="nsew")
        self.entry_x_limit_rev.grid(row=2, column=2, padx=(10, 0), pady=(5, 0), sticky="nsew")
        self.entry_y_limit_fwd.grid(row=3, column=1, padx=(5, 0), pady=(10, 0), sticky="nsew")
        self.entry_y_limit_rev.grid(row=3, column=2, padx=(10, 0), pady=(10, 0), sticky="nsew")
        self.entry_z_limit_fwd.grid(row=4, column=1, padx=(5, 0), pady=(10, 5), sticky="nsew")
        self.entry_z_limit_rev.grid(row=4, column=2, padx=(10, 0), pady=(10, 5), sticky="nsew")
        self.checkbox_unlock_limits.grid(row=2, column=3, padx=(10, 0), pady=(5, 0), sticky="w")
        self.button_set_limits.grid(row=2, column=3, padx=(40, 0), pady=(5, 0), sticky="e")
        self.button_recall_limits.grid(row=3, column=3, columnspan=2, padx=(10, 0), pady=(10, 0), sticky="nsew")

        # CARRIAGE STATUS CODES AND PROGRAM LOG EVENTS
        # -- create frame for status codes and program log events
        self.tabview_config = customtkinter.CTkTabview(self)
        self.tabview_config.grid(row=2, column=0, padx=5, sticky="nsew")

        # - CARRIAGE STATUS CODES
        # -- create tab/frame for status codes
        self.tabview_config.add("Status")

        # -- status codes database values entry defaults
        self.entry_x_status_code_stored = tk.IntVar()
        self.entry_x_status_code_stored.set(mwt_dict['x_stop_code'])
        self.entry_y_status_code_stored = tk.IntVar()
        self.entry_y_status_code_stored.set(mwt_dict['y_stop_code'])
        self.entry_z_status_code_stored = tk.IntVar()
        self.entry_z_status_code_stored.set(mwt_dict['z_stop_code'])

        # -- status codes labels
        self.label_status_title = customtkinter.CTkLabel(self.tabview_config.tab("Status"), text="Status",
                                                         anchor="center",
                                                         font=customtkinter.CTkFont(size=16, weight="bold"))
        self.label_status_codes = customtkinter.CTkLabel(self.tabview_config.tab("Status"),
                                                         text=(mwt_dict['x_stop_code'] + ", " + mwt_dict['y_stop_code']
                                                               + ", " + mwt_dict['z_stop_code']),
                                                         anchor="center", font=customtkinter.CTkFont(size=14))
        self.label_status_terms = customtkinter.CTkLabel(self.tabview_config.tab("Status"),
                                                         text="0 - motors are running\n1 - motors stopped at "
                                                              "commanded position\n7 - motors stopped after abort "
                                                              "command")

        # -- status codes widgets positioning
        self.label_status_title.grid(row=0, column=0, padx=(40, 0), pady=(10, 0), sticky="nsew")
        self.label_status_codes.grid(row=1, column=0, padx=(40, 0), pady=(10, 0), sticky="nsew")
        self.label_status_terms.grid(row=2, column=0, padx=(40, 0), pady=(10, 0), sticky="n")

        # - PROGRAM LOG EVENTS
        # -- create tab/frame for program log events
        self.tabview_config.add("Log")

        # -- log events label fields
        self.label_log = customtkinter.CTkLabel(self.tabview_config.tab("Log"), text="Event Log",
                                                anchor="center",
                                                font=customtkinter.CTkFont(size=16, weight="bold"))

        # -- log events text fields
        self.textbox_log = customtkinter.CTkTextbox(self.tabview_config.tab("Log"), width=250, height=75)

        # -- log events button
        self.button_clear_log = customtkinter.CTkButton(self.tabview_config.tab("Log"), text='Clear',
                                                        fg_color="transparent", border_width=2, width=90,
                                                        text_color=("gray10", "#DCE4EE"), command=self.clear_log)

        # -- log events widgets positioning
        self.label_log.grid(row=0, column=0, padx=(45, 0), pady=(10, 0), sticky="nsew")
        self.button_clear_log.grid(row=1, column=0, padx=(45, 0), pady=(10, 0), sticky="nsew")
        self.textbox_log.grid(row=2, column=0, padx=(45, 0), pady=(10, 0), sticky="nsew")

        # CARRIAGE ATTRIBUTES
        # - create frame for carriage attributes
        self.tabview_movement = customtkinter.CTkTabview(self)
        self.tabview_movement.grid(row=3, column=0, columnspan=2, padx=5, pady=(0, 5), sticky="nsew")

        # - CARRIAGE ATTRIBUTES (SP, AC, DC)
        # -- create tab/frame for attribute controls (SP: speed, AC: acceleration, DC: deceleration)
        self.tabview_movement.add("SP, AC, DC")

        # -- attribute entry defaults (SP, AC, DC)
        self.entry_speed_x_stored = tk.IntVar()
        self.entry_speed_x_stored.set(mwt_dict['sp_x'])
        self.entry_speed_y_stored = tk.IntVar()
        self.entry_speed_y_stored.set(mwt_dict['sp_y'])
        self.entry_speed_z_stored = tk.IntVar()
        self.entry_speed_z_stored.set(mwt_dict['sp_z'])
        self.entry_accel_x_stored = tk.IntVar()
        self.entry_accel_x_stored.set(mwt_dict['ac_x'])
        self.entry_accel_y_stored = tk.IntVar()
        self.entry_accel_y_stored.set(mwt_dict['ac_y'])
        self.entry_accel_z_stored = tk.IntVar()
        self.entry_accel_z_stored.set(mwt_dict['ac_z'])
        self.entry_decel_x_stored = tk.IntVar()
        self.entry_decel_x_stored.set(mwt_dict['dc_x'])
        self.entry_decel_y_stored = tk.IntVar()
        self.entry_decel_y_stored.set(mwt_dict['dc_y'])
        self.entry_decel_z_stored = tk.IntVar()
        self.entry_decel_z_stored.set(mwt_dict['dc_z'])
        self.checkbox_unlock_SAD_status = IntVar()

        # -- attribute labels (SP, AC, DC)
        self.label_sp_ac_dc = customtkinter.CTkLabel(self.tabview_movement.tab("SP, AC, DC"),
                                                     text="Speed, Acceleration, Deceleration", anchor="center",
                                                     font=customtkinter.CTkFont(size=16, weight="bold"))
        self.label_speed = customtkinter.CTkLabel(self.tabview_movement.tab("SP, AC, DC"), text="SP", anchor="center")
        self.label_accel = customtkinter.CTkLabel(self.tabview_movement.tab("SP, AC, DC"), text="AC", anchor="center")
        self.label_decel = customtkinter.CTkLabel(self.tabview_movement.tab("SP, AC, DC"), text="DC", anchor="center")
        self.label_SAD_x = customtkinter.CTkLabel(self.tabview_movement.tab("SP, AC, DC"), text="X", anchor="center")
        self.label_SAD_y = customtkinter.CTkLabel(self.tabview_movement.tab("SP, AC, DC"), text="Y", anchor="center")
        self.label_SAD_z = customtkinter.CTkLabel(self.tabview_movement.tab("SP, AC, DC"), text="Z", anchor="center")

        # -- attribute entry fields (SP, AC, DC)
        self.entry_speed_x = customtkinter.CTkEntry(self.tabview_movement.tab("SP, AC, DC"), width=50,
                                                    textvariable=self.entry_speed_x_stored)
        self.entry_speed_x.configure(justify="center")
        self.entry_speed_y = customtkinter.CTkEntry(self.tabview_movement.tab("SP, AC, DC"), width=50,
                                                    textvariable=self.entry_speed_y_stored)
        self.entry_speed_y.configure(justify="center")
        self.entry_speed_z = customtkinter.CTkEntry(self.tabview_movement.tab("SP, AC, DC"), width=50,
                                                    textvariable=self.entry_speed_z_stored)
        self.entry_speed_z.configure(justify="center")
        self.entry_accel_x = customtkinter.CTkEntry(self.tabview_movement.tab("SP, AC, DC"), width=50,
                                                    textvariable=self.entry_accel_x_stored)
        self.entry_accel_x.configure(justify="center")
        self.entry_accel_y = customtkinter.CTkEntry(self.tabview_movement.tab("SP, AC, DC"), width=50,
                                                    textvariable=self.entry_accel_y_stored)
        self.entry_accel_y.configure(justify="center")
        self.entry_accel_z = customtkinter.CTkEntry(self.tabview_movement.tab("SP, AC, DC"), width=50,
                                                    textvariable=self.entry_accel_z_stored)
        self.entry_accel_z.configure(justify="center")
        self.entry_decel_x = customtkinter.CTkEntry(self.tabview_movement.tab("SP, AC, DC"), width=50,
                                                    textvariable=self.entry_decel_x_stored)
        self.entry_decel_x.configure(justify="center")
        self.entry_decel_y = customtkinter.CTkEntry(self.tabview_movement.tab("SP, AC, DC"), width=50,
                                                    textvariable=self.entry_decel_y_stored)
        self.entry_decel_y.configure(justify="center")
        self.entry_decel_z = customtkinter.CTkEntry(self.tabview_movement.tab("SP, AC, DC"), width=50,
                                                    textvariable=self.entry_decel_z_stored)
        self.entry_decel_z.configure(justify="center")

        # -- attribute buttons and checkboxes (SP, AC, DC)
        self.checkbox_unlock_SAD = customtkinter.CTkCheckBox(self.tabview_movement.tab("SP, AC, DC"), text="",
                                                             onvalue=1, offvalue=0,
                                                             variable=self.checkbox_unlock_SAD_status,
                                                             command=self.enable_button_set_SAD)
        self.button_set_SAD = customtkinter.CTkButton(self.tabview_movement.tab("SP, AC, DC"), text='Set All',
                                                      fg_color="transparent", border_width=2, width=10,
                                                      text_color=("gray10", "#DCE4EE"), state="disabled",
                                                      command=self.set_SAD)
        self.button_recall_SAD = customtkinter.CTkButton(self.tabview_movement.tab("SP, AC, DC"), text='Recall',
                                                         fg_color="transparent", border_width=2, width=20,
                                                         text_color=("gray10", "#DCE4EE"),
                                                         command=self.recall_SAD)

        # -- attribute widgets positioning (SP, AC, DC)
        self.label_sp_ac_dc.grid(row=0, column=0, columnspan=6, padx=(10, 0), pady=(10, 0), sticky="nsew")
        self.label_speed.grid(row=1, column=1, padx=(0, 0), pady=(10, 0), sticky="s")
        self.label_accel.grid(row=1, column=2, padx=0, pady=(10, 0), sticky="s")
        self.label_decel.grid(row=1, column=3, padx=0, pady=(10, 0), sticky="s")
        self.label_SAD_x.grid(row=2, column=0, padx=(25, 0), pady=(5, 0), sticky="e")
        self.label_SAD_y.grid(row=3, column=0, padx=(25, 0), pady=(10, 0), sticky="e")
        self.label_SAD_z.grid(row=4, column=0, padx=(25, 0), pady=(10, 0), sticky="e")
        self.entry_speed_x.grid(row=2, column=1, padx=5, pady=(5, 0), sticky="nsew")
        self.entry_accel_x.grid(row=2, column=2, padx=5, pady=(5, 0), sticky="nsew")
        self.entry_decel_x.grid(row=2, column=3, padx=(5, 10), pady=(5, 0), sticky="nsew")
        self.entry_speed_y.grid(row=3, column=1, padx=5, pady=(10, 0), sticky="nsew")
        self.entry_accel_y.grid(row=3, column=2, padx=5, pady=(10, 0), sticky="nsew")
        self.entry_decel_y.grid(row=3, column=3, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.entry_speed_z.grid(row=4, column=1, padx=5, pady=(10, 0), sticky="nsew")
        self.entry_accel_z.grid(row=4, column=2, padx=5, pady=(10, 0), sticky="nsew")
        self.entry_decel_z.grid(row=4, column=3, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.checkbox_unlock_SAD.grid(row=2, column=4, padx=(10, 0), pady=(5, 0), sticky="w")
        self.button_set_SAD.grid(row=2, column=4, padx=(0, 20), pady=(5, 0), sticky="e")
        self.button_recall_SAD.grid(row=3, column=4, columnspan=2, padx=(10, 20), pady=(10, 0), sticky="nsew")

        # - CARRIAGE ATTRIBUTES (KP, KI, KD)
        # -- create tab/frame for attribute controls (KP: proportional, KI: integral, KD: derivative)
        self.tabview_movement.add("KP, KI, KD")

        # -- attribute entry defaults (KP, KI, KD)
        self.entry_kp_x_stored = tk.IntVar()
        self.entry_kp_x_stored.set(mwt_dict['kp_x'])
        self.entry_kp_y_stored = tk.IntVar()
        self.entry_kp_y_stored.set(mwt_dict['kp_y'])
        self.entry_kp_z_stored = tk.IntVar()
        self.entry_kp_z_stored.set(mwt_dict['kp_z'])
        self.entry_ki_x_stored = tk.DoubleVar()
        self.entry_ki_x_stored.set(mwt_dict['ki_x'])
        self.entry_ki_y_stored = tk.DoubleVar()
        self.entry_ki_y_stored.set(mwt_dict['ki_y'])
        self.entry_ki_z_stored = tk.DoubleVar()
        self.entry_ki_z_stored.set(mwt_dict['ki_z'])
        self.entry_kd_x_stored = tk.IntVar()
        self.entry_kd_x_stored.set(mwt_dict['kd_x'])
        self.entry_kd_y_stored = tk.IntVar()
        self.entry_kd_y_stored.set(mwt_dict['kd_y'])
        self.entry_kd_z_stored = tk.IntVar()
        self.entry_kd_z_stored.set(mwt_dict['kd_z'])
        self.checkbox_unlock_PID_status = IntVar()

        # -- attribute labels (KP, KI, KD)
        self.label_kp_ki_kd = customtkinter.CTkLabel(self.tabview_movement.tab("KP, KI, KD"), anchor="center",
                                                     text="Proportional, Integral, Derivative",
                                                     font=customtkinter.CTkFont(size=16, weight="bold"))
        self.label_kp = customtkinter.CTkLabel(self.tabview_movement.tab("KP, KI, KD"), text="KP", anchor="center")
        self.label_ki = customtkinter.CTkLabel(self.tabview_movement.tab("KP, KI, KD"), text="KI", anchor="center")
        self.label_kd = customtkinter.CTkLabel(self.tabview_movement.tab("KP, KI, KD"), text="KD", anchor="center")
        self.label_PID_x = customtkinter.CTkLabel(self.tabview_movement.tab("KP, KI, KD"), text="X", anchor="center")
        self.label_PID_y = customtkinter.CTkLabel(self.tabview_movement.tab("KP, KI, KD"), text="Y", anchor="center")
        self.label_PID_z = customtkinter.CTkLabel(self.tabview_movement.tab("KP, KI, KD"), text="Z", anchor="center")

        # -- attribute entry fields (KP, KI, KD)
        self.entry_kp_x = customtkinter.CTkEntry(self.tabview_movement.tab("KP, KI, KD"), width=50,
                                                 textvariable=self.entry_kp_x_stored)
        self.entry_kp_x.configure(justify="center")
        self.entry_kp_y = customtkinter.CTkEntry(self.tabview_movement.tab("KP, KI, KD"), width=50,
                                                 textvariable=self.entry_kp_y_stored)
        self.entry_kp_y.configure(justify="center")
        self.entry_kp_z = customtkinter.CTkEntry(self.tabview_movement.tab("KP, KI, KD"), width=50,
                                                 textvariable=self.entry_kp_z_stored)
        self.entry_kp_z.configure(justify="center")
        self.entry_ki_x = customtkinter.CTkEntry(self.tabview_movement.tab("KP, KI, KD"), width=50,
                                                 textvariable=self.entry_ki_x_stored)
        self.entry_ki_x.configure(justify="center")
        self.entry_ki_y = customtkinter.CTkEntry(self.tabview_movement.tab("KP, KI, KD"), width=50,
                                                 textvariable=self.entry_ki_y_stored)
        self.entry_ki_y.configure(justify="center")
        self.entry_ki_z = customtkinter.CTkEntry(self.tabview_movement.tab("KP, KI, KD"), width=50,
                                                 textvariable=self.entry_ki_z_stored)
        self.entry_ki_z.configure(justify="center")
        self.entry_kd_x = customtkinter.CTkEntry(self.tabview_movement.tab("KP, KI, KD"), width=50,
                                                 textvariable=self.entry_kd_x_stored)
        self.entry_kd_x.configure(justify="center")
        self.entry_kd_y = customtkinter.CTkEntry(self.tabview_movement.tab("KP, KI, KD"), width=50,
                                                 textvariable=self.entry_kd_y_stored)
        self.entry_kd_y.configure(justify="center")
        self.entry_kd_z = customtkinter.CTkEntry(self.tabview_movement.tab("KP, KI, KD"), width=50,
                                                 textvariable=self.entry_kd_z_stored)
        self.entry_kd_z.configure(justify="center")

        # -- attribute buttons (KP, KI, KD)
        self.checkbox_unlock_PID = customtkinter.CTkCheckBox(self.tabview_movement.tab("KP, KI, KD"), text="",
                                                             onvalue=1, offvalue=0,
                                                             variable=self.checkbox_unlock_PID_status,
                                                             command=self.enable_button_set_PID)
        self.button_set_PID = customtkinter.CTkButton(self.tabview_movement.tab("KP, KI, KD"), text='Set All',
                                                      fg_color="transparent", border_width=2, width=10,
                                                      text_color=("gray10", "#DCE4EE"), state="disabled",
                                                      command=self.set_PID)
        self.button_recall_PID = customtkinter.CTkButton(self.tabview_movement.tab("KP, KI, KD"), text='Recall',
                                                         fg_color="transparent", border_width=2, width=20,
                                                         text_color=("gray10", "#DCE4EE"),
                                                         command=self.recall_PID)

        # -- attribute widgets positioning (KP, KI, KD)
        self.label_kp_ki_kd.grid(row=0, column=0, columnspan=6, padx=(5, 0), pady=(10, 0), sticky="nsew")
        self.label_kp.grid(row=1, column=1, padx=(0, 0), pady=(10, 0), sticky="s")
        self.label_ki.grid(row=1, column=2, padx=0, pady=(10, 0), sticky="s")
        self.label_kd.grid(row=1, column=3, padx=0, pady=(10, 0), sticky="s")
        self.label_PID_x.grid(row=2, column=0, padx=(25, 0), pady=(5, 0), sticky="e")
        self.label_PID_y.grid(row=3, column=0, padx=(25, 0), pady=(10, 0), sticky="e")
        self.label_PID_z.grid(row=4, column=0, padx=(25, 0), pady=(10, 0), sticky="e")
        self.entry_kp_x.grid(row=2, column=1, padx=5, pady=(5, 0), sticky="nsew")
        self.entry_ki_x.grid(row=2, column=2, padx=5, pady=(5, 0), sticky="nsew")
        self.entry_kd_x.grid(row=2, column=3, padx=(5, 10), pady=(5, 0), sticky="nsew")
        self.entry_kp_y.grid(row=3, column=1, padx=5, pady=(10, 0), sticky="nsew")
        self.entry_ki_y.grid(row=3, column=2, padx=5, pady=(10, 0), sticky="nsew")
        self.entry_kd_y.grid(row=3, column=3, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.entry_kp_z.grid(row=4, column=1, padx=5, pady=(10, 0), sticky="nsew")
        self.entry_ki_z.grid(row=4, column=2, padx=5, pady=(10, 0), sticky="nsew")
        self.entry_kd_z.grid(row=4, column=3, padx=(5, 10), pady=(10, 0), sticky="nsew")
        self.checkbox_unlock_PID.grid(row=2, column=4, padx=(10, 0), pady=(5, 0), sticky="w")
        self.button_set_PID.grid(row=2, column=4, padx=(0, 20), pady=(5, 0), sticky="e")
        self.button_recall_PID.grid(row=3, column=4, columnspan=2, padx=(10, 20), pady=(10, 0), sticky="nsew")

    # - GUI functions
    # -- change overall appearance of program to light, dark, or system
    @staticmethod
    def change_appearance_mode_event(new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    # - carriage functions
    # -- stop carriage move execution and freeze actual position values
    def stop_carriage(self):
        c = galil.GCommand
        c('AB')
        del c
        self.print_to_log("Carriage stopped!")

    # -- close carriage connection and exit program window
    def quit_carriage(self):
        print("Connection closing, goodbye!")
        galil.GClose()
        self.destroy()

    # -- updates stop codes from carriage
    # noinspection PyTypeChecker
    def update_stop_codes(self):
        global mwt_dict
        c = galil.GCommand
        x_sc = c('SCA')
        y_sc = c('SCB')
        z_sc = c('SCC')
        self.entry_x_status_code_stored.set(x_sc)
        self.entry_y_status_code_stored.set(y_sc)
        self.entry_z_status_code_stored.set(z_sc)
        self.label_status_codes.configure(mwt_dict['x_stop_code'] + ", " + mwt_dict['y_stop_code'] + ", " +
                                          mwt_dict['z_stop_code'])
        del c
        self.csv_generate()

    # -- ends move command
    @staticmethod
    def motion_complete(axis):
        galil.GMotionComplete(axis)

    # -- updates positions from carriage
    def update_position(self, axis, target):
        c = galil.GCommand
        x_pos = float(self.label_x_actual.cget("text"))
        y_pos = float(self.label_y_actual.cget("text"))
        z_pos = float(self.label_z_actual.cget("text"))
        self.update_stop_codes()
        if axis == "X":
            if (abs(x_pos - float(target))) < 1:
                self.after(5000, self.motion_complete)
                self.motion_complete(axis)
            else:
                x_pos = c('TPA')
                self.label_x_actual.configure(x_pos)
                self.after(100, self.update_position("X", target))
        elif axis == "Y":
            if (abs(y_pos - float(target))) < 1:
                self.after(5000, self.motion_complete)
                self.motion_complete(axis)
            else:
                y_pos = c('TPB')
                self.label_y_actual.configure(y_pos)
                self.after(100, self.update_position("Y", target))
        elif axis == "Z":
            if (abs(z_pos - float(target))) < 1:
                self.after(5000, self.motion_complete)
                self.motion_complete(axis)
            else:
                z_pos = c('TPC')
                self.label_z_actual.configure(z_pos)
                self.after(100, self.update_position("Z", target))
        x_pos = c('TPA')
        y_pos = c('TPB')
        z_pos = c('TPC')
        self.update_stop_codes()
        self.label_x_actual.configure(x_pos)
        self.label_y_actual.configure(y_pos)
        self.label_z_actual.configure(z_pos)
        del c
        # return x_pos, y_pos, z_pos

    # -- move carriage to input position for axis
    def move_axis(self, axis, move_target, axis_limit_fwd, axis_limit_rev):
        app.bind_all("<1>", lambda event: event.widget.focus_set())
        move_encoder = str(float(move_target) * 40)
        c = galil.GCommand
        if (float(axis_limit_rev.get()) > float(move_target) or
                float(move_target) > float(axis_limit_fwd.get())):
            self.print_to_log("Move is beyond limits!")
        elif axis == "X":
            self.entry_x_target_stored.set(float(move_target))
            self.label_x_actual.configure(move_target)
            c('PAA=' + str(move_encoder))
            c('BGA')
            self.after(100, self.motion_complete("X"))
            self.after(100, self.entry_x_target_stored.set(float(move_target)))
            # self.update_position("X", move_target)
        elif axis == "Y":
            self.entry_y_target_stored.set(float(move_target))
            self.label_y_actual.configure(move_target)
            c('PAB=' + str(move_encoder))
            c('BGB')
            self.after(100, self.motion_complete("Y"))
            # self.update_position("Y", move_target)
        elif axis == "Z":
            self.entry_z_target_stored.set(float(move_target))
            self.label_z_actual.configure(move_target)
            c('PAC=' + str(move_encoder))
            c('BGC')
            self.after(100, self.motion_complete("Z"))
            # self.update_position("Z", move_target)
        else:
            self.print_to_log("Moving error!")
        del c

    # -- set axis position target value to actual value
    def set_axis(self, axis, value):
        global mwt_dict
        c = galil.GCommand
        value_encoder = str(float(value) * 40)  # 40 encoder counts per mm (230*40=9200)
        if axis == "X":
            self.entry_x_target_stored.set(float(value))
            c('DPA=' + str(value_encoder))
            mwt_dict |= {'x_actual': value}
            self.label_x_actual.configure(value)
            self.after(100, self.label_x_actual.configure(value))
        elif axis == "Y":
            self.entry_y_target_stored.set(float(value))
            c('DPB=' + str(value_encoder))
            mwt_dict |= {'y_actual': value}
            self.label_y_actual.configure(value)
            self.after(100, self.label_y_actual.configure(value))
        elif axis == "Z":
            self.entry_z_target_stored.set(float(value))
            c('DPC=' + str(value_encoder))
            mwt_dict |= {'z_actual': value}
            self.label_z_actual.configure(value)
            self.after(100, self.label_z_actual.configure(value))
        else:
            self.print_to_log("Set axis error!")
        self.csv_generate()

    # -- enables the set limits button if the adjacent checkbox is checked
    def enable_button_set_limits(self):
        self.button_set_limits.configure(state=NORMAL if self.checkbox_unlock_limits_status.get() == 1 else DISABLED)

    # -- takes user input for all limits entries and stores those values
    def set_limits(self):
        global mwt_dict
        c = galil.GCommand
        c('FLA=' + str(float(self.entry_x_limit_fwd.get()) * 40))
        c('BLA=' + str(float(self.entry_x_limit_rev.get()) * 40))
        c('FLB=' + str(float(self.entry_y_limit_fwd.get()) * 40))
        c('BLB=' + str(float(self.entry_y_limit_rev.get()) * 40))
        c('FLC=' + str(float(self.entry_z_limit_fwd.get()) * 40))
        c('BLC=' + str(float(self.entry_z_limit_rev.get()) * 40))
        self.entry_x_limit_fwd_stored.set(self.entry_x_limit_fwd.get())
        self.entry_x_limit_rev_stored.set(self.entry_x_limit_rev.get())
        self.entry_y_limit_fwd_stored.set(self.entry_y_limit_fwd.get())
        self.entry_y_limit_rev_stored.set(self.entry_y_limit_rev.get())
        self.entry_z_limit_fwd_stored.set(self.entry_z_limit_fwd.get())
        self.entry_z_limit_rev_stored.set(self.entry_z_limit_rev.get())
        mwt_dict |= {'x_fwd_limit': self.entry_x_limit_fwd_stored.get()}
        mwt_dict |= {'x_rev_limit': self.entry_x_limit_rev_stored.get()}
        mwt_dict |= {'y_fwd_limit': self.entry_y_limit_fwd_stored.get()}
        mwt_dict |= {'y_rev_limit': self.entry_y_limit_rev_stored.get()}
        mwt_dict |= {'z_fwd_limit': self.entry_z_limit_fwd_stored.get()}
        mwt_dict |= {'z_rev_limit': self.entry_z_limit_rev_stored.get()}
        self.checkbox_unlock_limits_status.set(0)
        self.button_set_limits.configure(state="disabled")
        self.csv_generate()
        del c

    # -- enables the set SAD button if the adjacent checkbox is checked
    def enable_button_set_SAD(self):
        self.button_set_SAD.configure(state=NORMAL if self.checkbox_unlock_SAD_status.get() == 1 else DISABLED)

    # -- used to save all current speed, accel, decel carriage attributes
    def set_SAD(self):
        global mwt_dict
        c = galil.GCommand
        self.entry_speed_x_stored.set(self.entry_speed_x.get())
        self.entry_speed_y_stored.set(self.entry_speed_y.get())
        self.entry_speed_z_stored.set(self.entry_speed_z.get())
        self.entry_accel_x_stored.set(self.entry_accel_x.get())
        self.entry_accel_y_stored.set(self.entry_accel_y.get())
        self.entry_accel_z_stored.set(self.entry_accel_z.get())
        self.entry_decel_x_stored.set(self.entry_decel_x.get())
        self.entry_decel_y_stored.set(self.entry_decel_y.get())
        self.entry_decel_z_stored.set(self.entry_decel_z.get())
        c('SPA=' + str(int(self.entry_speed_x.get())))
        c('SPB=' + str(int(self.entry_speed_y.get())))
        c('SPC=' + str(int(self.entry_speed_z.get())))
        c('ACA=' + str(int(self.entry_speed_x.get())))
        c('ACB=' + str(int(self.entry_speed_y.get())))
        c('ACC=' + str(int(self.entry_speed_z.get())))
        c('DCA=' + str(int(self.entry_speed_x.get())))
        c('DCB=' + str(int(self.entry_speed_y.get())))
        c('DCC=' + str(int(self.entry_speed_z.get())))
        mwt_dict |= {'sp_x': self.entry_speed_x_stored.get()}
        mwt_dict |= {'sp_y': self.entry_speed_y_stored.get()}
        mwt_dict |= {'sp_z': self.entry_speed_z_stored.get()}
        mwt_dict |= {'ac_x': self.entry_accel_x_stored.get()}
        mwt_dict |= {'ac_y': self.entry_accel_y_stored.get()}
        mwt_dict |= {'ac_z': self.entry_accel_z_stored.get()}
        mwt_dict |= {'dc_x': self.entry_decel_x_stored.get()}
        mwt_dict |= {'dc_y': self.entry_decel_y_stored.get()}
        mwt_dict |= {'dc_z': self.entry_decel_z_stored.get()}
        self.checkbox_unlock_SAD_status.set(0)
        self.button_set_SAD.configure(state="disabled")
        self.csv_generate()
        del c

    # -- enables the set PID button if the adjacent checkbox is checked
    def enable_button_set_PID(self):
        self.button_set_PID.configure(state=NORMAL if self.checkbox_unlock_PID_status.get() == 1 else DISABLED)

    # -- used to save all current proportional, integral, derivative carriage attributes
    def set_PID(self):
        global mwt_dict
        c = galil.GCommand
        self.entry_kp_x_stored.set(self.entry_kp_x.get())
        self.entry_kp_y_stored.set(self.entry_kp_y.get())
        self.entry_kp_z_stored.set(self.entry_kp_z.get())
        self.entry_ki_x_stored.set(self.entry_ki_x.get())
        self.entry_ki_y_stored.set(self.entry_ki_y.get())
        self.entry_ki_z_stored.set(self.entry_ki_z.get())
        self.entry_kd_x_stored.set(self.entry_kd_x.get())
        self.entry_kd_y_stored.set(self.entry_kd_y.get())
        self.entry_kd_z_stored.set(self.entry_kd_z.get())
        c('KPA=' + str(int(self.entry_kp_x.get())))
        c('KPB=' + str(float(self.entry_kp_y.get())))
        c('KPC=' + str(int(self.entry_kp_z.get())))
        c('KIA=' + str(int(self.entry_ki_x.get())))
        c('KIB=' + str(float(self.entry_ki_y.get())))
        c('KIC=' + str(int(self.entry_ki_z.get())))
        c('KDA=' + str(int(self.entry_kd_x.get())))
        c('KDB=' + str(float(self.entry_kd_y.get())))
        c('KDC=' + str(int(self.entry_kd_z.get())))
        mwt_dict |= {'kp_x': self.entry_kp_x_stored.get()}
        mwt_dict |= {'kp_y': self.entry_kp_y_stored.get()}
        mwt_dict |= {'kp_z': self.entry_kp_z_stored.get()}
        mwt_dict |= {'ki_x': self.entry_ki_x_stored.get()}
        mwt_dict |= {'ki_y': self.entry_ki_y_stored.get()}
        mwt_dict |= {'ki_z': self.entry_ki_z_stored.get()}
        mwt_dict |= {'kd_x': self.entry_kd_x_stored.get()}
        mwt_dict |= {'kd_y': self.entry_kd_y_stored.get()}
        mwt_dict |= {'kd_z': self.entry_kd_z_stored.get()}
        self.checkbox_unlock_PID_status.set(0)
        self.button_set_PID.configure(state="disabled")
        self.csv_generate()
        del c

    # - event log functions
    # -- used to print event descriptions or carriage status to the program event log
    def print_to_log(self, text):
        self.textbox_log.insert(tk.END, '\n')
        self.textbox_log.insert(tk.END, text)

    # -- clears the program event log
    def clear_log(self):
        self.textbox_log.delete("0.0", "end")
        self.textbox_log.insert("0.0", "Log cleared.")

    # - csv functions
    # -- recalls saved limits from csv and outputs them in the log
    # noinspection PyTypeChecker
    def recall_limits(self):
        c = galil.GCommand
        x_fwd = (float(c('FLA=?')) / 40)
        x_rev = (float(c('BLA=?')) / 40)
        y_fwd = (float(c('FLB=?')) / 40)
        y_rev = (float(c('BLB=?')) / 40)
        z_fwd = (float(c('FLC=?')) / 40)
        z_rev = (float(c('BLC=?')) / 40)
        self.entry_x_limit_fwd_stored.set(x_fwd)
        self.entry_x_limit_rev_stored.set(x_rev)
        self.entry_y_limit_fwd_stored.set(y_fwd)
        self.entry_y_limit_rev_stored.set(y_rev)
        self.entry_z_limit_fwd_stored.set(z_fwd)
        self.entry_z_limit_rev_stored.set(z_rev)
        del c

    # -- recalls saved SAD values from csv and outputs them in the log
    # noinspection PyTypeChecker
    def recall_SAD(self):
        c = galil.GCommand
        x_sp = (int(c('SPA=?')))
        x_ac = (int(c('ACA=?')))
        x_dc = (int(c('DCA=?')))
        y_sp = (int(c('SPB=?')))
        y_ac = (int(c('ACB=?')))
        y_dc = (int(c('DCB=?')))
        z_sp = (int(c('SPC=?')))
        z_ac = (int(c('ACC=?')))
        z_dc = (int(c('DCC=?')))
        self.entry_speed_x_stored.set(x_sp)
        self.entry_accel_x_stored.set(x_ac)
        self.entry_decel_x_stored.set(x_dc)
        self.entry_speed_y_stored.set(y_sp)
        self.entry_accel_y_stored.set(y_ac)
        self.entry_decel_y_stored.set(y_dc)
        self.entry_speed_z_stored.set(z_sp)
        self.entry_accel_z_stored.set(z_ac)
        self.entry_decel_z_stored.set(z_dc)
        self.csv_recall()
        del c

    # -- recalls saved PID values from csv and outputs them in the log
    # noinspection PyTypeChecker
    def recall_PID(self):
        c = galil.GCommand
        x_kp = (int(float(c('KPA=?'))))
        x_ki = (float(c('KIA=?')))
        x_kd = (int(float(c('KDA=?'))))
        y_kp = (int(float(c('KPB=?'))))
        y_ki = (float(c('KIB=?')))
        y_kd = (int(float(c('KDB=?'))))
        z_kp = (int(float(c('KPC=?'))))
        z_ki = (float(c('KIC=?')))
        z_kd = (int(float(c('KDC=?'))))
        self.entry_kp_x_stored.set(x_kp)
        self.entry_ki_x_stored.set(x_ki)
        self.entry_kd_x_stored.set(x_kd)
        self.entry_kp_y_stored.set(y_kp)
        self.entry_ki_y_stored.set(y_ki)
        self.entry_kd_y_stored.set(y_kd)
        self.entry_kp_z_stored.set(z_kp)
        self.entry_ki_z_stored.set(z_ki)
        self.entry_kd_z_stored.set(z_kd)
        self.csv_recall()
        del c

    # -- csv file that stores carriage values such as current position and movement limits
    def csv_generate(self):
        with open('mwt_storage.csv', 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in mwt_dict.items():
                writer.writerow([key, value])
        self.checkbox_unlock_limits_status.set(0)
        self.checkbox_unlock_SAD_status.set(0)
        self.checkbox_unlock_PID_status.set(0)
        self.button_set_limits.configure(state="disabled")
        self.button_set_SAD.configure(state="disabled")
        self.button_set_PID.configure(state="disabled")

    # -- recalls saved limits from csv
    def csv_recall(self):
        global mwt_dict
        with open("mwt_storage.csv", "r") as file:
            reader = csv.reader(file)
            for row in reader:
                print(','.join(row))
        self.print_to_log(mwt_dict)

    # -- restores saved positions to GUI/carriage from csv
    # def restore_positions(self):
    #     global mwt_dict
    #     c = galil.GCommand
    #     c('DPA=' + mwt_dict['x_actual'])
    #     c('DPB=' + mwt_dict['y_actual'])
    #     c('DPC=' + mwt_dict['z_actual'])
    #     self.x_actual_stored.set(mwt_dict['x_actual'])
    #     self.y_actual_stored.set(mwt_dict['y_actual'])
    #     self.z_actual_stored.set(mwt_dict['z_actual'])
    #     del c


if __name__ == "__main__":
    app = MoveCarriage()
    app.mainloop()
