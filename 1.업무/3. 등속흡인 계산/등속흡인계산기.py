import tkinter as tk
from tkinter import ttk

def calculate():
    try:
        # 필요한 입력값 가져오기
        m_a = float(entry_ma.get())
        theta_m = float(entry_theta_m.get())
        p_a = float(entry_pa.get())
        p_s = float(entry_ps.get())
        
        # 예제 계산 (수분량 % 계산)
        V_m = 22.4
        molecular_weight_ratio = 22.4 / 18
        X_w = (molecular_weight_ratio * m_a) / (V_m * (273 / (273 + theta_m)) * ((p_a + p_s) / 760) * molecular_weight_ratio * m_a) * 100

        # 결과 표시
        result_label.config(text=f"Moisture Content (X_w): {X_w:.2f}%")
    except ValueError:
        result_label.config(text="Invalid input, please enter numbers.")

# GUI 생성
root = tk.Tk()
root.title("Emission Gas Calculator")

# 입력 필드 생성
tk.Label(root, text="m_a (g):").grid(row=0, column=0, padx=10, pady=5)
entry_ma = tk.Entry(root)
entry_ma.grid(row=0, column=1)

tk.Label(root, text="theta_m (°C):").grid(row=1, column=0, padx=10, pady=5)
entry_theta_m = tk.Entry(root)
entry_theta_m.grid(row=1, column=1)

tk.Label(root, text="p_a (mmHg):").grid(row=2, column=0, padx=10, pady=5)
entry_pa = tk.Entry(root)
entry_pa.grid(row=2, column=1)

tk.Label(root, text="p_s (mmHg):").grid(row=3, column=0, padx=10, pady=5)
entry_ps = tk.Entry(root)
entry_ps.grid(row=3, column=1)

# 계산 버튼
calculate_button = tk.Button(root, text="Calculate", command=calculate)
calculate_button.grid(row=4, column=0, columnspan=2, pady=10)

# 결과 표시
result_label = tk.Label(root, text="Enter values and press Calculate")
result_label.grid(row=5, column=0, columnspan=2, pady=10)

# GUI 실행
root.mainloop()
