import os
import pandas as pd


# '회원정보' 폴더에 있는 모든 txt 파일을 읽고 정보를 추출하여 데이터프레임으로 반환하는 함수
def read_txt_files():
    folder_path = '회원정보'
    file_list = [file for file in os.listdir(folder_path) if file.endswith('.txt')]

    data_male = []
    data_female = []
    for file_name in file_list:
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'r') as file:
            lines = file.readlines()
            name = lines[0].split(': ')[1].strip()
            age = lines[1].split(': ')[1].strip()
            gender = lines[2].split(': ')[1].strip()
            email = lines[3].split(': ')[1].strip()
            if gender == '남':
                data_male.append([name, age, gender, email])
            elif gender == '여':
                data_female.append([name, age, gender, email])

    df_male = pd.DataFrame(data_male, columns=['이름', '나이', '성별', '이메일 주소'])
    df_female = pd.DataFrame(data_female, columns=['이름', '나이', '성별', '이메일 주소'])
    return df_male, df_female


# 데이터프레임을 엑셀 파일의 각각의 탭으로 저장하는 함수
def save_to_excel(df_male, df_female):
    file_name = '회원정보_결합(남녀).xlsx'
    with pd.ExcelWriter(file_name) as writer:
        df_male.to_excel(writer, sheet_name='남자', index=False)
        df_female.to_excel(writer, sheet_name='여자', index=False)


# '회원정보' 폴더의 txt 파일을 읽어 데이터프레임으로 만들고 각 탭으로 저장
def combine_txt_files_to_excel():
    df_male, df_female = read_txt_files()
    save_to_excel(df_male, df_female)
    print('모든 txt 파일을 엑셀 파일로 결합 완료!')


# 프로그램 실행
combine_txt_files_to_excel()
