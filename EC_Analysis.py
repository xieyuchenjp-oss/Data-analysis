import pandas as pd
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# ========= Basic configuration (normally no need to change) =========
TARGET_EXTS = [".mpt", ".xlsx", ".xls"]

# Columns for .mpt files
MPT_SOURCE_COLS = ["Ewe/V", "<I>/mA"]
MPT_NEW_COLS = ["Ewe_shifted_V", "Current_mA"]

# Columns for Excel files
EXCEL_SOURCE_COLS = ["Ewe/V", "<I>/mA"]
EXCEL_NEW_COLS = ["Ewe_shifted_V", "Current_mA"]

# Output file name
MERGED_OUTPUT_NAME = "all_data_wide.xlsx"
# ====================================================================


def log(text_widget, msg: str) -> None:
    """Append a message to the GUI log box."""
    if text_widget is not None:
        text_widget.insert(tk.END, msg + "\n")
        text_widget.see(tk.END)


def process_mpt(
    file_path: Path,
    voltage_offset: float,
    apply_voltage_shift: bool,
    area: float,
    convert_current_density: bool,
    text_widget=None,
):
    """Read and process a .mpt file."""
    log(text_widget, f"[INFO] Processing mpt: {file_path.name}")

    # 1) Find header line starting with "mode"
    header_line = None
    with open(file_path, "r", errors="ignore") as f:
        for i, line in enumerate(f):
            if line.startswith("mode"):
                header_line = i
                break

    if header_line is None:
        log(text_widget, "  ⚠ Could not find a line starting with 'mode'; skipping this file.")
        return None

    # 2) Read data
    df = pd.read_csv(
        file_path,
        sep="\t",
        skiprows=header_line,
        header=0,
        engine="python",
    )

    log(text_widget, "  Columns: " + ", ".join(df.columns.astype(str).tolist()))

    # 3) Check required columns
    for col in MPT_SOURCE_COLS:
        if col not in df.columns:
            log(text_widget, f"  ⚠ Required column '{col}' is missing; skipping this file.")
            return None

    # 4) Select and rename columns
    out = df[MPT_SOURCE_COLS].copy()
    out.columns = MPT_NEW_COLS  # ["Ewe_shifted_V", "Current_mA"]

    # 5) Apply voltage shift
    if apply_voltage_shift and voltage_offset not in (None, 0):
        v_col = MPT_NEW_COLS[0]
        out[v_col] = out[v_col] + voltage_offset
        log(text_widget, f"  Added {voltage_offset} V to column '{v_col}'")

    # 6) Convert current to current density (mA/cm²)
    if convert_current_density:
        i_col = MPT_NEW_COLS[1]  # "Current_mA"
        if area is None or area <= 0:
            log(text_widget, "  ⚠ Invalid area; current density was not calculated.")
        else:
            j_col = "CurrentDensity_mA_cm2"
            out[j_col] = out[i_col] / area
            log(text_widget, f"  Calculated '{j_col}' using area = {area} cm²")

    # 7) Reset index and add file name prefix
    out = out.reset_index(drop=True)
    prefix = file_path.stem
    out.columns = [f"{prefix}_{col}" for col in out.columns]

    return out


def process_excel(
    file_path: Path,
    voltage_offset: float,
    apply_voltage_shift: bool,
    area: float,
    convert_current_density: bool,
    text_widget=None,
):
    """Read and process an Excel file (.xlsx / .xls)."""
    log(text_widget, f"[INFO] Processing Excel: {file_path.name}")

    df = pd.read_excel(file_path, sheet_name=0)
    log(text_widget, "  Columns: " + ", ".join(df.columns.astype(str).tolist()))

    # Check required columns
    for col in EXCEL_SOURCE_COLS:
        if col not in df.columns:
            log(text_widget, f"  ⚠ Required column '{col}' is missing; skipping this file.")
            return None

    # Select and rename columns
    out = df[EXCEL_SOURCE_COLS].copy()
    out.columns = EXCEL_NEW_COLS  # ["Ewe_shifted_V", "Current_mA"]

    # Apply voltage shift
    if apply_voltage_shift and voltage_offset not in (None, 0):
        v_col = EXCEL_NEW_COLS[0]
        out[v_col] = out[v_col] + voltage_offset
        log(text_widget, f"  Added {voltage_offset} V to column '{v_col}'")

    # Convert current to current density (mA/cm²)
    if convert_current_density:
        i_col = EXCEL_NEW_COLS[1]
        if area is None or area <= 0:
            log(text_widget, "  ⚠ Invalid area; current density was not calculated.")
        else:
            j_col = "CurrentDensity_mA_cm2"
            out[j_col] = out[i_col] / area
            log(text_widget, f"  Calculated '{j_col}' using area = {area} cm²")

    # Reset index and add file name prefix
    out = out.reset_index(drop=True)
    prefix = file_path.stem
    out.columns = [f"{prefix}_{col}" for col in out.columns]

    return out


