import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import os
import json

CONFIG_FILE = "settings.json"

# Load persistent settings
default_settings = {
    "theme": "cosmo",
    "default_input_dir": "",
    "default_output_dir": ""
}

if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r") as f:
            saved = json.load(f)
            default_settings.update(saved)
    except Exception:
        pass  # Ignore malformed files

# GUI setup
style = tb.Style()
root = style.master
style.theme_use(default_settings["theme"])
root.title("BizHawk/FCEUX to Yuzu TAS Converter")

# State variables
delay_frames_var = tb.IntVar(value=202)
sync_correction_var = tb.BooleanVar(value=False)
first_frame_a_var = tb.BooleanVar(value=True)
input_file_path = tb.StringVar()
output_file_path = tb.StringVar(value="script0-1.txt")
tas_type_var = tb.StringVar(value="BizHawk")

# Persistent config variables
default_input_dir_var = tb.StringVar(value=default_settings["default_input_dir"])
default_output_path_var = tb.StringVar(value=default_settings["default_output_dir"])
theme_choice_var = tb.StringVar(value=default_settings["theme"])

# Constants
SYNC_CORRECTION_INTERVAL = 606

# Button mappings
bizhawk_mapping = {
    0: "KEY_DUP", 1: "KEY_DDOWN", 2: "KEY_DLEFT", 3: "KEY_DRIGHT",
    4: "KEY_START", 5: "KEY_SELECT", 6: "KEY_B", 7: "KEY_A",
}

fceux_char_mapping = {
    'A': "KEY_A", 'B': "KEY_B", 'S': "KEY_SELECT", 'T': "KEY_START",
    'U': "KEY_DUP", 'D': "KEY_DDOWN", 'L': "KEY_DLEFT", 'R': "KEY_DRIGHT",
}

