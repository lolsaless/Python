import pandas as pd
import glob

# '회원정보' 폴더에 있는 모든 txt 파일을 가져옵니다.
file_list = glob.glob('회원정보/*.txt')

# 추출한 정보를 저장할 리스트를 생성합니다.
data = []

# 각 파일에서 정보를 읽어와 리스트에 추가합니다.
for file in file_list:
    with open(file, 'r') as f:
        lines = f.readlines()
        name = lines[0].split(':')[1].strip()
        age = lines[1].split(':')[1].strip()
        gender = lines[2].split(':')[1].strip()
        email = lines[3].split(':')[1].strip()
        data.append([name, age, gender, email])

# 데이터프레임 생성
df = pd.DataFrame(data, columns=['이름', '나이', '성별', '이메일'])

# 데이터프레임을 엑셀 파일로 저장
df.to_excel('회원정보_결합.xlsx', index=False)

# 완료 메시지 출력
print('모든 txt 파일을 엑셀 파일로 결합 완료!')
