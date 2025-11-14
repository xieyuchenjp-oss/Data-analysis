1. What does the script do?
•	Scans the folder where ecauto.py is located
•	Finds all:
o	.mpt (EC-Lab ASCII)
o	.xlsx / .xls
•	From each file, extracts two columns (you define their names)
•	Optionally adds an offset (e.g. +1.025) to the first column
•	Each file contributes its own pair of columns side by side
•	Creates one Excel file: all_data_wide.xlsx
________________________________________
2. How to organize the files?
1.	Create a folder, e.g.:
C:\Users\labuser\Desktop\ECauto\
2.	Put ecauto.py in this folder
3.	Put all .mpt / .xlsx / .xls files to be processed in the same folder
Example:
ECauto\
 ├─ ecauto.py
 ├─ sample1.mpt
 ├─ sample2.mpt
 ├─ sample3.xlsx
 └─ sample4.xlsx
________________________________________
3. What can you configure?
At the top of ecauto.py:
TARGET_EXTS = [".mpt", ".xlsx", ".xls"]

MPT_SOURCE_COLS = ["Ewe/V", "<I>/mA"]
MPT_NEW_COLS    = ["Ewe_shifted_V", "Current_mA"]
MPT_ADD_TO_FIRST = 1.025   # set to 0 or None if no offset

EXCEL_SOURCE_COLS = ["Ewe/V", "<I>/mA"]
EXCEL_NEW_COLS    = ["Ewe_shifted_V", "Current_mA"]
EXCEL_ADD_TO_FIRST = 1.025

MERGED_OUTPUT_NAME = "all_data_wide.xlsx"
You may:
•	Change column names:
o	MPT_SOURCE_COLS / EXCEL_SOURCE_COLS: column names as they appear in your raw files
o	MPT_NEW_COLS / EXCEL_NEW_COLS: desired output names (e.g. English)
•	Change offset:
o	If you don’t want +1.025, set MPT_ADD_TO_FIRST / EXCEL_ADD_TO_FIRST to 0 or None
•	Change output file name:
o	e.g. MERGED_OUTPUT_NAME = "CV_merged.xlsx"
________________________________________
4. How to run it?
1.	Make sure packages are installed:
2.	python -m pip install pandas openpyxl
3.	Open the folder containing ecauto.py and your data files
4.	Shift + right-click in empty space →
“Open PowerShell window here” or “Open command window here”
5.	Run:
6.	python ecauto.py
or
py ecauto.py
________________________________________
5. What is the result?
•	A single Excel file is created in the same folder:
•	all_data_wide.xlsx
•	If you have 4 files and extract 2 columns from each, you get 8 columns total, e.g.:
file1_Ewe_shifted_V	file1_Current_mA	file2_Ewe_shifted_V	file2_Current_mA	…
Each file’s data occupies its own pair of columns; they are not mixed into one.