def run_merge(
    files,
    voltage_offset: float,
    apply_voltage_shift: bool,
    area: float,
    convert_current_density: bool,
    text_widget=None,
) -> bool:
    """Process selected files and create the merged wide Excel file."""
    # Filter valid files by extension
    valid_files = [
        f for f in files
        if f.is_file() and f.suffix.lower() in [ext.lower() for ext in TARGET_EXTS]
    ]

    if not valid_files:
        log(text_widget, "⚠ No valid .mpt / .xlsx / .xls files selected.")
        return False

    out_folder = valid_files[0].parent
    log(text_widget, f"Output folder: {out_folder}")

    log(text_widget, f"Total selected files: {len(valid_files)}")
    for f in valid_files:
        log(text_widget, "  - " + f.name)

    df_list = []

    for f in valid_files:
        try:
            if f.suffix.lower() == ".mpt":
                out = process_mpt(
                    f, voltage_offset, apply_voltage_shift,
                    area, convert_current_density, text_widget
                )
            else:
                out = process_excel(
                    f, voltage_offset, apply_voltage_shift,
                    area, convert_current_density, text_widget
                )

            if out is not None:
                df_list.append(out)
        except Exception as e:
            log(text_widget, f"  ❌ Error while processing {f.name}: {repr(e)}")

    if not df_list:
        log(text_widget, "⚠ No files were successfully processed; nothing was saved.")
        return False

    # Horizontal merge (side-by-side)
    merged = pd.concat(df_list, axis=1)

    out_file = out_folder / MERGED_OUTPUT_NAME
    merged.to_excel(out_file, index=False)
    log(text_widget, f"\n✅ Merged file created: {out_file.name}")

    return True


# ========================== GUI ==========================

def main_gui() -> None:
    root = tk.Tk()
    root.title("MPT/Excel Merge Tool (Voltage shift & Current density)")

    # Top frame: parameters
    frm_top = tk.Frame(root)
    frm_top.pack(padx=10, pady=5, fill=tk.X)

    # Voltage offset
    tk.Label(frm_top, text="Voltage offset (V):").grid(row=0, column=0, sticky="w")
    voltage_var = tk.StringVar(value="1.025")
    tk.Entry(frm_top, textvariable=voltage_var, width=10).grid(row=0, column=1, sticky="w")

    apply_shift_var = tk.BooleanVar(value=True)
    tk.Checkbutton(
        frm_top,
        text="Apply voltage shift",
        variable=apply_shift_var,
    ).grid(row=0, column=2, padx=10, sticky="w")

    # Electrode area & current density
    tk.Label(frm_top, text="Electrode area (cm²):").grid(row=1, column=0, sticky="w")
    area_var = tk.StringVar(value="1.0")
    tk.Entry(frm_top, textvariable=area_var, width=10).grid(row=1, column=1, sticky="w")

    convert_j_var = tk.BooleanVar(value=True)
    tk.Checkbutton(
        frm_top,
        text="Convert current to current density (mA/cm²)",
        variable=convert_j_var,
    ).grid(row=1, column=2, padx=10, sticky="w")

    # Button frame
    frm_btn = tk.Frame(root)
    frm_btn.pack(padx=10, pady=5, fill=tk.X)

    # Log box
    log_box = scrolledtext.ScrolledText(root, width=80, height=18)
    log_box.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    def on_run() -> None:
        # Select multiple files
        file_paths = filedialog.askopenfilenames(
            title="Select mpt / Excel files to process",
            filetypes=[
                ("Data files", "*.mpt *.xlsx *.xls"),
                ("All files", "*.*"),
            ],
        )
        if not file_paths:
            return

        files = [Path(p) for p in file_paths]

        # Parse parameters
        try:
            v_offset = float(voltage_var.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Voltage offset must be a number.")
            return

        try:
            area_str = area_var.get().strip()
            area_val = float(area_str) if area_str else None
        except ValueError:
            area_val = None

        apply_shift = apply_shift_var.get()
        convert_j = convert_j_var.get()

        log_box.delete("1.0", tk.END)
        success = run_merge(
            files,
            v_offset,
            apply_shift,
            area_val,
            convert_j,
            text_widget=log_box,
        )

        if success:
            out_folder = files[0].parent
            messagebox.showinfo(
                "Done",
                f"Processing finished.\nOutput file:\n{out_folder / MERGED_OUTPUT_NAME}",
            )
        else:
            messagebox.showwarning(
                "No output",
                "No files were successfully processed; no merged file was created.",
            )

    tk.Button(frm_btn, text="Select files and run", command=on_run).pack(
        side=tk.LEFT, padx=5, pady=5
    )

    root.mainloop()


if __name__ == "__main__":
    main_gui()
