import os
import subprocess
from pdf2image import convert_from_path
from PIL import Image

# 패키지 설치
subprocess.run(['apt-get', 'install', '-y', 'poppler-utils'])

# 라이브러리 설치
subprocess.run(['pip', 'install', 'pdf2image', 'Pillow'])

# 'os'와 'pdf2image' 라이브러리 임포트
import os
from pdf2image import convert_from_path

# PDF 파일이 저장된 디렉토리 경로
pdf_directory = 'pdf_files'

# 디렉토리 내 모든 파일을 리스트로 받아오는 함수
def get_pdf_files(directory):
    files = []
    for file in os.listdir(directory):
        if file.endswith('.pdf'):
            files.append(file)
    return files

# PDF 파일을 이미지로 변환하는 함수
def convert_pdf_to_images(file_path):
    images = convert_from_path(file_path)
    return images

# PDF 파일이 이미지로 변환되었는지 확인하고 저장하는 함수
def save_images(images, file_path):
    directory = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    file_name_without_extension = os.path.splitext(file_name)[0]

    for i, image in enumerate(images):
        image.save(f'{directory}/{file_name_without_extension}_page{i+1}.jpg', 'JPEG')

# PDF 파일 목록을 가져옴
pdf_files = get_pdf_files(pdf_directory)

# PDF 파일을 이미지로 변환하고 저장
converted_count = 0
for file in pdf_files:
    file_path = os.path.join(pdf_directory, file)
    images = convert_pdf_to_images(file_path)
    save_images(images, file_path)
    converted_count += 1

# 모든 PDF 파일이 이미지 파일로 변환되었는지 출력
if converted_count == len(pdf_files):
    print('모든 PDF 파일이 이미지 파일로 변환되었습니다.')
else:
    print('일부 PDF 파일이 이미지 파일로 변환되지 않았습니다.')
