from flask import Flask, jsonify, render_template_string, request
import pandas as pd
import folium
from tkinter import Tk, filedialog
import webbrowser
import threading
import sys
import os
import signal
import platform

# Flask 앱 초기화
app = Flask(__name__)

# 엑셀 파일 로드
def load_excel():
    """엑셀 파일 선택"""
    Tk().withdraw()  # Tkinter GUI 숨기기
    file_path = filedialog.askopenfilename(
        title="엑셀 파일 선택",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    
    if file_path:
        return pd.read_excel(file_path), file_path
    
    raise FileNotFoundError("엑셀 파일이 선택되지 않았습니다.")

try:
    # 엑셀 파일 로드 시도
    df, EXCEL_PATH = load_excel()
except FileNotFoundError as e:
    # 엑셀 파일이 선택되지 않은 경우 프로그램 종료
    print(str(e))
    exit()

# "완료" 열 추가 (없으면)
if "완료" not in df.columns:
    df["완료"] = ""  # 기본값은 빈 문자열로 설정

# 시설군별 색상 매핑
facility_colors = {
    "학원": "blue",
    "지하역사": "gray",
    "장례식장": "white",
    "인터넷컴퓨터게임시설제공업의영업시설": "red",
    "의료기관": "green",
    "영화상영관": "yellow",
    "업무시설": "purple",
    "어린이집": "orange",
    "실내주차장": "brown",
    "실내어린이놀이시설": "pink",
    "산후조리원": "lightblue",  # 색상 이름에 공백이 없도록 수정
    "박물관": "beige",
    "목욕장업의 영업시설": "teal",
    "도서관": "gold",
    "대규모 점포": "silver",
    "노인요양시설": "lavender"
}


def get_facility_color(row):
    """시설군에 따른 색상 반환."""
    if row["완료"] == "완료":
        return "black"  # 완료된 항목은 검은색으로 표시
    return facility_colors.get(row["시설군"], "green")  # 기본 색상은 녹색


def calculate_progress():
    """시군별 완료 진행 상황 계산."""
    # 각 시군에 대해 완료된 건수와 전체 건수를 계산하여 문자열로 반환
    if "시군" not in df.columns:
        raise KeyError("'시군' 열이 데이터프레임에 존재하지 않습니다.")
    progress = df.groupby("시군").apply(lambda x: f"{(x['완료'] == '완료').sum()}건 완료 / {len(x)}건")
    return progress.to_dict()


def calculate_total_progress():
    """전체 완료 진행 상황 계산."""
    total_completed = (df["완료"] == "완료").sum()
    total_count = len(df)
    return f"총 완료: {total_completed}건 / 전체: {total_count}건"


@app.route("/")
def map_view():
    """지도와 초기 상태를 렌더링."""
    # 지도 생성 - 위도와 경도의 평균 값을 중심으로 설정
    map_center = [df["Latitude"].mean(), df["Longitude"].mean()]
    mymap = folium.Map(location=map_center, zoom_start=12)

    # 마커를 추가
    for _, row in df.iterrows():
        color = get_facility_color(row)  # 각 시설의 색상을 결정
        marker = folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=(f"""
                <div style='width:300px; height:auto;'>
                    <b>시설명:</b> {row['시설명']}<br>
                    <b>시설군:</b> {row['시설군']}<br>
                    <b>주소:</b> {row['주소']}<br>
                    <button onclick='markAsComplete({row.name})'>완료</button>
                    <button onclick='cancelCompletion({row.name})'>취소</button>
                </div>
            """),
            icon=folium.Icon(color=color),  # 마커의 색상 설정
        )
        marker.add_to(mymap)  # 지도에 마커 추가

    # 지도 HTML 생성
    map_html = mymap.get_root().render()

    # 진행 상황 계산
    progress_info = calculate_progress()
    total_progress = calculate_total_progress()
    progress_html = "<div style='position: fixed; top: 10px; right: 10px; background: rgba(255, 255, 255, 0.9); padding: 10px; border: 1px solid black; z-index: 1000;'>"
    progress_html += f"<h4>{total_progress}</h4>"
    progress_html += "<h4>각 시군별 진행 상황</h4>"
    for region, status in progress_info.items():
        progress_html += f"<p><b>{region}:</b> {status}</p>"  # 각 시군의 진행 상황을 추가
    progress_html += "<button onclick='shutdownServer()' style='margin-top: 10px; padding: 5px 10px;'>종료</button>"
    progress_html += "</div>"

    # JavaScript 추가 (마커 완료 처리 기능 및 서버 종료 기능)
    map_html += progress_html
    map_html += """
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        function markAsComplete(index) {
            // 마커를 완료 상태로 업데이트하기 위한 AJAX POST 요청
            $.post("/update", { id: index, action: 'complete' }, function(response) {
                if (response.success) {
                    alert("마커 상태가 업데이트되었습니다.");
                    location.reload(); // 새로고침
                } else {
                    alert("업데이트 실패: " + response.error);
                }
            });
        }

        function cancelCompletion(index) {
            // 마커의 완료 상태를 취소하기 위한 AJAX POST 요청
            $.post("/update", { id: index, action: 'cancel' }, function(response) {
                if (response.success) {
                    alert("마커 상태가 취소되었습니다.");
                    location.reload(); // 새로고침
                } else {
                    alert("취소 실패: " + response.error);
                }
            });
        }

        function shutdownServer() {
            // 서버 종료 요청
            if (confirm('프로그램을 종료하시겠습니까?')) {
                $.get('/shutdown', function(response) {
                    alert(response);
                    window.open('', '_self', '');
                    window.close();
                });
            }
        }
    </script>
    """
    return render_template_string(map_html)


@app.route("/update", methods=["POST"])
def update_marker():
    """마커를 완료 상태로 업데이트 또는 취소."""
    try:
        marker_id = int(request.form["id"])
        action = request.form["action"]
        if action == 'complete':
            df.loc[marker_id, "완료"] = "완료"  # "완료" 열에 상태 저장
        elif action == 'cancel':
            df.loc[marker_id, "완료"] = ""  # 완료 상태 취소
        df.to_excel(EXCEL_PATH, index=False)  # 엑셀 파일에 변경 사항 저장
        return jsonify(success=True)
    except Exception as e:
        # 예외 발생 시 오류 메시지를 반환
        return jsonify(success=False, error=str(e))


@app.route('/shutdown', methods=['GET'])
def shutdown():
    """서버를 종료합니다."""
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        if platform.system() == "Windows":
            os.system(f'taskkill /PID {os.getpid()} /F')
        else:
            os.kill(os.getpid(), signal.SIGTERM)
    else:
        func()
    return '서버가 종료되었습니다.'


def open_browser():
    """서버가 실행된 후 브라우저를 자동으로 엽니다."""
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":
    # 웹 서버 실행 및 브라우저 열기
    threading.Timer(1, open_browser).start()  # 1초 후 브라우저 열기
    app.run(debug=False)
