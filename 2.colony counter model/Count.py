import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from tkinter import Tk, filedialog

# Tkinter 초기화 및 숨기기 (파일 선택 대화 상자를 위해 사용)
Tk().withdraw()

# 모델 파일 경로 설정 (현재 스크립트가 있는 디렉토리 기준)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, '/Users/lol/Documents/GitHub/model/colony_detector_model.h5')

# 학습된 모델 로드
model = load_model(model_path)
print("Model loaded successfully.")

# 이미지 선택 함수 (사용자가 이미지를 선택할 수 있도록 파일 대화 상자 열기)
def select_image():
    file_path = filedialog.askopenfilename()
    if not file_path:
        raise ValueError("No image file selected.")
    return file_path

# 이미지 전처리 및 분할 함수
def preprocess_and_split_image(image_path, tile_size=(256, 256)):
    """
    이미지를 타일로 분할하고 전처리하여 모델 입력에 맞게 준비합니다.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Image at path '{image_path}' could not be loaded. Please check the file path.")
    
    h, w, _ = image.shape
    tiles = []
    
    for y in range(0, h, tile_size[1]):
        for x in range(0, w, tile_size[0]):
            tile = image[y:y+tile_size[1], x:x+tile_size[0]]
            if tile.shape[0] != tile_size[1] or tile.shape[1] != tile_size[0]:
                # 패딩을 추가하여 타일 크기를 고정
                tile = cv2.copyMakeBorder(tile, 0, tile_size[1] - tile.shape[0], 0, tile_size[0] - tile.shape[1], cv2.BORDER_CONSTANT, value=(0, 0, 0))
            tile_scaled = tile / 255.0  # 0-1 스케일링
            tiles.append(tile_scaled)
    
    tiles = np.array(tiles)
    grid_shape = (len(range(0, h, tile_size[1])), len(range(0, w, tile_size[0])))
    return tiles, grid_shape, h, w

# 예측 수행 함수
def predict_colony(image_path, model):
    """
    전처리된 타일 이미지에 대해 모델을 사용하여 예측을 수행합니다.
    """
    tiles, grid_shape, h, w = preprocess_and_split_image(image_path)
    predictions = model.predict(tiles)
    return predictions, grid_shape, h, w

# 붉은색 동그라미 콜로니를 카운트하는 함수
def count_red_circles(image, circle):
    """
    이미지에서 주어진 원 안의 붉은색 동그라미 (콜로니) 개수를 카운트합니다.
    """
    original_image = image.copy()  # 원본 이미지 복사

    # 원 영역을 마스크로 적용
    mask = np.zeros_like(image[:, :, 0])
    cv2.circle(mask, (circle[0], circle[1]), circle[2], 255, -1)
    masked_image = cv2.bitwise_and(image, image, mask=mask)
    
    # 이미지를 HSV 색 공간으로 변환
    hsv = cv2.cvtColor(masked_image, cv2.COLOR_BGR2HSV)

    # 붉은색 범위 정의 (두 범위를 사용하여 더 넓은 범위의 붉은색을 검출)
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 50, 50])
    upper_red2 = np.array([180, 255, 255])

    # 붉은색에 해당하는 마스크 생성
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 | mask2

    # 마스크에 블러 적용하여 노이즈 제거
    blurred = cv2.GaussianBlur(mask, (5, 5), 2)

    # 동그라미 검출
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.4, minDist=10,
                               param1=60, param2=22, minRadius=2, maxRadius=50)

    # 동그라미 카운트 및 이미지에 표시
    circle_count = 0
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            if 4 < r < 20:  # 필터링 조건 (동그라미의 반지름이 특정 범위 내에 있을 때만 카운트)
                cv2.circle(original_image, (x, y), r, (0, 255, 0), 2)  # 동그라미를 원본 이미지에 그리기
                circle_count += 1

    # 이미지에 콜로니 카운트 추가
    text = f"Number of colony circles: {circle_count}"
    font = cv2.FONT_HERSHEY_SIMPLEX  # 폰트 설정
    scale = 5  # 글씨 크기 조정
    color = (255, 0, 0)  # 글씨 색상 (BGR 형식)
    thickness = 3  # 글씨 두께 조정
    position = (10, 120)  # 글씨 위치 조정

    cv2.putText(original_image, text, position, font, scale, color, thickness)  # 이미지에 텍스트 추가

    return circle_count, original_image

# 마우스 이벤트를 처리하는 함수
def draw_circle(event, x, y, flags, param):
    """
    마우스 이벤트를 처리하여 사용자가 이미지 위에 원을 그릴 수 있도록 합니다.
    """
    global ix, iy, drawing, image

    if event == cv2.EVENT_LBUTTONDOWN:
        # 마우스 왼쪽 버튼을 눌렀을 때 시작 좌표 기록
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            # 마우스 이동 중일 때 현재 이미지 복사본에 원 그리기
            image = temp_image.copy()
            cv2.circle(image, (ix, iy), int(((x - ix)**2 + (y - iy)**2)**0.5), (0, 255, 0), 2)

    elif event == cv2.EVENT_LBUTTONUP:
        # 마우스 왼쪽 버튼을 뗐을 때 원 그리기 완료
        drawing = False
        radius = int(((x - ix)**2 + (y - iy)**2)**0.5)
        cv2.circle(image, (ix, iy), radius, (0, 255, 0), 2)
        circle_count, output_image = count_red_circles(image, (ix, iy, radius))
        print(f"Number of red circles detected: {circle_count}")

        # 결과 이미지 저장
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if save_path:
            cv2.imwrite(save_path, output_image)
            print(f"Result saved to {save_path}")
        
        # 창 닫기
        cv2.destroyAllWindows()
        for i in range(1, 5):
            cv2.waitKey(1)

def main():
    global temp_image, image

    # 이미지 선택
    image_path = select_image()
    
    # 모델을 사용하여 예측 수행
    predictions, grid_shape, h, w = predict_colony(image_path, model)
    predictions_2d = predictions.reshape(grid_shape)
    overall_prediction = np.mean(predictions_2d)

    print(f"Overall Prediction: {overall_prediction}")

    if overall_prediction > 0.6:
        # 이미지 로드 및 복사본 생성
        image = cv2.imread(image_path)
        temp_image = image.copy()
        drawing = False
        ix, iy = -1, -1

        # 마우스 콜백 설정
        cv2.namedWindow('image')
        cv2.setMouseCallback('image', draw_circle)

        # 이미지 창 표시
        while True:
            cv2.imshow('image', image)
            if cv2.waitKey(20) & 0xFF == 27:  # Esc 키를 누르면 종료
                break

        # 창 닫기
        cv2.destroyAllWindows()
        for i in range(1, 5):
            cv2.waitKey(1)
    else:
        print("No colonies detected in the image.")

if __name__ == "__main__":
    main()
