import asyncio
import customtkinter as ctk
import os
import pyautogui
import re
import threading
import time

from PIL import Image
from pynput.mouse import Button, Controller

from autoclicker.utils import Utils

class AutoClicker(Utils):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Moon Auto Clicker")
        self.root.geometry("600x600")

        # Set Window Icon with robust path handling
        self.root.after(200, lambda: self._set_icon())
        
        self.root.bind("<<ToggleAction>>", lambda e: self._toggle_action())
        self.root.bind("<<ExitApp>>", lambda e: self._exit_app())

        config = self.load_config()

        # Load Hotkeys safely
        hotkeys_conf = config.get('hotkeys', {})
        self.hk_action = hotkeys_conf.get('toggle_action', 'F6')
        self.hk_exit = hotkeys_conf.get('exit_app', 'F5')

        self.active = threading.Event()
        self.mouse = Controller()
        self.i = 0

        # delay
        self.delay_hours = 0
        self.delay_minutes = 0
        self.delay_seconds = 0
        self.delay_milliseconds = 100
        self.loop_interval = self._calculate_interval()

        # click options
        self.mouse_btn = "left"
        self.click_type = "single"

        # repeat options
        self.repeat_type = "infinite"
        self.repeat_count = 1

        # cursor position
        self.cursor_position = "current"
        self.cursor_x = 0
        self.cursor_y = 0

        # presets
        self.presets = self.load_presets()

        self.create_widgets()

    def _calculate_interval(self):
        return (self.delay_hours * 3600000 + 
                self.delay_minutes * 60000 + 
                self.delay_seconds * 1000 + 
                self.delay_milliseconds)

    def _on_interval_change(self, *args):
        try:
            self.delay_hours = int(self.hours_var.get()) if self.hours_var.get() else 0
            self.delay_minutes = int(self.minutes_var.get()) if self.minutes_var.get() else 0
            self.delay_seconds = int(self.seconds_var.get()) if self.seconds_var.get() else 0
            self.delay_milliseconds = int(self.milliseconds_var.get()) if self.milliseconds_var.get() else 0
            self.loop_interval = self._calculate_interval()
        except ValueError:
            pass # Ignore non-integer input

    def _on_mouse_btn_change(self, *args):
        self.mouse_btn = self.mouse_btn_var.get()

    def _on_click_type_change(self, *args):
        self.click_type = self.click_type_var.get()

    def _on_repeat_type_change(self, *args):
        self.repeat_type = self.repeat_type_var.get()

    def _on_repeat_count_change(self, *args):
        try:
            self.repeat_count = int(self.repeat_count_var.get()) if self.repeat_count_var.get() else 0
        except ValueError:
            pass

    def _pick_cursor_position(self):
        def countdown(count):
            if count > 0:
                self.pick_button.configure(text=f"Picking in {count}...")
                self.root.after(1000, lambda: countdown(count - 1))
            else:
                x, y = pyautogui.position()
                self.cursor_x_var.set(str(x))
                self.cursor_y_var.set(str(y))
                self.cursor_position_var.set("custom")
                self.pick_button.configure(text="Pick Position")
        
        countdown(3)

    def _on_cursor_position_change(self, *args):
        self.cursor_position = self.cursor_position_var.get()

    def _on_cursor_x_change(self, *args):
        try:
            self.cursor_x = int(self.cursor_x_var.get()) if self.cursor_x_var.get() else 0
        except ValueError:
            pass

    def _on_cursor_y_change(self, *args):
        try:
            self.cursor_y = int(self.cursor_y_var.get()) if self.cursor_y_var.get() else 0
        except ValueError:
            pass

    def _apply_preset(self, preset_name):
        if preset_name in self.presets:
            p = self.presets[preset_name]
            self.hours_var.set(str(p.get('hours', 0)))
            self.minutes_var.set(str(p.get('minutes', 0)))
            self.seconds_var.set(str(p.get('seconds', 0)))
            self.milliseconds_var.set(str(p.get('milliseconds', 100)))

    def _save_current_as_preset(self):
        # Using a simple dialog to get the name
        dialog = ctk.CTkInputDialog(text="Enter preset name:", title="Save Preset")
        name = dialog.get_input()
        if name:
            self.save_new_preset(preset_name=name)
            self.presets = self.load_presets()
            self.preset_menu.configure(values=list(self.presets.keys()))
            self.preset_var.set(name)

    def _delete_selected_preset(self):
        name = self.preset_var.get()
        if name == "default":
            return
        
        if self.delete_preset(name):
            self.presets = self.load_presets()
            self.preset_menu.configure(values=list(self.presets.keys()))
            self.preset_var.set("default")
            self._apply_preset("default")

    def _set_icon(self):
        try:
            icon_path = self.resource_path("res/icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
            else:
                print(f"Icon not found at: {icon_path}")
        except Exception as e:
            print(f"Failed to set icon: {e}")

    def _toggle_action(self):
        if self.active.is_set():
            self.active.clear()
            self.status_label.configure(text="Status: Inactive", text_color="#ff5555")
            self.mouse_position = None
        else:
            self.active.set()
            self.status_label.configure(text="Status: Active", text_color="#2cc985")

    def _exit_app(self):
        self.save_config()
        if self.active.is_set():
            self.active.clear()
            time.sleep(0.1)
        self.root.destroy()
        # Ensure thread exit
        os._exit(0)

    def create_widgets(self):
        # Configure Grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # Title Section
        self.title_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.title_frame.grid(row=0, column=0, padx=30, pady=(25, 5), sticky="ew")

        self.title = ctk.CTkLabel(self.title_frame, text="Moon Auto Clicker", font=ctk.CTkFont(size=28, weight="bold"))
        self.title.pack(side="left")

        self.status_label = ctk.CTkLabel(
            self.title_frame, 
            text="Status: Inactive", 
            text_color="#ff5555", 
            font=ctk.CTkFont(size=14, weight="bold"),
            bg_color="#2b2b2b",
            corner_radius=8,
            padx=15,
            pady=5
        )
        self.status_label.pack(side="right")

        # Tabs
        self.tab_view = ctk.CTkTabview(self.root, corner_radius=15)
        self.tab_view.grid(row=1, column=0, padx=20, pady=(10, 20), sticky="nsew")
        
        self.tab_settings = self.tab_view.add("Settings")
        self.tab_hotkeys = self.tab_view.add("Hotkeys")

        # -- Settings Tab Layout --
        self.tab_settings.grid_columnconfigure(0, weight=1)
        self.tab_settings.grid_columnconfigure(1, weight=1)

        # Common style for section labels
        section_font = ctk.CTkFont(size=15, weight="bold")
        label_font = ctk.CTkFont(size=13)

        # --- Section 1: Timing ---
        timing_frame = ctk.CTkFrame(self.tab_settings, corner_radius=10, border_width=2)
        timing_frame.grid(row=0, column=0, columnspan=2, padx=15, pady=10, sticky="nsew")
        timing_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(timing_frame, text="Click Interval", font=section_font).grid(row=0, column=0, columnspan=4, padx=15, pady=(10, 5), sticky="w")

        # Timing Inputs
        timer_labels = ["Hours", "Minutes", "Seconds", "Milliseconds"]
        self.hours_var = ctk.StringVar(value=str(self.delay_hours))
        self.minutes_var = ctk.StringVar(value=str(self.delay_minutes))
        self.seconds_var = ctk.StringVar(value=str(self.delay_seconds))
        self.milliseconds_var = ctk.StringVar(value=str(self.delay_milliseconds))

        # Add traces
        self.hours_var.trace_add("write", self._on_interval_change)
        self.minutes_var.trace_add("write", self._on_interval_change)
        self.seconds_var.trace_add("write", self._on_interval_change)
        self.milliseconds_var.trace_add("write", self._on_interval_change)

        vars_list = [self.hours_var, self.minutes_var, self.seconds_var, self.milliseconds_var]

        for i, label in enumerate(timer_labels):
            box = ctk.CTkFrame(timing_frame, fg_color="transparent")
            box.grid(row=1, column=i, padx=5, pady=(0, 15))
            ctk.CTkLabel(box, text=label, font=label_font, text_color="#aaaaaa").pack()
            # Assigning to self attributes for consistency if needed, though they are stored in self.xxx_var
            ctk.CTkEntry(box, width=70, textvariable=vars_list[i], justify="center", font=ctk.CTkFont(size=14)).pack(pady=2)
    
        ctk.CTkLabel(timing_frame, text="Preset:", font=label_font).grid(row=2, column=0, padx=15, pady=5, sticky="w")
        self.preset_var = ctk.StringVar(value="default")
        self.preset_menu = ctk.CTkOptionMenu(
            timing_frame, 
            variable=self.preset_var, 
            values=list(self.presets.keys()),
            command=self._apply_preset,
            width=150
        )
        self.preset_menu.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Delete Button
        ctk.CTkButton(
            timing_frame, 
            text="Delete", 
            command=self._delete_selected_preset,
            width=70,
            fg_color="#ff5555",
            hover_color="#ff3333"
        ).grid(row=2, column=2, padx=5, pady=5, sticky="w")

        ctk.CTkButton(
            timing_frame, 
            text="Save Current", 
            command=self._save_current_as_preset,
            width=100
        ).grid(row=2, column=3, padx=15, pady=5, sticky="e")

        # --- Section 2: Click Options & Repeat ---
        # Bottom grid for options and repeat
        bottom_grid = ctk.CTkFrame(self.tab_settings, fg_color="transparent")
        bottom_grid.grid(row=1, column=0, columnspan=2, sticky="nsew")
        bottom_grid.grid_columnconfigure((0, 1), weight=1)

        # 2a: Click Options
        opts_frame = ctk.CTkFrame(bottom_grid, corner_radius=10, border_width=2)
        opts_frame.grid(row=0, column=0, padx=(15, 7), pady=5, sticky="nsew")
        opts_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(opts_frame, text="Click Configuration", font=section_font).grid(row=0, column=0, columnspan=2, padx=15, pady=(10, 5), sticky="w")
        
        self.mouse_btn_var = ctk.StringVar(value=self.mouse_btn)
        self.click_type_var = ctk.StringVar(value=self.click_type)
        self.mouse_btn_var.trace_add("write", self._on_mouse_btn_change)
        self.click_type_var.trace_add("write", self._on_click_type_change)

        ctk.CTkLabel(opts_frame, text="Mouse Button:", font=label_font).grid(row=1, column=0, padx=15, pady=5, sticky="w")
        ctk.CTkOptionMenu(opts_frame, variable=self.mouse_btn_var, values=["left", "right", "middle"], width=120).grid(row=1, column=1, padx=15, pady=5, sticky="ew")

        ctk.CTkLabel(opts_frame, text="Click Type:", font=label_font).grid(row=2, column=0, padx=15, pady=5, sticky="w")
        ctk.CTkOptionMenu(opts_frame, variable=self.click_type_var, values=["single", "double"], width=120).grid(row=2, column=1, padx=15, pady=5, sticky="ew")

        # 2b: Repeat Options
        repeat_frame = ctk.CTkFrame(bottom_grid, corner_radius=10, border_width=2)
        repeat_frame.grid(row=0, column=1, padx=(7, 15), pady=5, sticky="nsew")

        ctk.CTkLabel(repeat_frame, text="Repetition", font=section_font).grid(row=0, column=0, columnspan=2, padx=15, pady=(10, 5), sticky="w")

        self.repeat_type_var = ctk.StringVar(value=self.repeat_type)
        self.repeat_count_var = ctk.StringVar(value=str(self.repeat_count))
        self.repeat_type_var.trace_add("write", self._on_repeat_type_change)
        self.repeat_count_var.trace_add("write", self._on_repeat_count_change)

        ctk.CTkRadioButton(repeat_frame, text="Until Stopped", variable=self.repeat_type_var, value="infinite", font=label_font).grid(row=1, column=0, columnspan=2, padx=15, pady=5, sticky="w")
        finite_radio = ctk.CTkRadioButton(repeat_frame, text="Repeat Count:", variable=self.repeat_type_var, value="finite", font=label_font)
        finite_radio.grid(row=2, column=0, padx=(15, 5), pady=5, sticky="w")
        ctk.CTkEntry(repeat_frame, width=60, textvariable=self.repeat_count_var, justify="center").grid(row=2, column=1, padx=(0, 15), pady=5, sticky="w")

        # --- Section 3: Cursor Position ---
        cursor_frame = ctk.CTkFrame(self.tab_settings, corner_radius=10, border_width=2)
        cursor_frame.grid(row=2, column=0, columnspan=2, padx=15, pady=10, sticky="nsew")
        cursor_frame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(cursor_frame, text="Cursor Location", font=section_font).grid(row=0, column=0, columnspan=2, padx=15, pady=(10, 5), sticky="w")

        self.cursor_position_var = ctk.StringVar(value=self.cursor_position)
        self.cursor_x_var = ctk.StringVar(value=str(self.cursor_x))
        self.cursor_y_var = ctk.StringVar(value=str(self.cursor_y))
        self.cursor_position_var.trace_add("write", self._on_cursor_position_change)
        self.cursor_x_var.trace_add("write", self._on_cursor_x_change)
        self.cursor_y_var.trace_add("write", self._on_cursor_y_change)

        ctk.CTkRadioButton(cursor_frame, text="Current Cursor", variable=self.cursor_position_var, value="current", font=label_font).grid(row=1, column=0, padx=15, pady=5, sticky="w")
        ctk.CTkRadioButton(cursor_frame, text="Custom Position", variable=self.cursor_position_var, value="custom", font=label_font).grid(row=2, column=0, padx=15, pady=5, sticky="w")

        # Custom values row
        coords_frame = ctk.CTkFrame(cursor_frame, fg_color="transparent")
        coords_frame.grid(row=2, column=1, columnspan=3, padx=15, pady=5, sticky="ew")
        
        ctk.CTkLabel(coords_frame, text="X:", font=label_font).pack(side="left", padx=5)
        ctk.CTkEntry(coords_frame, width=60, textvariable=self.cursor_x_var, justify="center").pack(side="left", padx=5)
        ctk.CTkLabel(coords_frame, text="Y:", font=label_font).pack(side="left", padx=5)
        ctk.CTkEntry(coords_frame, width=60, textvariable=self.cursor_y_var, justify="center").pack(side="left", padx=5)
        
        self.pick_button = ctk.CTkButton(
            coords_frame, 
            text="Pick Position", 
            command=self._pick_cursor_position,
            fg_color="#3b3b3b",
            hover_color="#4b4b4b",
            width=120
        )
        self.pick_button.pack(side="right", padx=10)

        # -- Hotkeys Tab --
        self.tab_hotkeys.grid_columnconfigure(0, weight=1)
        self.hk_frame = ctk.CTkFrame(self.tab_hotkeys, corner_radius=10)
        self.hk_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.hk_frame.grid_columnconfigure(1, weight=1)

        # Helper to create row
        def add_hk_row(row, label, current_val):
            ctk.CTkLabel(self.hk_frame, text=label, font=label_font).grid(row=row, column=0, padx=25, pady=15, sticky="w")
            entry = ctk.CTkEntry(self.hk_frame, font=ctk.CTkFont(size=14, weight="bold"), justify="center")
            entry.insert(0, current_val)
            entry.grid(row=row, column=1, padx=25, pady=15, sticky="ew")
            return entry

        ctk.CTkLabel(self.hk_frame, text="Configure Global Hotkeys", font=section_font).grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")

        self.entry_action = add_hk_row(1, "Start / Stop Clicker:", self.hk_action)
        self.entry_exit = add_hk_row(2, "Emergency Exit:", self.hk_exit)

        save_btn = ctk.CTkButton(
            self.hk_frame, 
            text="Save & Update Hotkeys", 
            command=self.save_hotkeys,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        save_btn.grid(row=3, column=0, columnspan=2, pady=30, padx=50, sticky="ew")

    def clicker_worker(self):
        while True:
            self.active.wait()
            try:
                mouse_btn = None
                if self.mouse_btn == "left":
                    mouse_btn = Button.left
                elif self.mouse_btn == "right":
                    mouse_btn = Button.right
                elif self.mouse_btn == "middle":
                    mouse_btn = Button.middle
                if self.cursor_position != "current":
                    self.mouse.position = (int(self.cursor_x), int(self.cursor_y))
                if self.click_type == "single":
                    self.mouse.click(mouse_btn)
                elif self.click_type == "double":
                    self.mouse.click(mouse_btn, 2)
                if self.repeat_type != "infinite":
                    self.i += 1
                    if self.i >= int(self.repeat_count):
                        self._toggle_action()
                        self.i = 0
            except Exception as e:
                print(f"Error in clicker worker: {e}")
                time.sleep(1)
            time.sleep(self.loop_interval / 1000)

    def run(self):
        self.update_hotkeys()

        threading.Thread(target=self.clicker_worker, daemon=True).start()

        self.root.protocol("WM_DELETE_WINDOW", self._exit_app)
        self.root.mainloop()
