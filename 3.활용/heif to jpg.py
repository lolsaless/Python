import os
from PIL import Image
import pyheif

# HEIC 파일이 있는 디렉토리 경로
directory = '/Users/lol/Downloads/Photos-001'

# 디렉토리 내의 모든 파일을 순회
for filename in os.listdir(directory):
    if filename.lower().endswith('.heic'):
        heic_path = os.path.join(directory, filename)
        jpg_path = os.path.splitext(heic_path)[0] + '.jpg'

        # HEIC 파일을 읽고 변환
        heif_file = pyheif.read(heic_path)
        image = Image.frombytes(
            heif_file.mode, 
            heif_file.size, 
            heif_file.data,
            "raw",
            heif_file.mode,
            heif_file.stride,
        )

        # JPG 파일로 저장
        image.save(jpg_path, "JPEG")
        print(f'변환 완료: {jpg_path}')