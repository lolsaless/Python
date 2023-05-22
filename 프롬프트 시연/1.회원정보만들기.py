import os
import random

# 세 글자 한글 이름 100개를 무작위로 생성하는 함수
def generate_names():
    names = []
    for _ in range(100):
        name = ""
        for _ in range(3):
            syllables = random.choice(['가','나','다','라','마','바','사','아','자','차','카','타','파','하'])
            name += syllables
        names.append(name)
    return names

# 디렉토리를 확인하고 '회원정보'라는 이름의 폴더를 생성하는 함수
def create_directory():
    if not os.path.exists('회원정보'):
        os.makedirs('회원정보')

# 각 이름별로 '회원정보' 폴더에 txt 파일을 생성하는 함수
def create_txt_files(names):
    for name in names:
        index = 1
        while True:
            file_name = f'회원정보/{name}_{index}.txt'
            if not os.path.exists(file_name):
                with open(file_name, 'w') as file:
                    file.write(f'이름: {name}\n')
                    file.write(f'나이: {generate_age()}\n')
                    file.write(f'성별: {generate_gender()}\n')
                    file.write(f'이메일: {generate_email(name)}\n')
                break
            else:
                index += 1

# 임의의 나이를 생성하는 함수
def generate_age():
    return random.randint(18, 70)

# 임의의 성별을 생성하는 함수
def generate_gender():
    return random.choice(['남', '여'])

# 임의의 이메일 주소를 생성하는 함수
def generate_email(name):
    domain = random.choice(['gmail.com', 'naver.com', 'yahoo.com', 'daum.net', 'kakao.com'])
    return f'{name}@{domain}'

# 생성한 함수들을 사용하여 이름 100개에 대해 모든 txt 파일을 생성하는 함수
def generate_member_info():
    names = generate_names()
    create_directory()
    create_txt_files(names)

# 파일 생성 프로세스가 완료되면 메시지를 출력하는 코드
generate_member_info()
print('100개의 회원 정보를 담은 텍스트 파일 생성이 완료되었습니다.')
