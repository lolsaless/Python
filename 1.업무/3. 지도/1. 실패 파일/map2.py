from flask import Flask, jsonify, render_template_string, request
import pandas as pd
import folium

# 엑셀 파일 경로
EXCEL_PATH = "map_data.xlsx"

# Flask 앱 초기화
app = Flask(__name__)

# 엑셀 파일 읽기
df = pd.read_excel(EXCEL_PATH)

# 시설군별 색상 매핑
facility_colors = {
    "지하역사": "gray",
    "노인요양시설": "blue",
    "어린이집": "yellow",
}

def get_facility_color(facility_group):
    """시설군에 따른 색상 반환."""
    return facility_colors.get(facility_group, "green")  # 기본 색상은 녹색


@app.route("/")
def map_view():
    """지도와 초기 상태를 렌더링."""
    # 지도 생성
    map_center = [df["Latitude"].mean(), df["Longitude"].mean()]
    mymap = folium.Map(location=map_center, zoom_start=12)

    # 마커를 추가
    for _, row in df.iterrows():
        color = get_facility_color(row["시설군"])
        marker = folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=(f"""
                <div style='width:300px; height:auto;'>
                    <b>시설명:</b> {row['시설명']}<br>
                    <b>시설군:</b> {row['시설군']}<br>
                    <b>주소:</b> {row['주소']}<br>
                    <button onclick='markAsComplete({row.name})'>완료</button>
                </div>
            """),
            icon=folium.Icon(color=color),
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
        df.loc[marker_id, "시설군"] = "완료"  # 상태를 "완료"로 표시
        df.to_excel(EXCEL_PATH, index=False)  # 엑셀 파일에 저장
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))


if __name__ == "__main__":
    app.run(debug=True)
