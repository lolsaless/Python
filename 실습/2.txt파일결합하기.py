import os
import pandas as pd

folder_name = '회원정보'
output_file = '회원정보_결합.xlsx'

# 1. '회원정보' 폴더 확인
if not os.path.exists(folder_name):
    print("회원정보 폴더를 찾을 수 없습니다.")
    exit()

data = []
error_files = []

# 2. 폴더 내의 모든 txt 파일 읽기
for file_name in os.listdir(folder_name):
    if file_name.endswith('.txt'):
        file_path = os.path.join(folder_name, file_name)
        try:
            with open(file_path, 'r') as file:
                # 개인 정보 추출
                name, age, gender, email = '', '', '', ''
                for line in file:
                    line = line.strip()
                    if line.startswith('이름:'):
                        name = line.split(':')[1].strip()
                    elif line.startswith('나이:'):
                        age = line.split(':')[1].strip()
                    elif line.startswith('성별:'):
                        gender = line.split(':')[1].strip()
                    elif line.startswith('이메일:'):
                        email = line.split(':')[1].strip()
                # 추출한 정보 데이터에 추가
                data.append([name, age, gender, email])
        except Exception as e:
            error_files.append((file_name, str(e)))

# 3. 데이터프레임 생성
df = pd.DataFrame(data, columns=['이름', '나이', '성별', '이메일 주소'])

# 4. 데이터프레임을 엑셀 파일로 저장
try:
    df.to_excel(output_file, index=False)
    print("모든 txt 파일을 엑셀 파일로 결합 완료!")
except Exception as e:
    print("엑셀 파일을 저장하는 데 문제가 발생했습니다.")
    print(str(e))

# 5. 오류가 발생한 파일 목록 출력
if error_files:
    print("파일에서 정보를 추출하는 데 문제가 발생했습니다:")
    for file_name, error_message in error_files:
        print(f"{file_name}: {error_message}")
