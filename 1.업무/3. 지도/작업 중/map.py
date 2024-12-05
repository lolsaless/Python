from flask import Flask, jsonify, render_template_string, request
import pandas as pd
import folium

# 엑셀 파일 경로
EXCEL_PATH = "marker_data.xlsx"

# Flask 앱 초기화
app = Flask(__name__)

# 초기 데이터 로드
try:
    df = pd.read_excel(EXCEL_PATH)
except FileNotFoundError:
    # 엑셀 파일이 없을 경우 기본 데이터 생성
    data = {
        "Name": ["주차장 A", "요양원 B", "어린이집 C", "산후조리원 D", "주차장 E"],
        "Category": ["실내주차장", "요양원", "어린이집", "산후조리원", "실내주차장"],
        "Latitude": [37.5665, 37.5675, 37.5685, 37.5695, 37.5705],
        "Longitude": [126.9780, 126.9790, 126.9800, 126.9810, 126.9820],
        "Info": [
            "주차장 A 정보",
            "요양원 B 정보",
            "어린이집 C 정보",
            "산후조리원 D 정보",
            "주차장 E 정보",
        ],
        "Color": ["blue", "green", "red", "purple", "blue"],
    }
    df = pd.DataFrame(data)
    df.to_excel(EXCEL_PATH, index=False)


@app.route("/")
def map_view():
    """지도와 초기 상태를 렌더링."""
    # 지도 생성
    map_center = [37.5665, 126.9780]
    mymap = folium.Map(location=map_center, zoom_start=14)

    # 마커를 추가
    for _, row in df.iterrows():
        marker = folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=(
                f"<b>{row['Name']}</b><br>"
                f"Category: {row['Category']}<br>"
                f"Info: {row['Info']}<br>"
                f"<button onclick='markAsComplete({row.name})'>완료</button>"
            ),
            icon=folium.Icon(color=row["Color"]),
        )
        marker.add_to(mymap)

    # 지도 HTML
    map_html = mymap.get_root().render()

    # JavaScript 추가
    map_html += """
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        function markAsComplete(index) {
            $.post("/update", { id: index }, function(response) {
                if (response.success) {
                    alert("마커 상태가 업데이트되었습니다.");
                    location.reload(); // 새로고침
                } else {
                    alert("업데이트 실패: " + response.error);
                }
            });
        }
    </script>
    """
    return render_template_string(map_html)


@app.route("/update", methods=["POST"])
def update_marker():
    """마커 색상을 검은색으로 업데이트."""
    try:
        marker_id = int(request.form["id"])
        df.loc[marker_id, "Color"] = "black"  # 색상 변경
        df.to_excel(EXCEL_PATH, index=False)  # 엑셀 파일에 저장
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))


if __name__ == "__main__":
    app.run(debug=True)