# --- Settings persistence ---
def save_settings():
    settings = {
        "theme": theme_choice_var.get(),
        "default_input_dir": default_input_dir_var.get(),
        "default_output_dir": default_output_path_var.get()
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(settings, f, indent=2)

# --- Functions ---
def select_input_file():
    initial_dir = default_input_dir_var.get() or os.getcwd()
    file_path = filedialog.askopenfilename(title="Select Input TAS File", initialdir=initial_dir)
    if file_path:
        input_file_path.set(file_path)

def select_output_file():
    initial_dir = default_output_path_var.get() or os.getcwd()
    file_path = filedialog.asksaveasfilename(title="Save Converted File As", defaultextension=".txt", initialdir=initial_dir)
    if file_path:
        output_file_path.set(file_path)

def convert_file():
    input_path = input_file_path.get()
    output_path = output_file_path.get()
    delay_frames = delay_frames_var.get()
    sync_correction = sync_correction_var.get()
    first_frame_key_a = first_frame_a_var.get()

    if not input_path or not output_path:
        messagebox.showerror("Error", "Please specify both input and output file paths.")
        return

    try:
        with open(input_path, "r") as f:
            lines = f.readlines()

        if tas_type_var.get() == "FCEUX":
            input_lines = [line.strip() for line in lines if line.strip().startswith('|') and line.count('|') >= 3]
        else:
            input_lines = [line.strip() for line in lines if line.strip().startswith('|') and line.count('|') == 3]

        converted = []

        for i in range(delay_frames):
            if i == 0 and (delay_frames == 202 or first_frame_key_a):
                converted.append(f"{i:03} KEY_A 0;0 0;0")
            else:
                converted.append(f"{i:03} NONE 0;0 0;0")

        frame_number = delay_frames
        inserted = 0
        for idx, line in enumerate(input_lines):
            if sync_correction and (inserted + 1) % SYNC_CORRECTION_INTERVAL == 0:
                converted.append(f"{frame_number:03} NONE 0;0 0;0")
                frame_number += 1
                inserted = 0
            inserted += 1

            parts = line.split('|')
            if len(parts) < 3:
                continue
            bitstring = parts[2].strip()

            if tas_type_var.get() == "FCEUX":
                buttons = [fceux_char_mapping[char] for char in bitstring if char in fceux_char_mapping]
            else:
                buttons = [bizhawk_mapping[bit] for bit, char in enumerate(bitstring) if char != '.' and bit in bizhawk_mapping]

            btn_output = ';'.join(buttons) if buttons else 'NONE'
            converted.append(f"{frame_number:03} {btn_output} 0;0 0;0")
            frame_number += 1

        with open(output_path, "w") as f:
            f.write('\n'.join(converted))

        messagebox.showinfo("Success", f"Converted {len(input_lines)} frames with {delay_frames} delay frames.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to convert: {e}")

def apply_theme():
    new_theme = theme_choice_var.get()
    style.theme_use(new_theme)
    save_settings()

def set_default_output_folder():
    folder = filedialog.askdirectory(title="Select Default Output Folder")
    if folder:
        default_output_path_var.set(folder)
        save_settings()

def set_default_input_folder():
    folder = filedialog.askdirectory(title="Select Default Input Folder")
    if folder:
        default_input_dir_var.set(folder)
        save_settings()

# --- Tabs ---
notebook = tb.Notebook(root)
notebook.pack(fill=BOTH, expand=YES)

# --- TAS Converter Tab ---
converter_tab = tb.Frame(notebook, padding=15)
notebook.add(converter_tab, text="TAS Converter")

tb.Label(converter_tab, text="Input File:").grid(row=0, column=0, sticky=E)
tb.Entry(converter_tab, textvariable=input_file_path, width=50).grid(row=0, column=1)
tb.Button(converter_tab, text="Browse", command=select_input_file).grid(row=0, column=2)

tb.Label(converter_tab, text="Output File:").grid(row=1, column=0, sticky=E)
tb.Entry(converter_tab, textvariable=output_file_path, width=50).grid(row=1, column=1)
tb.Button(converter_tab, text="Browse", command=select_output_file).grid(row=1, column=2)

tb.Label(converter_tab, text="Delay Frames:").grid(row=2, column=0, sticky=E)
tb.Entry(converter_tab, textvariable=delay_frames_var, width=10, foreground="gray").grid(row=2, column=1, sticky=W)

tb.Label(converter_tab, text="TAS Type:").grid(row=3, column=0, sticky=E)
tb.OptionMenu(converter_tab, tas_type_var, "BizHawk", "BizHawk", "FCEUX").grid(row=3, column=1, sticky=W)

tb.Checkbutton(converter_tab, text="First frame is KEY_A", variable=first_frame_a_var).grid(row=4, column=1, sticky=W)

tb.Button(converter_tab, text="Convert", command=convert_file, width=20, bootstyle=SUCCESS).grid(row=5, column=1, pady=15)

# --- Experimental Features Tab ---
exp_tab = tb.Frame(notebook, padding=15)
notebook.add(exp_tab, text="Experimental Features")

tb.Label(exp_tab, text="Select Target Console:").pack(anchor=W, pady=(0, 10))
tb.Button(exp_tab, text="NES", width=20).pack(pady=5)
tb.Button(exp_tab, text="N64", width=20).pack(pady=5)
tb.Button(exp_tab, text="Switch", width=20).pack(pady=5)

# --- Options Tab ---
options_tab = tb.Frame(notebook, padding=15)
notebook.add(options_tab, text="Options")

tb.Label(options_tab, text="Select Theme:").grid(row=0, column=0, sticky=E, pady=5)
tb.OptionMenu(options_tab, theme_choice_var, theme_choice_var.get(), *style.theme_names(), command=lambda _: apply_theme()).grid(row=0, column=1, sticky=W)

tb.Label(options_tab, text="Default TAS Input Folder:").grid(row=1, column=0, sticky=E, pady=5)
tb.Entry(options_tab, textvariable=default_input_dir_var, width=40).grid(row=1, column=1, sticky=W)
tb.Button(options_tab, text="Set", command=set_default_input_folder).grid(row=1, column=2, padx=5)

tb.Label(options_tab, text="Default Output Folder:").grid(row=2, column=0, sticky=E, pady=5)
tb.Entry(options_tab, textvariable=default_output_path_var, width=40).grid(row=2, column=1, sticky=W)
tb.Button(options_tab, text="Set", command=set_default_output_folder).grid(row=2, column=2, padx=5)

# About section
ttk_separator = tb.Separator(options_tab, orient=HORIZONTAL)
ttk_separator.grid(row=3, columnspan=3, sticky="ew", pady=10)

tb.Label(options_tab, text="About", font=("PT Sans Narrow", 11, "bold")).grid(row=4, column=0, sticky=W, pady=(0, 5))
about_text = (
    "TAS Converter v1.2\n"
    "Convert BizHawk/FCEUX TAS files to Yuzu format.\n"
    "Developed by Vim\n"
    "https://github.com/vimxd/nwctas"
)
tb.Label(options_tab, text=about_text, justify=LEFT).grid(row=5, column=0, columnspan=3, sticky=W)

# --- Main Loop ---
root.mainloop()
