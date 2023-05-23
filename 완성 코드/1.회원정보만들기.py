import os
import random

def generate_random_name():
    first_names = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임']
    middle_names = ['철', '영', '미', '수', '진', '현', '석', '미', '종', '민']
    last_names = ['동', '수', '호', '희', '훈', '은', '흥', '우', '기', '선']
    name = random.choice(first_names) + random.choice(middle_names) + random.choice(last_names)
    return name

def create_directory():
    directory = '회원정보'
    if not os.path.exists(directory):
        os.makedirs(directory)

def generate_age():
    return random.randint(18, 70)

def generate_gender():
    genders = ['남', '여']
    return random.choice(genders)

def generate_email(name):
    domains = ['google', 'naver', 'yahoo', 'daum', 'kakao']
    domain = random.choice(domains)
    email = name + '@' + domain + '.com'
    return email

def write_member_info(name, age, gender, email):
    filename = '회원정보/' + name + '.txt'
    count = 1
    while os.path.exists(filename):
        count += 1
        filename = '회원정보/' + name + '_' + str(count) + '.txt'
    with open(filename, 'w') as file:
        file.write('이름: ' + name + '\n')
        file.write('나이: ' + str(age) + '\n')
        file.write('성별: ' + gender + '\n')
        file.write('이메일: ' + email + '\n')

def generate_member_files():
    create_directory()
    for _ in range(100):
        name = generate_random_name()
        age = generate_age()
        gender = generate_gender()
        email = generate_email(name)
        write_member_info(name, age, gender, email)
    print('100개의 회원 정보를 담은 텍스트 파일 생성이 완료되었습니다.')

generate_member_files()
