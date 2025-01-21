import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox
)
import math


# 계산 함수 정의
def calculate_X_w(m_a, theta_m, p_a, p_s):
    """수분량(%) 계산"""
    try:
        V_m = 22.4
        molecular_weight_ratio = 22.4 / 18
        numerator = molecular_weight_ratio * m_a
        denominator = (
            V_m *
            (273 / (273 + theta_m)) *
            ((p_a + p_s) / 760) *
            molecular_weight_ratio *
            m_a
        )
        X_w = (numerator / denominator) * 100
        return X_w
    except Exception as e:
        return str(e)


class GasCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Emission Gas Calculator")
        self.setGeometry(100, 100, 400, 300)

        # Main widget
        self.widget = QWidget()
        self.setCentralWidget(self.widget)

        # Layout
        layout = QVBoxLayout()

        # Labels and input fields
        self.label_m_a = QLabel("m_a (g):")
        self.input_m_a = QLineEdit()
        layout.addWidget(self.label_m_a)
        layout.addWidget(self.input_m_a)

        self.label_theta_m = QLabel("theta_m (°C):")
        self.input_theta_m = QLineEdit()
        layout.addWidget(self.label_theta_m)
        layout.addWidget(self.input_theta_m)

        self.label_p_a = QLabel("p_a (mmHg):")
        self.input_p_a = QLineEdit()
        layout.addWidget(self.label_p_a)
        layout.addWidget(self.input_p_a)

        self.label_p_s = QLabel("p_s (mmHg):")
        self.input_p_s = QLineEdit()
        layout.addWidget(self.label_p_s)
        layout.addWidget(self.input_p_s)

        # Calculate button
        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.perform_calculation)
        layout.addWidget(self.calculate_button)

        # Result display
        self.result_label = QLabel("Result: ")
        layout.addWidget(self.result_label)

        # Set layout
        self.widget.setLayout(layout)

    def perform_calculation(self):
        try:
            # Get user inputs
            m_a = float(self.input_m_a.text())
            theta_m = float(self.input_theta_m.text())
            p_a = float(self.input_p_a.text())
            p_s = float(self.input_p_s.text())

            # Perform calculation
            result = calculate_X_w(m_a, theta_m, p_a, p_s)

            # Display result
            self.result_label.setText(f"Result: X_w = {result:.2f}%")
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numbers.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


# Main application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GasCalculator()
    window.show()
    sys.exit(app.exec_())
