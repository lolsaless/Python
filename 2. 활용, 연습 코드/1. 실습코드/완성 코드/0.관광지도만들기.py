import os
import sys
import pandas as pd
import folium
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QLineEdit, QDesktopWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from folium.plugins import MarkerCluster
from folium import Tooltip

# Ensure the PyQtWebEngineWidgets module is imported before a QCoreApplication instance is created
from PyQt5 import QtWebEngineWidgets

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tourism Information")

        self.file_path = None
        self.tourism_data = None

        self.map = folium.Map(location=[0, 0], zoom_start=2)
        self.marker_cluster = MarkerCluster().add_to(self.map)

        self.info_label = QLabel(self)
        self.info_label.setGeometry(10, 10, 300, 30)

        self.search_input = QLineEdit(self)
        self.search_input.setGeometry(10, 50, 150, 30)
        self.search_input.textChanged.connect(self.search_tourism)

        self.search_result_label = QLabel(self)
        self.search_result_label.setGeometry(170, 50, 200, 30)

        self.select_button = QPushButton("Select Excel File", self)
        self.select_button.setGeometry(10, 90, 150, 30)
        self.select_button.clicked.connect(self.select_file)

        self.map_view = QWebEngineView(self)

        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, screen.width(), screen.height())
        self.map_view.setGeometry(10, 130, screen.width() - 20, screen.height() - 140)

    def select_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Select Excel File")
        file_dialog.setNameFilter("Excel Files (*.xlsx *.xls)")
        if file_dialog.exec_():
            self.load_data(file_dialog.selectedFiles()[0])

    def load_data(self, file_path):
        self.file_path = file_path
        self.tourism_data = pd.read_excel(file_path, sheet_name="Sheet1")

        self.show_markers()
        self.update_info_label()

    def show_markers(self):
        self.marker_cluster = MarkerCluster().add_to(self.map)

        for _, row in self.tourism_data.iterrows():
            name = row["관광지"]
            lat = row["위도"]
            lon = row["경도"]

            tooltip = Tooltip(name)
            marker = folium.Marker([lat, lon], popup=name, tooltip=tooltip)
            marker.add_to(self.marker_cluster)

        self.map.fit_bounds(self.marker_cluster.get_bounds())
        self.map.save("map.html")
        self.map_view.setUrl(QUrl.fromLocalFile(f"{os.getcwd()}/map.html"))

    def update_info_label(self):
        if self.file_path:
            self.info_label.setText(f"Selected File: {self.file_path}")
        else:
            self.info_label.setText("No file selected.")

    def search_tourism(self, text):
        if self.tourism_data is None:
            self.search_result_label.setText("No data loaded.")
            return

        if text:
            matching_rows = self.tourism_data[self.tourism_data["관광지"].str.contains(text)]
            self.show_search_results(matching_rows)
        else:
            self.search_result_label.clear()

    def show_search_results(self, rows):
        if len(rows) == 0:
            self.search_result_label.setText("No matching results.")
            return

        result = "Matching Results: " + ", ".join(rows["관광지"])
        self.search_result_label.setText(result)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
