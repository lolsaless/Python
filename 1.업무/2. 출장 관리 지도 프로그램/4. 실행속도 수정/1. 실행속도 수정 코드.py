from flask import Flask, jsonify, render_template_string, request
import pandas as pd
import folium
import webbrowser
import threading
import os
import signal
import platform
from tkinter.filedialog import askopenfilename

# Flask 앱 초기화
app = Flask(__name__)

# 엑셀 파일 로드

def load_excel():
    """엑셀 파일 선택"""
    file_path = askopenfilename(
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
    print(str(e))
    exit()

# "완료" 열 추가 (없으면)
df["완료"] = df.get("완료", "")  # 열이 없으면 기본값으로 빈 문자열 설정

# 시설군별 색상 매핑
FACILITY_COLORS = {
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
    "산후조리원": "lightblue",
    "박물관": "beige",
    "목욕장업의 영업시설": "teal",
    "도서관": "gold",
    "대규모 점포": "silver",
    "노인요양시설": "lavender",
}

def get_facility_color(row):
    """시설군에 따른 색상 반환."""
    return "black" if row["완료"] == "완료" else FACILITY_COLORS.get(row["시설군"], "green")

def calculate_progress():
    """시군별 완료 진행 상황 계산."""
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
    map_center = [df["Latitude"].mean(), df["Longitude"].mean()]
    mymap = folium.Map(location=map_center, zoom_start=12)

    for _, row in df.iterrows():
        color = get_facility_color(row)
        marker = folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=(
                """
                <div style='width:300px; height:auto;'>
                    <b>시설명:</b> {시설명}<br>
                    <b>시설군:</b> {시설군}<br>
                    <b>주소:</b> {주소}<br>
                    <button onclick="markAsComplete({index})">완료</button>
                    <button onclick="cancelCompletion({index})">취소</button>
                </div>
                """.format(시설명=row['시설명'], 시설군=row['시설군'], 주소=row['주소'], index=row.name)
            ),
            icon=folium.Icon(color=color),
        )
        marker.add_to(mymap)

    map_html = mymap.get_root().render()
    progress_info = calculate_progress()
    total_progress = calculate_total_progress()
    progress_html = """
    <div style='position: fixed; top: 10px; right: 10px; background: rgba(255, 255, 255, 0.9); padding: 10px; border: 1px solid black; z-index: 1000;'>
        <h4>{total_progress}</h4>
        <h4>각 시군별 진행 상황</h4>
        {progress_rows}
        <button onclick="shutdownServer()" style='margin-top: 10px; padding: 5px 10px;'>종료</button>
    </div>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        function markAsComplete(index) {
            $.post("/update", { id: index, action: 'complete' }, function(response) {
                if (response.success) {
                    alert("마커 상태가 업데이트되었습니다.");
                    location.reload();
                } else {
                    alert("업데이트 실패: " + response.error);
                }
            });
        }
        function cancelCompletion(index) {
            $.post("/update", { id: index, action: 'cancel' }, function(response) {
                if (response.success) {
                    alert("마커 상태가 취소되었습니다.");
                    location.reload();
                } else {
                    alert("취소 실패: " + response.error);
                }
            });
        }
        function shutdownServer() {
            if (confirm('프로그램을 종료하시겠습니까?')) {
                $.get('/shutdown', function(response) {
                    alert(response);
                    window.open('', '_self', '');
                    window.close();
                });
            }
        }
    </script>
    """.format(
        total_progress=total_progress,
        progress_rows=''.join(f'<p><b>{region}:</b> {status}</p>' for region, status in progress_info.items())
    )
    return render_template_string(map_html + progress_html)

@app.route("/update", methods=["POST"])
def update_marker():
    try:
        marker_id = int(request.form["id"])
        action = request.form["action"]
        df.at[marker_id, "완료"] = "완료" if action == 'complete' else ""
        df.to_excel(EXCEL_PATH, index=False)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

@app.route('/shutdown', methods=['GET'])
def shutdown():
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
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":
    threading.Timer(1, open_browser).start()
    app.run(debug=False)
