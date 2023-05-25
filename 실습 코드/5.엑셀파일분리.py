import pandas as pd
from tkinter import Tk, filedialog

# 파일 선택 대화 상자를 통해 엑셀 파일 선택
Tk().withdraw()
file_path = filedialog.askopenfilename(filetypes=[('Excel Files', '*.xlsx')])

# 엑셀 파일을 DataFrame으로 읽어오기
xls = pd.ExcelFile(file_path)

# 각 시트를 분리하여 개별 엑셀 파일로 저장
for sheet_name in xls.sheet_names:
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    new_file_name = f"{sheet_name}.xlsx"
    df.to_excel(new_file_name, index=False)
    print(f"{new_file_name} 파일이 생성되었습니다.")
