import customtkinter
import tkinter as tk
from tkinter import messagebox # For error popups
from src.utils.config_manager import get_config, save_config, get_initial_defaults
import logging


class SettingsPage(customtkinter.CTkToplevel):
    def __init__(self, master, context):
        super().__init__(master)
        self.context = context

        self.title("Application Settings")
        self.geometry("850x650") # Adjusted size
        self.resizable(True, True)

        # Main frame
        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.main_frame.grid_columnconfigure(0, weight=1) # Sidebar
        self.main_frame.grid_columnconfigure(1, weight=3) # Content area
        self.main_frame.grid_rowconfigure(0, weight=1) # Categories content
        self.main_frame.grid_rowconfigure(1, weight=0) # Action buttons

        # Sidebar for categories
        self.sidebar_frame = customtkinter.CTkFrame(self.main_frame, width=200) # Increased width slightly
        self.sidebar_frame.grid(row=0, column=0, padx=(0, 5), pady=(0,5), sticky="nswe")

        self.content_frame = customtkinter.CTkFrame(self.main_frame)
        self.content_frame.grid(row=0, column=1, padx=(5, 0), pady=(0,5), sticky="nswe")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        self.ui_widgets = {} # To store references to widgets for saving/resetting
        self.backpack_widget_list = [] # Specific list for backpack entries

        self.categories = [
            "General", "Items & Names", "Gameplay & Combat",
            "Hotkeys", "Refill & NPC", "Timings", "UI Defaults"
        ]

        self.category_buttons = {}
        for i, category_name in enumerate(self.categories):
            button = customtkinter.CTkButton(
                self.sidebar_frame,
                text=category_name,
                command=lambda cat=category_name: self.show_category_content(cat)
            )
            button.pack(fill="x", padx=10, pady=5)
            self.category_buttons[category_name] = button

        self.category_content_frames = {}

        self.action_buttons_frame = customtkinter.CTkFrame(self.main_frame)
        self.action_buttons_frame.grid(row=1, column=0, columnspan=2, padx=0, pady=(5,0), sticky="ew")
        self.action_buttons_frame.grid_columnconfigure(0, weight=1)
        self.action_buttons_frame.grid_columnconfigure(1, weight=1)

        self.save_button = customtkinter.CTkButton(self.action_buttons_frame, text="Save Settings", command=self.save_settings_handler)
        self.save_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.reset_button = customtkinter.CTkButton(self.action_buttons_frame, text="Reset to Defaults", command=self.reset_settings_handler)
        self.reset_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.show_category_content(self.categories[0])

    def set_nested_value(self, d, key_path, value):
        keys = key_path.split('.')
        current_level = d
        for i, key in enumerate(keys):
            if i == len(keys) - 1:
                current_level[key] = value
            else:
                current_level = current_level.setdefault(key, {})

    def get_nested_value(self, d, key_path, default=None):
        keys = key_path.split('.')
        current_level = d
        try:
            for key in keys:
                current_level = current_level[key]
            return current_level
        except (KeyError, TypeError):
            return default

    def show_category_content(self, category_name):
        # Hide all other frames
        for frame in self.category_content_frames.values():
            frame.pack_forget()

        # Create frame if it doesn't exist
        if category_name not in self.category_content_frames:
            frame = customtkinter.CTkFrame(self.content_frame)
            self.category_content_frames[category_name] = frame

            # Populate frame based on category
            if category_name == "General":
                self.create_general_settings_ui(frame)
            elif category_name == "Items & Names":
                self.create_items_names_settings_ui(frame)
            elif category_name == "Gameplay & Combat":
                self.create_gameplay_combat_settings_ui(frame)
            elif category_name == "Hotkeys":
                self.create_hotkeys_settings_ui(frame)
            elif category_name == "Refill & NPC":
                self.create_refill_npc_settings_ui(frame)
            elif category_name == "Timings":
                self.create_timings_delays_settings_ui(frame)
            elif category_name == "UI Defaults":
                self.create_ui_app_defaults_settings_ui(frame)
            else:
                label = customtkinter.CTkLabel(frame, text=f"Content for {category_name}")
                label.pack(padx=20, pady=20)

        # Show the current category frame
        self.category_content_frames[category_name].pack(fill="both", expand=True, padx=10, pady=10)
        # print(f"Switched to {category_name}") # For debugging

    def _create_labeled_entry(self, parent, config_key, label_text, default_value, row, expected_type='str', read_only=False):
        label = customtkinter.CTkLabel(parent, text=label_text)
        label.grid(row=row, column=0, padx=10, pady=(10,5), sticky="w")

        current_value = get_config(config_key, default_value)
        entry_var = tk.StringVar(value=str(current_value)) # Ensure string for CTkEntry

        entry_state = 'readonly' if read_only else 'normal'
        entry = customtkinter.CTkEntry(parent, textvariable=entry_var, state=entry_state)
        entry.grid(row=row, column=1, padx=10, pady=(10,5), sticky="ew")

        self.ui_widgets[config_key] = {'widget': entry, 'var': entry_var, 'type': expected_type, 'category': parent}
        return entry_var, entry

    def create_general_settings_ui(self, parent_frame):
        parent_frame.grid_columnconfigure(1, weight=1)

        self._create_labeled_entry(
            parent_frame, 'profile_file_path',
            "Profile Storage Path:",
            'file.json',
            row=0,
            read_only=True
        )

        self._create_labeled_entry(
            parent_frame, 'game_window.resolution_height',
            "Game Window Height (pixels):",
            1080,
            row=1,
            expected_type='int'
        )

    def create_items_names_settings_ui(self, parent_frame):
        parent_frame.grid_columnconfigure(1, weight=1)
        current_row = 0

        # Backpacks
        backpacks_label = customtkinter.CTkLabel(parent_frame, text="Backpack Names:")
        backpacks_label.grid(row=current_row, column=0, padx=10, pady=(10,0), sticky="nw")

        self.backpacks_scrollable_frame = customtkinter.CTkScrollableFrame(parent_frame, height=200)
        self.backpacks_scrollable_frame.grid(row=current_row, column=1, padx=10, pady=(10,0), sticky="nsew")
        self.backpacks_scrollable_frame.grid_columnconfigure(0, weight=1)

        self.backpack_widget_list = [] # Store StringVar for each backpack entry

        current_backpacks = get_config('backpacks', [])
        self._repopulate_backpack_entries(current_backpacks)
        current_row +=1

        add_bp_button = customtkinter.CTkButton(parent_frame, text="Add Backpack", command=self._add_new_backpack_ui_entry)
        add_bp_button.grid(row=current_row, column=1, padx=10, pady=5, sticky="w")
        current_row +=1

        # Store a reference to control this list of widgets
        self.ui_widgets['backpacks'] = {'widget_list': self.backpack_widget_list, 'type': 'list[str]', 'category': parent_frame, 'frame': self.backpacks_scrollable_frame}

        sep = ttk.Separator(parent_frame, orient='horizontal') # Using ttk for separator
        sep.grid(row=current_row, column=0, columnspan=2, sticky='ew', pady=10)
        current_row +=1

        self._create_labeled_entry(
            parent_frame, 'chat_tabs.local_chat',
            "Local Chat Tab Name:",
            'local chat',
            row=current_row
        )
        current_row +=1

    def _repopulate_backpack_entries(self, backpack_names_list):
        # Clear existing UI entries
        for child in self.backpacks_scrollable_frame.winfo_children():
            child.destroy()
        self.backpack_widget_list.clear()

        for bp_name in backpack_names_list:
            self._add_backpack_ui_entry(bp_name)

    def _add_backpack_ui_entry(self, name=""):
        entry_var = tk.StringVar(value=name)

        entry_frame = customtkinter.CTkFrame(self.backpacks_scrollable_frame)
        entry_frame.pack(fill="x", pady=2)
        entry_frame.grid_columnconfigure(0, weight=1)
        entry_frame.grid_columnconfigure(1, weight=0) # For remove button

        entry = customtkinter.CTkEntry(entry_frame, textvariable=entry_var)
        entry.grid(row=0, column=0, padx=(0,5), sticky="ew")

        remove_button = customtkinter.CTkButton(entry_frame, text="X", width=30,
            command=lambda ef=entry_frame, ev=entry_var: self._remove_backpack_ui_entry(ef, ev))
        remove_button.grid(row=0, column=1, sticky="e")

        self.backpack_widget_list.append(entry_var) # Store the var

    def _add_new_backpack_ui_entry(self): # Renamed to avoid conflict
        self._add_backpack_ui_entry("")


    def _remove_backpack_ui_entry(self, entry_frame_to_remove, entry_var_to_remove):
        entry_frame_to_remove.destroy()
        self.backpack_widget_list = [v for v in self.backpack_widget_list if v != entry_var_to_remove]

    def _create_section_label(self, parent, text, row):
        label = customtkinter.CTkLabel(parent, text=text, font=customtkinter.CTkFont(weight="bold"))
        label.grid(row=row, column=0, columnspan=2, padx=10, pady=(15, 5), sticky="w")
        return row + 1

    def _create_checkbox_entry(self, parent, config_key, label_text, default_value, row):
        label = customtkinter.CTkLabel(parent, text=label_text)
        label.grid(row=row, column=0, padx=10, pady=(10,5), sticky="w")

        current_value = get_config(config_key, default_value)
        checkbox_var = tk.BooleanVar(value=bool(current_value)) # Ensure bool

        checkbox = customtkinter.CTkCheckBox(parent, text="", variable=checkbox_var)
        checkbox.grid(row=row, column=1, padx=10, pady=(10,5), sticky="w")

        self.ui_widgets[config_key] = {'widget': checkbox, 'var': checkbox_var, 'type': 'bool', 'category': parent}
        return checkbox_var, checkbox

    def _create_combobox_entry(self, parent, config_key, label_text, default_value, options, row):
        label = customtkinter.CTkLabel(parent, text=label_text)
        label.grid(row=row, column=0, padx=10, pady=(10,5), sticky="w")

        current_value = get_config(config_key, default_value)
        combobox_var = tk.StringVar(value=str(current_value)) # Ensure string

        combobox = customtkinter.CTkComboBox(parent, variable=combobox_var, values=options, state='readonly')
        combobox.grid(row=row, column=1, padx=10, pady=(10,5), sticky="ew")

        self.ui_widgets[config_key] = {'widget': combobox, 'var': combobox_var, 'type': 'str_choice', 'category': parent} # type 'str_choice' for combobox
        return combobox_var, combobox

    def create_gameplay_combat_settings_ui(self, parent_frame):
        parent_frame.grid_columnconfigure(1, weight=1)
        current_row = 0
        self._create_labeled_entry(
            parent_frame, 'combat_thresholds.no_monster_stop_attack_threshold',
            "Stop Attack Threshold (no monster):", 70,
            row=current_row, expected_type='int'
        )
        current_row += 1

        current_row = self._create_section_label(parent_frame, "Pathfinding Settings", current_row)
        self._create_labeled_entry(parent_frame, 'pathfinding.radar_x_offset', "Radar X Offset:", 53, row=current_row, expected_type='int')
        current_row += 1
        self._create_labeled_entry(parent_frame, 'pathfinding.radar_y_offset_start', "Radar Y Offset Start:", 54, row=current_row, expected_type='int')
        current_row += 1
        self._create_labeled_entry(parent_frame, 'pathfinding.radar_y_offset_end', "Radar Y Offset End:", 55, row=current_row, expected_type='int')
        current_row += 1
        self._create_labeled_entry(parent_frame, 'pathfinding.astar_diagonal_cost', "A* Diagonal Cost:", 0, row=current_row, expected_type='float') # Or int
        current_row += 1
        self._create_labeled_entry(parent_frame, 'pathfinding.move_action_offset', "Move Action Offset:", 2, row=current_row, expected_type='int')
        current_row += 1

    def create_hotkeys_settings_ui(self, parent_frame):
        scrollable_frame = customtkinter.CTkScrollableFrame(parent_frame)
        scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0)
        scrollable_frame.grid_columnconfigure(1, weight=1)

        current_row = 0
        # get_initial_defaults is already imported at the top
        default_hotkeys = get_initial_defaults().get('hotkeys', {})

        for key_name, default_value in default_hotkeys.items():
            label_text = key_name.replace('_', ' ').title() + ":"
            self._create_labeled_entry(
                scrollable_frame, f'hotkeys.{key_name}',
                label_text, default_value, row=current_row
            )
            current_row += 1

    def create_refill_npc_settings_ui(self, parent_frame):
        scrollable_frame = customtkinter.CTkScrollableFrame(parent_frame)
        scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0)
        scrollable_frame.grid_columnconfigure(1, weight=1)
        current_row = 0

        # get_initial_defaults is already imported at the top
        current_row = self._create_section_label(scrollable_frame, "NPC Keywords", current_row)
        default_npc_keywords = get_initial_defaults().get('npc_keywords', {})
        for key, default_val in default_npc_keywords.items():
            label = key.replace('_', ' ').title() + " Keyword:"
            self._create_labeled_entry(scrollable_frame, f'npc_keywords.{key}', label, default_val, current_row)
            current_row += 1

        current_row = self._create_section_label(scrollable_frame, "Refill Delays", current_row)
        self._create_labeled_entry(scrollable_frame, 'refill_delays.before_start', "Delay Before Start (s):", 1.0, current_row, expected_type='float')
        current_row += 1
        self._create_labeled_entry(scrollable_frame, 'refill_delays.after_complete', "Delay After Complete (s):", 1.0, current_row, expected_type='float')
        current_row += 1
        self._create_labeled_entry(scrollable_frame, 'refill_delays.use_hotkey_min', "Hotkey Use Min Delay (s):", 0.8, current_row, expected_type='float')
        current_row += 1
        self._create_labeled_entry(scrollable_frame, 'refill_delays.use_hotkey_max', "Hotkey Use Max Delay (s):", 1.2, current_row, expected_type='float')
        current_row += 1

    def create_timings_delays_settings_ui(self, parent_frame):
        scrollable_frame = customtkinter.CTkScrollableFrame(parent_frame)
        scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0)
        scrollable_frame.grid_columnconfigure(1, weight=1)
        current_row = 0

        current_row = self._create_section_label(scrollable_frame, "Keyboard Delays", current_row)
        self._create_labeled_entry(scrollable_frame, 'keyboard_delays.write_interval_min', "Write Min Interval (s):", 0.03, current_row, expected_type='float')
        current_row += 1
        self._create_labeled_entry(scrollable_frame, 'keyboard_delays.write_interval_max', "Write Max Interval (s):", 0.12, current_row, expected_type='float')
        current_row += 1
        self._create_labeled_entry(scrollable_frame, 'keyboard_delays.default_random_min', "Default Random Min Delay (s):", 0.2, current_row, expected_type='float')
        current_row += 1
        self._create_labeled_entry(scrollable_frame, 'keyboard_delays.default_random_max', "Default Random Max Delay (s):", 0.5, current_row, expected_type='float')
        current_row += 1
        self._create_labeled_entry(scrollable_frame, 'keyboard_delays.say_task_min', "Say Task Min Delay (s):", 0.3, current_row, expected_type='float')
        current_row += 1
        self._create_labeled_entry(scrollable_frame, 'keyboard_delays.say_task_max', "Say Task Max Delay (s):", 0.6, current_row, expected_type='float')
        current_row += 1

    def create_ui_app_defaults_settings_ui(self, parent_frame):
        scrollable_frame = customtkinter.CTkScrollableFrame(parent_frame)
        scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0)
        scrollable_frame.grid_columnconfigure(1, weight=1)
        current_row = 0

        # get_initial_defaults is already imported at the top
        current_row = self._create_section_label(scrollable_frame, "Combo Spell Defaults", current_row)
        self._create_labeled_entry(scrollable_frame, 'ui_defaults.combo_spell_name', "Default Spell Name:", 'Default', current_row)
        current_row += 1
        self._create_combobox_entry(scrollable_frame, 'ui_defaults.combo_spell_creature_compare', "Creature Compare:", 'lessThan', ["lessThan", "greaterThan", "equalTo"], current_row)
        current_row += 1
        self._create_labeled_entry(scrollable_frame, 'ui_defaults.combo_spell_creature_value', "Creature Value:", 5, current_row, expected_type='int')
        current_row += 1
        self._create_checkbox_entry(scrollable_frame, 'ui_defaults.combo_spell_current_index_reset_on_load', "Reset Spell Index on Load:", True, current_row)
        current_row += 1

        current_row = self._create_section_label(scrollable_frame, "Waypoint Defaults", current_row)
        self._create_combobox_entry(scrollable_frame, 'ui_defaults.waypoint_direction', "Default Waypoint Direction:", 'center', ["center", "north", "south", "east", "west"], current_row)
        current_row += 1

        current_row = self._create_section_label(scrollable_frame, "Slot Assignments", current_row)
        default_slots = get_initial_defaults().get('slots', {})
        for key, default_val in default_slots.items():
            label = key.replace('_', ' ').title() + " Slot:"
            self._create_labeled_entry(scrollable_frame, f'slots.{key}', label, default_val, current_row, expected_type='int')
            current_row += 1

    def save_settings_handler(self):
        new_config_data = {}
        validation_failed = False
        for config_key, widget_info in self.ui_widgets.items():
            widget = widget_info['widget']
            var = widget_info.get('var') # CTkEntry uses textvariable, CTkCheckBox uses variable directly
            expected_type = widget_info['type']

            current_value_str = ""
            if isinstance(widget, customtkinter.CTkEntry):
                current_value_str = var.get()
            elif isinstance(widget, customtkinter.CTkCheckBox):
                # .get() for CTkCheckBox returns int (0 or 1)
                current_value_str = bool(widget.get())
            elif isinstance(widget, customtkinter.CTkComboBox):
                current_value_str = var.get()
            elif config_key == 'backpacks': # Special handling for backpack list
                backpack_values = [bp_var.get() for bp_var in self.backpack_widget_list if bp_var.get().strip() != ""]
                self.set_nested_value(new_config_data, config_key, backpack_values)
                continue # Skip to next widget

            processed_value = None
            if expected_type == 'str':
                processed_value = current_value_str
            elif expected_type == 'int':
                try:
                    processed_value = int(current_value_str)
                except ValueError:
                    logging.error(f"Invalid integer value for {config_key}: {current_value_str}")
                    messagebox.showerror("Validation Error", f"Invalid integer value for '{config_key.replace('_', ' ').title()}': {current_value_str}")
                    validation_failed = True
                    continue
            elif expected_type == 'float':
                try:
                    processed_value = float(current_value_str)
                except ValueError:
                    logging.error(f"Invalid float value for {config_key}: {current_value_str}")
                    messagebox.showerror("Validation Error", f"Invalid float value for '{config_key.replace('_', ' ').title()}': {current_value_str}")
                    validation_failed = True
                    continue
            elif expected_type == 'bool':
                processed_value = current_value_str # Already bool from CTkCheckBox
            elif expected_type == 'str_choice': # For ComboBox
                processed_value = current_value_str

            if processed_value is not None:
                self.set_nested_value(new_config_data, config_key, processed_value)

        if validation_failed:
            messagebox.showinfo("Save Status", "Settings not saved due to validation errors.")
            return

        if save_config(new_config_data):
            messagebox.showinfo("Save Status", "Settings saved successfully!\nSome changes may require an application restart to take full effect.")
        else:
            messagebox.showerror("Save Status", "Failed to save settings. Check logs.")

    def reset_settings_handler(self):
        if not messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all settings to their defaults? Unsaved changes will be lost."):
            return

        defaults = get_initial_defaults()

        for config_key, widget_info in self.ui_widgets.items():
            widget = widget_info['widget']
            var = widget_info.get('var')
            expected_type = widget_info['type']

            default_value = self.get_nested_value(defaults, config_key)
            if default_value is None: # Should not happen if defaults are comprehensive
                logging.warning(f"No default value found for {config_key} during reset.")
                continue

            if config_key == 'backpacks':
                self._repopulate_backpack_entries(default_value) # default_value is the list of backpack names
            elif isinstance(widget, customtkinter.CTkEntry):
                var.set(str(default_value))
            elif isinstance(widget, customtkinter.CTkCheckBox):
                if bool(default_value):
                    widget.select()
                else:
                    widget.deselect()
            elif isinstance(widget, customtkinter.CTkComboBox):
                var.set(str(default_value))

        messagebox.showinfo("Reset Complete", "Settings have been reset to defaults. Click 'Save Settings' to make them permanent.")


# Example usage (if you want to run this page standalone for testing)
if __name__ == '__main__':
    app = customtkinter.CTk()
    customtkinter.set_appearance_mode("dark") # or "light"
    customtkinter.set_default_color_theme("blue")

    # Mock context if needed for standalone run
    # Also need to mock config_manager or ensure it loads defaults for standalone test
    from src.utils.config_manager import load_config # Ensure defaults are loaded
    load_config()

    class MockContext:
        pass
    mock_context = MockContext()

    settings_window = SettingsPage(app, mock_context)
    settings_window.grab_set() # Make it modal if run standalone
    app.mainloop()

# Need to import ttk for the separator, ensure it's there
from tkinter import ttk
