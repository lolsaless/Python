import os
import pandas as pd
from tkinter import filedialog
from tkinter import Tk
from openpyxl import load_workbook

# GUI를 통한 폴더 선택
root = Tk()
root.withdraw()  # 창이 보이지 않도록 하기
folder_selected = filedialog.askdirectory()  # 폴더 선택 대화상자 열기
print('Selected folder:', folder_selected)

# 선택한 폴더의 모든 엑셀 파일 읽기
file_list = os.listdir(folder_selected)
excel_files = [file for file in file_list if file.endswith(".xlsx") or file.endswith(".xls")]

# 새 엑셀 파일 생성
with pd.ExcelWriter('merged.xlsx') as writer:
    for excel_file in excel_files:
        try:
            file_path = os.path.join(folder_selected, excel_file)
            excel_df = pd.read_excel(file_path)
            excel_df.to_excel(writer, sheet_name=os.path.splitext(excel_file)[0], index=False)
        except Exception as e:
            print(f"An error occurred with file {excel_file}: {str(e)}")
            continue

print("All excel files have been merged.")
