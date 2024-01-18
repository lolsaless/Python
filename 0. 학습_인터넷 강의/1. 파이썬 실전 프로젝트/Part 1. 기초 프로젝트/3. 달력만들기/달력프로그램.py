def isLeapYear(year):
    return year % 4 == 0 and year % 100 != 0 or year % 400 == 0

def lastDay(year, month):
    m = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    if isLeapYear(year):
        m[1] = 29

    return m[month - 1]

def totalDay(year, month, day):
    total = (year - 1) * 365 + (year - 1) // 4 - (year - 1) // 100 + (year - 1) // 400

    for i in range(1, month):
        total += lastDay(year, i)

    return total + day

def weekDay(year, month ,day):
    return totalDay(year, month, day) % 7

if __name__== "__main__":
    year, month = map(int, input('달력을 출력할 년, 월을 입력하세요: ').split())
    print('=' * 28)
    print('         {0:4d}년{1:2d}월'.format(year, month))
    print('=' * 28)
    print('  일   월   화   수   목   금   토')
    print('=' * 28)

    for i in range(weekDay(year, month, 1)):
        print('     ', end = '')

    for i in range(1, lastDay(year, month) + 1):
        print('  {0:2d} '.format(i), end = '')

        if weekDay(year, month, i) == 6 and i != lastDay(year, month):
            print()

    print('\n' + '=' *28)