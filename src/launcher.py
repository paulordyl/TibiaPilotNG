#!/usr/bin/env python3
"""Launcher GUI: automatic importer, waypoint capture, auto-heal toggle, and start/stop pilot.

Run with:
  PYTHONPATH=$(pwd) python3 src/launcher.py

Notes:
 - Requires project dependencies (customtkinter, pyautogui, tinydb, etc.)
 - Uses src.ui.context.Context to manipulate current profile and load scripts
 - Uses PilotNGThread to run the pilot loop in a background thread when starting the bot
"""
import os
import threading
import time
import json
import traceback

try:
    import customtkinter
    from tkinter import Listbox, END, StringVar
except Exception:
    print('customtkinter not available. Install customtkinter to use the launcher UI.')
    raise

# optional runtime imports
try:
    import pyautogui
except Exception:
    pyautogui = None

# project imports
from src.ui.context import Context as UIContext
from src.gameplay.context import context as default_context
from src.gameplay.threads.pilotNG import PilotNGThread

IMPORT_DIR = os.path.join('src', 'data', 'imported', 'current-repo')

class LauncherApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        customtkinter.set_appearance_mode('dark')
        self.title('TibiaPilotNG Launcher')
        self.resizable(False, False)

        # context and profile
        self.ui_ctx = UIContext(default_context)

        # UI elements
        self.import_btn = customtkinter.CTkButton(self, text='Auto-Import', command=self.auto_import)
        self.import_btn.grid(row=0, column=0, padx=10, pady=10)

        self.refresh_btn = customtkinter.CTkButton(self, text='Refresh List', command=self.refresh_list)
        self.refresh_btn.grid(row=0, column=1, padx=10, pady=10)

        self.listbox = Listbox(self, width=60, height=8)
        self.listbox.grid(row=1, column=0, columnspan=2, padx=10, pady=6)

        self.load_btn = customtkinter.CTkButton(self, text='Load Selected', command=self.load_selected)
        self.load_btn.grid(row=2, column=0, padx=10, pady=8)

        self.capture_btn = customtkinter.CTkButton(self, text='Capture Waypoint', command=self.capture_waypoint)
        self.capture_btn.grid(row=2, column=1, padx=10, pady=8)

        # auto-heal toggle
        self.auto_heal_var = StringVar(value='off')
        self.auto_heal_btn = customtkinter.CTkButton(self, text='Toggle Auto-Heal (Off)', command=self.toggle_auto_heal)
        self.auto_heal_btn.grid(row=3, column=0, padx=10, pady=8)

        # start/stop bot
        self.start_btn = customtkinter.CTkButton(self, text='Start Bot', fg_color='#0a7f3f', command=self.toggle_bot)
        self.start_btn.grid(row=3, column=1, padx=10, pady=8)

        self.log_box = Listbox(self, width=80, height=8)
        self.log_box.grid(row=4, column=0, columnspan=2, padx=10, pady=8)

        self.pilot_thread = None
        self.running = False

        self.refresh_list()

    def log(self, *args):
        txt = ' '.join(str(a) for a in args)
        print(txt)
        self.log_box.insert(END, txt)
        self.log_box.yview_moveto(1.0)

    def auto_import(self):
        # run the tools/import_and_migrate.py logic
        try:
            from tools import import_and_migrate as migrator
            # If run as module, call its main logic (we wrote it as script). Instead, call the script file.
            script = os.path.join('tools', 'import_and_migrate.py')
            if os.path.isfile(script):
                self.log('Running automatic import/migration...')
                os.system(f'python3 {script}')
                self.log('Import done. Refreshing list...')
                self.refresh_list()
            else:
                self.log('Importer script not found at', script)
        except Exception as e:
            self.log('Auto-import failed:', e)
            traceback.print_exc()

    def refresh_list(self):
        self.listbox.delete(0, END)
        if not os.path.isdir(IMPORT_DIR):
            self.log('No imported data at', IMPORT_DIR)
            return
        for f in sorted(os.listdir(IMPORT_DIR)):
            if f.lower().endswith(('.json', '.yaml', '.yml')):
                self.listbox.insert(END, f)
        self.log('Found', self.listbox.size(), 'importable files')

    def load_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            self.log('No selection')
            return
        fname = self.listbox.get(sel[0])
        full = os.path.join(IMPORT_DIR, fname)
        try:
            with open(full, 'r') as fh:
                data = json.load(fh)
                if not isinstance(data, list):
                    # if file is migrated_waypoints.json it may be a list already
                    self.log('Loaded file is not a list; wrapping into list for safety')
                    data = [data]
                self.ui_ctx.loadScript(data)
                self.log('Loaded', fname, 'into current profile')
        except Exception as e:
            self.log('Error loading', fname, e)
            traceback.print_exc()

    def capture_waypoint(self):
        if pyautogui is None:
            self.log('pyautogui not available. Install pyautogui to capture screen positions.')
            return
        # instruct user
        self.log('Move your mouse to the waypoint position and press Enter in this window to record')
        # wait for Enter key press in console instead of gui blocking
        # alternatively, show a blocking dialog
        from tkinter import simpledialog
        label = simpledialog.askstring('Waypoint label', 'Label for waypoint:')
        if label is None:
            self.log('Capture cancelled')
            return
        self.log('When ready, move the mouse to target and press OK')
        from tkinter import messagebox
        messagebox.showinfo('Capture', 'Move the mouse to the desired position and click OK')
        x, y = pyautogui.position()
        # The project stores coordinates as [x,y,z]. z unknown; use 7 as default or 0
        waypoint = {
            'label': label or f'wp-{int(time.time())}',
            'type': 'walk',
            'coordinate': [int(x), int(y), 7],
            'options': {}
        }
        self.ui_ctx.addWaypoint(waypoint)
        self.log('Captured waypoint', waypoint)

    def toggle_auto_heal(self):
        # simple toggle: enable/disable first health potion
        current = self.ui_ctx.enabledProfile['config'].get('healing', {})
        pot = current.get('potions', {}).get('firstHealthPotion', None)
        if pot is None:
            # ensure structure
            self.ui_ctx.enabledProfile['config'].setdefault('healing', {}).setdefault('potions', {})['firstHealthPotion'] = {
                'enabled': True, 'hotkey': '1', 'slot': 1, 'hpPercentageLessThanOrEqual': 50, 'manaPercentageGreaterThanOrEqual': 0
            }
            self.ui_ctx.db.update(self.ui_ctx.enabledProfile)
            self.auto_heal_btn.configure(text='Toggle Auto-Heal (On)')
            self.log('Auto-heal enabled with default potion config')
            return
        pot['enabled'] = not pot.get('enabled', False)
        self.ui_ctx.db.update(self.ui_ctx.enabledProfile)
        state = 'On' if pot['enabled'] else 'Off'
        self.auto_heal_btn.configure(text=f'Toggle Auto-Heal ({state})')
        self.log('Auto-heal toggled to', state)

    def toggle_bot(self):
        if not self.running:
            # start pilot thread
            try:
                self.pilot_thread = PilotNGThread(self.ui_ctx)
                if hasattr(self.pilot_thread, 'start'):
                    self.pilot_thread.start()
                else:
                    # fallback to running loop in thread
                    t = threading.Thread(target=self._run_pilot_loop, args=(self.pilot_thread,))
                    t.daemon = True
                    t.start()
                self.ui_ctx.play()
                self.start_btn.configure(text='Stop Bot', fg_color='#a02a2a')
                self.running = True
                self.log('Pilot started')
            except Exception as e:
                self.log('Failed to start pilot:', e)
                traceback.print_exc()
        else:
            try:
                self.ui_ctx.pause()
                # Attempt to stop thread gracefully if possible
                if self.pilot_thread and hasattr(self.pilot_thread, 'stop'):
                    try:
                        self.pilot_thread.stop()
                    except Exception:
                        pass
                self.start_btn.configure(text='Start Bot', fg_color='#0a7f3f')
                self.running = False
                self.log('Pilot stopped')
            except Exception as e:
                self.log('Error stopping pilot:', e)
                traceback.print_exc()

    def _run_pilot_loop(self, pilot):
        # fallback loop for non-threaded PilotNGThread-like objects
        while self.running:
            try:
                self.ui_ctx.context = pilot.handleGameData(self.ui_ctx.context)
                self.ui_ctx.context = pilot.handleGameplayTasks(self.ui_ctx.context)
                self.ui_ctx.context = self.ui_ctx.context['ng_tasksOrchestrator'].do(self.ui_ctx.context)
                time.sleep(0.05)
            except Exception as e:
                self.log('Exception in pilot loop:', e)
                traceback.print_exc()
                break

if __name__ == '__main__':
    app = LauncherApp()
    app.mainloop()
