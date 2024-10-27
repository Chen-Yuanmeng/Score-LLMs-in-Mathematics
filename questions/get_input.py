import json
import time
import getpass

class Question:
    def __init__(self):
        self.unique_id: str = getpass.getuser() + '.' + str(int(time.time()))
        self.category = ""
        self.sub_category = ""
        self.question_Chinese = ""
        self.question_English = "" # optional
        self.answer = ""

    def fill(self, category, sub_category, question_Chinese, question_English, answer):
        self.category = category
        self.sub_category = sub_category
        self.question_Chinese = question_Chinese
        if question_English:
            self.question_English = question_English
        self.answer = answer
    
    def __str__(self):
        return f'''Unique ID: {self.unique_id}
Category: {self.category}
Sub-category: {self.sub_category}
Question in Chinese: {self.question_Chinese}
Question in English: {self.question_English}
Answer: {self.answer}\n
'''

    def dct(self):
        return {
            "Unique ID": self.unique_id,
            "Category": self.category,
            "Sub-category": self.sub_category,
            "Question in Chinese": self.question_Chinese,
            "Question in English": self.question_English,
            "Answer": self.answer
        }

    def direct_fill(self):
        self.fill(
            my_input("请输入大类:"),
            my_input("请输入小类:"),
            my_input("请输入中文问题:"),
            my_input("请输入英文问题: ") if yes_or_no("是否要添加英文版问题?") else "",
            my_input("请输入参考答案:"),
        )



def my_input(prompt: str = '') -> str:
    """
    输入, 避免误触回车键, 返回前确认
    :param prompt: 输入提示
    :return: 用户输入的字符串
    """
    while True:
        text = input(prompt)
        while not text:
            text = input('输入为空, 请重新输入: ')
        print('您的输入是:\n' + text + '\n请确认 (输入n可重新输入) ')

        if yes_or_no():
            return text


def yes_or_no(prompt: str = '') -> bool:
    """
    与用户确认 Yes or No

    :param prompt: 输入提示
    :return: `True/False`
    """
    while True:
        key = input(prompt + '(y/n):').lower()

        if key == "y" or key == "yes":
            return True
        elif key == "n" or key == "no":
            return False
        else:
            print("非法输入, 请输入 y / n:", end="")


def main():
    pool = []
    
    while True:
        ques = Question()
        ques.direct_fill()
        pool.append(ques.dct())

        if not yes_or_no('还要继续输入题目吗?'):
            break

    with open(f'output-{str(int(time.time()))}.json', 'w', encoding='UTF-8') as g:
        json.dump(pool, g, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
