Here’s a short step-by-step guide for general users:

---

### 1. Install (first time only)

1. Make sure **Python** is installed.

2. Install required packages:

   ```bash
   pip install pandas openpyxl
   ```
   or
   ```bash
   python -m pip install -U pip
   ```bash

4. Save the script as **`merge_mpt_excel_gui.pyw`**.

---

### 2. Prepare your data

1. Make sure your files are in **.mpt / .xlsx / .xls** format.
2. Check that they contain columns named (or mapped in the code to):

   * `Ewe/V` (potential)
   * `<I>/mA` (current)

---

### 3. Run the program

1. **Double-click** `merge_mpt_excel_gui.pyw`.
2. In the window:

   * Enter **Voltage offset (V)** (e.g. `1.025` or `0`).
   * Enter **Electrode area (cm²)** (e.g. `1.0` or `0.196`).
   * Tick/untick:

     * **Apply voltage shift**
     * **Convert current to current density (mA/cm²)**
3. Click **“Select files and run”**.
4. In the file dialog, select one or more `.mpt / .xlsx / .xls` files → click **Open**.

---

### 4. Check the result

1. After processing, an Excel file is created in the folder of the **first selected file**.
2. File name: **`all_data_wide.xlsx`**.
3. Open it in Excel: each input file has its own block of columns, e.g.
   `sample1_Ewe_shifted_V`, `sample1_Current_mA`, `sample1_CurrentDensity_mA_cm2`, etc.
