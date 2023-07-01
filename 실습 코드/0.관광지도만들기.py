import tkinter as tk
from tkinter import filedialog
import pandas as pd
import folium

# UI를 생성하는 클래스
class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("관광지 정보 지도")
        self.root.geometry("400x200")

        # 엑셀 파일 선택 버튼
        self.select_button = tk.Button(self.root, text="엑셀 파일 선택", command=self.select_excel_file)
        self.select_button.pack(pady=20)

    # 엑셀 파일 선택 함수
    def select_excel_file(self):
        filetypes = (("Excel files", "*.xlsx"), ("All files", "*.*"))
        file_path = filedialog.askopenfilename(title="Select Excel File", filetypes=filetypes)

        # 엑셀 파일 읽기
        if file_path:
            self.read_excel(file_path)

    # 엑셀 파일 읽기 함수
    def read_excel(self, file_path):
        df = pd.read_excel(file_path, sheet_name="Sheet1")

        # 관광지명, 위도, 경도 추출
        locations = df["관광지"].tolist()
        latitudes = df["위도"].tolist()
        longitudes = df["경도"].tolist()

        # Folium 지도 생성
        map = folium.Map(location=[latitudes[0], longitudes[0]], zoom_start=12)

        # 마커 추가
        for location, lat, lng in zip(locations, latitudes, longitudes):
            tooltip = folium.Tooltip(text=location)
            folium.Marker([lat, lng], tooltip=tooltip).add_to(map)

        # Folium 지도 HTML 파일로 저장
        map.save("tourist_map.html")
        print("지도가 생성되었습니다.")

# 메인 함수
def main():
    root = tk.Tk()
    gui = GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
