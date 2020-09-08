import re


def end_num(string):
    list1 = []
    # 以一个数字结尾字符串
    text = re.compile(r"__.*?[0-9]$")
    if text.search(string):
        list1.append(string)
        return list1
    else:
        pass


print(end_num('abcdef'))
print(end_num('abcdef__1'))
