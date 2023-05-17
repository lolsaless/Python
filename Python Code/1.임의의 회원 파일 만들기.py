import os
import random


# 세 글자 한글 이름 100개를 무작위로 생성하는 함수
def generate_names():
    surnames = ['김', '이', '박', '조', '한']
    given_names = ['영', '찬', '진', '오', '하', '영']
    names = []
    for _ in range(100):
        full_name = random.choice(surnames) + random.choice(given_names) + random.choice(given_names)
        names.append(full_name)
    return names


# 디렉토리를 확인하고 '회원정보'라는 이름의 폴더를 생성하는 함수
def create_directory():
    directory_name = '회원정보'
    if not os.path.exists(directory_name):
        os.mkdir(directory_name)


# 각 이름별로 '회원정보' 폴더에 세 개의 txt 파일을 생성하는 함수
def create_files(names):
    for name in names:
        for i in range(1, 4):
            file_name = f'{name}_{i}.txt'
            if not os.path.exists(file_name):
                with open(f'회원정보/{file_name}', 'w') as file:
                    file.write(f'이름: {name}\n')
                    file.write(f'나이: {generate_age()}\n')
                    file.write(f'성별: {generate_gender()}\n')
                    file.write(f'이메일: {generate_email(name)}\n')


# 임의의 나이를 생성하는 함수
def generate_age():
    return random.randint(18, 70)


# 임의의 성별을 생성하는 함수
def generate_gender():
    genders = ['남', '여']
    return random.choice(genders)


# 임의의 이메일 주소를 생성하는 함수
def generate_email(name):
    domains = ['google.com', 'naver.com', 'yahoo.com', 'daum.net', 'kakao.com']
    return f'{name}@{random.choice(domains)}'


# 생성한 함수들을 사용하여 이름 100개에 대해 모든 txt 파일을 생성
def generate_member_info_files():
    names = generate_names()
    create_directory()
    create_files(names)
    print('100개의 회원 정보를 담은 텍스트 파일 생성이 완료되었습니다.')


# 프로그램 실행
generate_member_info_files()
