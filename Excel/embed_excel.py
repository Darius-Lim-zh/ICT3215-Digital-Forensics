import base64
import openpyxl
import os
import sys
from win32com.client import Dispatch

def embed_python_script_and_vba(original_excel_path, python_file_path, output_excel_path, vba_macro_path):
    # Temporary .xlsx path to avoid format issues
    temp_xlsx_path = output_excel_path.replace(".xlsm", ".xlsx")

    # Load the existing Excel file and preserve its content
    workbook = openpyxl.load_workbook(original_excel_path)
    sheet = workbook.active  # Use the active sheet or specify a sheet name if needed

    # Read the Python file and encode it as base64
    with open(python_file_path, "rb") as f:
        encoded_script = base64.b64encode(f.read()).decode('utf-8')

    # Insert the encoded Python script into cell XFD1048576 (last cell in the sheet)
    sheet["XFD1048576"] = encoded_script

    # Save the workbook temporarily as a .xlsx file
    workbook.save(temp_xlsx_path)

    # Add VBA macro and save as .xlsm
    add_vba_macro(temp_xlsx_path, output_excel_path, vba_macro_path)

    # Remove the temporary .xlsx file
    os.remove(temp_xlsx_path)

def add_vba_macro(input_excel_path, output_excel_path, vba_macro_path):
    # Read VBA macro from text file
    with open(vba_macro_path, "r") as f:
        vba_code = f.read()

    # Use win32com to open the Excel file and add the VBA code
    excel_app = Dispatch("Excel.Application")
    excel_app.Visible = False

    try:
        # Open the temporary .xlsx file
        print(f"Opening workbook: {input_excel_path}")
        workbook = excel_app.Workbooks.Open(os.path.abspath(input_excel_path))

        # Directly insert VBA code into ThisWorkbook
        print("Inserting VBA macro into ThisWorkbook...")
        workbook.VBProject.VBComponents("ThisWorkbook").CodeModule.AddFromString(vba_code)
        print("VBA macro inserted into ThisWorkbook.")

        # Save the workbook as a macro-enabled workbook (.xlsm)
        print(f"Saving workbook as macro-enabled .xlsm: {output_excel_path}")
        workbook.SaveAs(os.path.abspath(output_excel_path), FileFormat=52)  # 52 = .xlsm for macro-enabled workbook
        workbook.Close(False)
        print("Workbook saved and closed.")

    except Exception as e:
        print(f"Error adding VBA macro: {e}")
    finally:
        excel_app.Quit()

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python embed_excel.py <original_excel> <python_script> <output_excel> <vba_macro_path>")
    else:
        original_excel_path = sys.argv[1]
        python_script = sys.argv[2]
        output_excel = sys.argv[3]
        vba_macro_path = sys.argv[4]
        embed_python_script_and_vba(original_excel_path, python_script, output_excel, vba_macro_path)
