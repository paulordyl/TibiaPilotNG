import os
import json
import customtkinter
from tkinter import messagebox, Listbox, END

class ImporterPage(customtkinter.CTkToplevel):
    def __init__(self, context):
        super().__init__()
        self.context = context
        self.title('Importer')
        self.resizable(False, False)

        self.import_dir = os.path.join('src', 'data', 'imported')
        self.repo_dir = os.path.join(self.import_dir, 'current-repo')

        self.listbox = Listbox(self, width=60, height=10)
        self.listbox.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        refreshBtn = customtkinter.CTkButton(self, text='Refresh', command=self.refresh)
        refreshBtn.grid(row=1, column=0, padx=10, pady=8, sticky='w')

        loadBtn = customtkinter.CTkButton(self, text='Load into profile', command=self.load_selected)
        loadBtn.grid(row=1, column=1, padx=10, pady=8, sticky='e')

        self.refresh()

    def refresh(self):
        self.listbox.delete(0, END)
        if not os.path.isdir(self.repo_dir):
            messagebox.showinfo('Importer', f'No imported files found in {self.repo_dir}')
            return
        for f in sorted(os.listdir(self.repo_dir)):
            if f.lower().endswith(('.json', '.yaml', '.yml')):
                self.listbox.insert(END, f)

    def load_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning('Importer', 'Select a file first')
            return
        fname = self.listbox.get(sel[0])
        full = os.path.join(self.repo_dir, fname)
        try:
            with open(full, 'r') as fh:
                data = json.load(fh)
                # Expecting a list of waypoint dicts
                if not isinstance(data, list):
                    messagebox.showerror('Importer', 'Imported file is not a list of waypoints')
                    return
                self.context.loadScript(data)
                messagebox.showinfo('Importer', f'Loaded {fname} into current profile')
        except Exception as e:
            messagebox.showerror('Importer', f'Error loading file: {e}')
