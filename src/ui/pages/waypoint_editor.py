import os
import json
import customtkinter
from tkinter import Listbox, END, StringVar, Entry, Label, Button

DATA_DIR = os.path.join('src', 'data', 'imported', 'current-repo')

class WaypointEditor(customtkinter.CTkToplevel):
    def __init__(self, context):
        super().__init__()
        self.context = context
        self.title('Waypoint Editor')
        self.resizable(False, False)

        self.listbox = Listbox(self, width=50, height=12)
        self.listbox.grid(row=0, column=0, rowspan=6, padx=8, pady=8)

        refresh = customtkinter.CTkButton(self, text='Refresh', command=self.refresh)
        refresh.grid(row=0, column=1, padx=8, pady=4)

        Label(self, text='Label:').grid(row=1, column=1, sticky='w')
        self.label_entry = Entry(self, width=30)
        self.label_entry.grid(row=2, column=1, padx=8, pady=2)

        Label(self, text='Type:').grid(row=3, column=1, sticky='w')
        self.type_entry = Entry(self, width=30)
        self.type_entry.grid(row=4, column=1, padx=8, pady=2)

        Label(self, text='Coordinate (x,y,z):').grid(row=5, column=1, sticky='w')
        self.coord_entry = Entry(self, width=30)
        self.coord_entry.grid(row=6, column=1, padx=8, pady=2)

        save_btn = customtkinter.CTkButton(self, text='Save to file', command=self.save_to_file)
        save_btn.grid(row=7, column=1, padx=8, pady=6)

        load_btn = customtkinter.CTkButton(self, text='Load into profile', command=self.load_into_profile)
        load_btn.grid(row=8, column=1, padx=8, pady=6)

        self.refresh()

    def refresh(self):
        self.listbox.delete(0, END)
        if not os.path.isdir(DATA_DIR):
            return
        for f in sorted(os.listdir(DATA_DIR)):
            if f.lower().endswith('.converted.json') or f.lower().endswith('.json'):
                self.listbox.insert(END, f)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)

    def on_select(self, event=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        fname = self.listbox.get(sel[0])
        full = os.path.join(DATA_DIR, fname)
        try:
            with open(full, 'r') as fh:
                data = json.load(fh)
                if isinstance(data, list) and len(data) > 0:
                    wp = data[0]
                elif isinstance(data, dict):
                    wp = data
                else:
                    wp = None
                if wp:
                    self.label_entry.delete(0, END); self.label_entry.insert(0, wp.get('label',''))
                    self.type_entry.delete(0, END); self.type_entry.insert(0, wp.get('type',''))
                    coord = wp.get('coordinate')
                    if coord:
                        s = f"{coord[0]},{coord[1]},{coord[2]}"
                    else:
                        s = ''
                    self.coord_entry.delete(0, END); self.coord_entry.insert(0, s)
                    self.current_fname = fname
        except Exception:
            return

    def save_to_file(self):
        if not hasattr(self, 'current_fname'):
            return
        full = os.path.join(DATA_DIR, self.current_fname)
        try:
            label = self.label_entry.get()
            typ = self.type_entry.get()
            coord_text = self.coord_entry.get().strip()
            coord = None
            if coord_text:
                parts = coord_text.split(',')
                if len(parts) >= 3:
                    try:
                        coord = [int(parts[0]), int(parts[1]), int(parts[2])]
                    except Exception:
                        coord = None
            wp = {'label': label, 'type': typ, 'coordinate': coord, 'options': {}}
            with open(full, 'w') as fh:
                json.dump([wp], fh, indent=2)
            self.refresh()
        except Exception as e:
            print('Failed saving', e)

    def load_into_profile(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        fname = self.listbox.get(sel[0])
        full = os.path.join(DATA_DIR, fname)
        try:
            with open(full, 'r') as fh:
                data = json.load(fh)
                if isinstance(data, list):
                    self.context.loadScript(data)
                else:
                    self.context.loadScript([data])
                print('Loaded', fname, 'into profile')
        except Exception as e:
            print('Load failed', e)
