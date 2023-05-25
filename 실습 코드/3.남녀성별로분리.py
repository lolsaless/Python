import pandas as pd
import glob

# '회원정보' 폴더에 있는 모든 txt 파일을 가져옵니다.
file_list = glob.glob('회원정보/*.txt')

# 추출한 정보를 저장할 리스트를 생성합니다.
male_data = []  # 남자 정보를 저장할 리스트
female_data = []  # 여자 정보를 저장할 리스트

# 각 파일에서 정보를 읽어와 리스트에 추가합니다.
for file in file_list:
    with open(file, 'r') as f:
        lines = f.readlines()
        name = lines[0].split(':')[1].strip()
        age = lines[1].split(':')[1].strip()
        gender = lines[2].split(':')[1].strip()
        email = lines[3].split(':')[1].strip()

        # 성별에 따라서 데이터를 분리해서 각각의 리스트에 추가합니다.
        if gender == '남':
            male_data.append([name, age, gender, email])
        elif gender == '여':
            female_data.append([name, age, gender, email])

# 각 데이터프레임 생성
male_df = pd.DataFrame(male_data, columns=['이름', '나이', '성별', '이메일'])
female_df = pd.DataFrame(female_data, columns=['이름', '나이', '성별', '이메일'])

# 데이터프레임을 엑셀 파일로 저장 (각각의 탭으로 저장)
with pd.ExcelWriter('회원정보_결합(남여).xlsx') as writer:
    male_df.to_excel(writer, sheet_name='남자', index=False)
    female_df.to_excel(writer, sheet_name='여자', index=False)

# 완료 메시지 출력
print('모든 txt 파일을 엑셀 파일로 결합 완료!')
