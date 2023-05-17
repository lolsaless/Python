import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from openpyxl import load_workbook

# GUI를 이용하여 폴더 선택
root = tk.Tk()
root.withdraw()
folder_path = filedialog.askdirectory()

# 선택된 폴더 내의 모든 엑셀 파일 읽기
excel_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx') or f.endswith('.xls')]

# 각 엑셀 파일을 읽어서 새로운 엑셀 파일의 시트로 추가
for idx, excel_file in enumerate(excel_files):
    df = pd.read_excel(os.path.join(folder_path, excel_file))
    with pd.ExcelWriter('combined_file.xlsx', engine='openpyxl', mode='a' if idx else 'w') as writer: 
        # 파일 이름에서 확장자 제거하여 시트 이름으로 사용
        df.to_excel(writer, sheet_name=os.path.splitext(excel_file)[0], index=False)

print("Excel files combined successfully!")
