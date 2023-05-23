import os
import random
import string

# 1. 세 글자 한글 이름 100개를 무작위로 생성하는 함수
def generate_names(n):
    first_names = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임"]
    middle_names = ["재", "영", "찬", "현", "유", "석", "민", "경", "지", "수"]
    last_names = ["호", "희", "수", "동", "선", "연", "우", "윤", "진", "현"]

    names = [random.choice(first_names) + random.choice(middle_names) + random.choice(last_names) for _ in range(n)]
    return names

# 2. '회원정보'라는 이름의 폴더를 생성하는 함수
def make_directory():
    if not os.path.exists('회원정보'):
        os.mkdir('회원정보')

# 3. 각 이름별로 '회원정보' 폴더에 txt 파일을 생성하는 함수
def create_txt_files(names):
    for i, name in enumerate(names, 1):
        with open(f'회원정보/{name}_{i}.txt', 'w') as f:
            pass

# 4. 임의의 나이를 생성하는 함수
def generate_age():
    return random.randint(18, 70)

# 5. 임의의 성별을 생성하는 함수
def generate_gender():
    return random.choice(['남', '여'])

# 6. 임의의 이메일 주소를 생성하는 함수
def generate_email(name):
    domains = ["@gmail.com", "@naver.com", "@yahoo.com", "@daum.net", "@kakao.com"]
    return name + random.choice(domains)

# 7. 각 txt 파일에 이름, 생성된 나이, 생성된 성별, 생성된 이메일 주소 정보를 쓰는 함수
def write_info(names):
    for i, name in enumerate(names, 1):
        age = generate_age()
        gender = generate_gender()
        email = generate_email(name)
        
        with open(f'회원정보/{name}_{i}.txt', 'w') as f:
            f.write(f'이름: {name}\n나이: {age}\n성별: {gender}\n이메일: {email}\n')

# 8. 생성한 함수들을 사용하여 이름 100개에 대해 모든 txt 파일을 생성합니다.
def create_files():
    names = generate_names(100)
    make_directory()
    create_txt_files(names)
    write_info(names)

# 9. 파일 생성 프로세스가 완료되면 '100개의 회원 정보를 담은 텍스트 파일 생성이 완료되었습니다.'라는 메시지를 출력하는 코드를 작성합니다.
create_files()
print('100개의 회원 정보를 담은 텍스트 파일 생성이 완료되었습니다.')
