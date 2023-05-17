import pandas as pd
from tkinter import filedialog
from tkinter import Tk

# 창 생성
root = Tk()

# 창 숨기기
root.withdraw()

# 파일 선택 대화 상자 띄우기
filename = filedialog.askopenfilename()

# 엑셀 파일 읽기
xlsx = pd.ExcelFile(filename)

# 각 시트를 돌며 개별 엑셀 파일로 저장
for sheet in xlsx.sheet_names:
    df = pd.read_excel(xlsx, sheet_name=sheet)
    df.to_excel(f'{sheet}.xlsx', index=False)
