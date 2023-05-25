import os
import random
import string
from itertools import count

# 1. 세 글자 한글 이름 100개를 무작위로 생성하는 함수
def generate_names(n):
    first_names = ["김", "박", "이", "최", "황", "오", "강", "조", "윤", "장", "정"]
    middle_names = ["철", "영", "정", "민", "준", "지", "선", "승", "경", "유", "재"]
    last_names = ["수", "희", "동", "호", "민", "윤", "진", "훈", "현", "원", "식"]

    names = [random.choice(first_names) + random.choice(middle_names) + random.choice(last_names) for _ in range(n)]
    return names

# 2. '회원정보'라는 이름의 폴더를 생성하는 함수
def create_directory():
    dir_name = "회원정보"
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

# 3. 각 이름별로 '회원정보' 폴더에 txt 파일을 생성하는 함수
def create_file(name):
    for i in count(1):
        file_name = f"회원정보/{name}_{i}.txt"
        if not os.path.exists(file_name):
            return open(file_name, "w")

# 4. 임의의 나이를 생성하는 함수
def generate_age():
    return random.randint(18, 70)

# 5. 임의의 성별을 생성하는 함수
def generate_gender():
    return random.choice(["남", "여"])

# 6. 임의의 이메일 주소를 생성하는 함수
def generate_email(name):
    domains = ["gmail.com", "naver.com", "yahoo.com", "daum.net", "kakao.com"]
    return name + "@" + random.choice(domains)

# 7. 각 txt 파일에 이름, 생성된 나이, 생성된 성별, 생성된 이메일 주소 정보를 쓰는 함수
def write_member_info(name, file):
    age = generate_age()
    gender = generate_gender()
    email = generate_email(name)
    file.write(f"이름: {name}\n나이: {age}\n성별: {gender}\n이메일: {email}\n")

# 8. 생성한 함수들을 사용하여 이름 100개에 대해 모든 txt 파일을 생성합니다.
def generate_member_info():
    names = generate_names(100)
    create_directory()
    for name in names:
        file = create_file(name)
        write_member_info(name, file)
        file.close()

# 9. 파일 생성 프로세스가 완료되면 메시지를 출력하는 코드
generate_member_info()
print("100개의 회원 정보를 담은 텍스트 파일 생성이 완료되었습니다.")
