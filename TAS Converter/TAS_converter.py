import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import os

# GUI window setup
root = tb.Window(themename="cosmo")  # OS default styled theme
root.title("BizHawk/FCEUX to Yuzu TAS Converter")

# State variables
delay_frames_var = tb.IntVar(value=202)
sync_correction_var = tb.BooleanVar(value=True)
first_frame_a_var = tb.BooleanVar(value=False)
input_file_path = tb.StringVar()
output_file_path = tb.StringVar(value="script0-1.txt")
tas_type_var = tb.StringVar(value="BizHawk")

# Constants
SYNC_CORRECTION_INTERVAL = 606

# Button mappings
bizhawk_mapping = {
    0: "KEY_DUP",
    1: "KEY_DDOWN",
    2: "KEY_DLEFT",
    3: "KEY_DRIGHT",
    4: "KEY_START",
    5: "KEY_SELECT",
    6: "KEY_B",
    7: "KEY_A",
}

# FCEUX character-based mapping
fceux_char_mapping = {
    'A': "KEY_A",
    'B': "KEY_B",
    'S': "KEY_SELECT",
    'T': "KEY_START",
    'U': "KEY_DUP",
    'D': "KEY_DDOWN",
    'L': "KEY_DLEFT",
    'R': "KEY_DRIGHT",
}

def select_input_file():
    file_path = filedialog.askopenfilename(title="Select Input TAS File")
    if file_path:
        input_file_path.set(file_path)
        suggested_output = os.path.splitext(file_path)[0] + "_converted.txt"
        output_file_path.set(suggested_output)

def select_output_file():
    file_path = filedialog.asksaveasfilename(title="Save Converted File As", defaultextension=".txt")
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

# --- GUI Layout ---
frame = tb.Frame(root, padding=15)
frame.pack(fill=BOTH, expand=YES)

tb.Label(frame, text="Input File:").grid(row=0, column=0, sticky=E)
tb.Entry(frame, textvariable=input_file_path, width=50).grid(row=0, column=1)
tb.Button(frame, text="Browse", command=select_input_file).grid(row=0, column=2)

tb.Label(frame, text="Output File:").grid(row=1, column=0, sticky=E)
tb.Entry(frame, textvariable=output_file_path, width=50).grid(row=1, column=1)
tb.Button(frame, text="Browse", command=select_output_file).grid(row=1, column=2)

tb.Label(frame, text="Delay Frames:").grid(row=2, column=0, sticky=E)
tb.Entry(frame, textvariable=delay_frames_var, width=10, foreground="gray").grid(row=2, column=1, sticky=W)

tb.Label(frame, text="TAS Type:").grid(row=3, column=0, sticky=E)
tb.OptionMenu(frame, tas_type_var, "BizHawk", "BizHawk", "FCEUX").grid(row=3, column=1, sticky=W)

tb.Checkbutton(frame, text="EXPERIMENTAL: Enable sync correction (every 606 frames)", variable=sync_correction_var).grid(row=4, column=1, sticky=W)
tb.Checkbutton(frame, text="First frame is KEY_A", variable=first_frame_a_var).grid(row=5, column=1, sticky=W)

tb.Button(frame, text="Convert", command=convert_file, width=20, bootstyle=SUCCESS).grid(row=6, column=1, pady=15)

root.mainloop()
