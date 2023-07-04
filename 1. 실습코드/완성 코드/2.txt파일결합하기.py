import os
import pandas as pd

# '회원정보' 폴더 경로
folder_path = '회원정보'

# 파일명에서 정보 추출하는 함수
def extract_info_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    info = {}
    for line in lines:
        line = line.strip()
        if line:
            key, value = line.split(':', 1)
            info[key.strip()] = value.strip()

    return info

# 모든 txt 파일에서 정보 추출
data = []
for file_name in os.listdir(folder_path):
    if file_name.endswith('.txt'):
        file_path = os.path.join(folder_path, file_name)
        info = extract_info_from_file(file_path)
        data.append(info)

# 추출한 정보로 데이터프레임 생성
df = pd.DataFrame(data, columns=['이름', '나이', '성별', '이메일'])

# 엑셀 파일로 저장
output_file = '회원정보_결합.xlsx'
df.to_excel(output_file, index=False)

# 완료 메시지 출력
print('모든 txt 파일을 엑셀 파일로 결합 완료!')
