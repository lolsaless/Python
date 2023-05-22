import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog


def split_excel_sheets(file_path):
    # 엑셀 파일 로드
    excel_file = pd.ExcelFile(file_path)

    # 각 시트를 분리하여 개별 엑셀 파일로 저장
    for sheet_name in excel_file.sheet_names:
        df = excel_file.parse(sheet_name)

        # 시트 이름으로 파일명 생성
        sheet_filename = f"{sheet_name}.xlsx"

        # 새로운 엑셀 파일로 저장
        df.to_excel(sheet_filename, index=False)

        print(f"시트 '{sheet_name}'이(가) 성공적으로 분리되었습니다. 저장 위치: {os.path.abspath(sheet_filename)}")


# 파일 선택 대화상자 열기
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(title="엑셀 파일을 선택하세요.", filetypes=[("Excel Files", "*.xlsx")])

# 파일 선택이 이루어진 경우에만 실행
if file_path:
    split_excel_sheets(file_path)
else:
    print("파일 선택이 취소되었습니다.")
