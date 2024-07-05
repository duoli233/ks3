import json
import openai
from CreatM import QUExtractor
from openai import OpenAI
import CreatM
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import copy
import re

api_key = "sk-3g9Z5bQ4DWLQMKpMBb42A820Cb424e599822C882A055Ab32"
base_url = "https://api.gpt.ge/v1/"

openai.api_key = api_key
openai.base_url = base_url
openai.default_headers = {"x-foo": "true"}


# 读取训练集信息，并且使用api训练
class Train:
    def __init__(self, raw_data):
        self.data = raw_data
        self.search_word = []
        OpenAI.api_key = api_key
        self.model = "gpt-3.5-turbo"
        self.url = base_url
        os.environ["OPENAI_BASE_URL"] = base_url
        os.environ["OPENAI_API_KEY"] = OpenAI.api_key

        self.client = OpenAI(base_url=self.url, api_key=OpenAI.api_key)


    # 更新新的查询语句
    def re_flash(self, question):
        # New data to append
        # 将原始训练集拿出来

        # 创建第一个JSON对象的副本
        data_copy = copy.deepcopy(self.data)
        new_entry = {
            "role": "user",
            "content": question
        }
        data_copy.append(new_entry)
        return data_copy

    # 使用chartGPT生成回答
    def generate_response(self, data):
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=data,
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        message = completion.choices[0].message.content
        return message

    def generate_test(self, question_data):
        a = 1
        return ""

    # 训练主控函数
    def train_start(self, questions):
        query_pattern = re.compile(r'^select \?\w+ where \{ .* \}', re.IGNORECASE)
        max_retries = 4
        for i in questions:
            print("问题:" + i)
            question_data = self.re_flash(i)
            # 输出最后两个数据
            # last_data = question_data[-3:]
            # print("最后几个数据为:", last_data)
            message = ""
            retries = 0
            # 进入循环，筛选有效信息
            while retries < max_retries:
                try:
                    message = self.generate_response(question_data)
                    message = message.replace("\n", "")
                except Exception as e:
                    print("出现错误，未知错误")
                    # retries = max_retries + 1
                    retries += 1
                    continue
                # 查错时使用
                # message = self.generate_test(question_data)

                # 符合要求，直接退出循环
                if query_pattern.match(message.strip()):
                    triples = split_sparql_triples(message)
                    if triples != []:
                        # 正确就直接退出，错误就重新查找
                        if has_variable_entity(triples):
                            break
                print("Received invalid response, retrying...", message)
                retries += 1
            # 超过上限，跳过这个问题
            if retries == max_retries:
                print(f"Skipping question '{i}' after {max_retries} failed attempts.")
                output_str = f"Skipping question '{i}' after {max_retries} failed attempts."
            elif retries == max_retries + 1:
                print(f"Skipping question '{i}' ,have a Exception.")
                output_str = f"Skipping question '{i}' , have a Exception."
            else:
                output_str = message.replace("\n", "")
            # 加入我的查找语句列表中
            print("GPT回答:" + output_str)
            self.search_word.append(output_str)
        return self.search_word


def write_text(filepath, value):
    with open(filepath, 'w', encoding='utf-8') as file:
        for item in value:
            file.write(item + '\n')


def read_text(filepath):
    value = []
    with open(filepath, 'r', encoding='utf-8') as file:
        data = file.readlines()
    for i in data:
        value.append(i.strip())  # 添加每一行去掉末尾换行符的内容，保留空行
    return value

# Function to read the JSON file
def read_json(file_path, num_items=301):
    if num_items % 2 == 0:
        num_items -= 1
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        selected_data = data[:num_items]  # 取前 num_items 条记录
    return selected_data


# 步长为20，抽取样例数组
def read_json_jump(file_path, jump_step=110):
    if jump_step % 2 != 0:
        jump_step -= 1
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        selected_data = extract_elements(data, jump_step)
    return selected_data

# 跳跃实现函数
def extract_elements(data, jump_step):
    result = []

    # 获取第一个元素
    if len(data) > 0:
        result.append(data[0])

    # 从索引1开始，每取2个元素，跳过20个元素
    index = 1
    # print(len(data))
    while index < len(data):
        # 提取两个元素
        for _ in range(2):
            if index < len(data):
                result.append(data[index])
                index += 1
            else:
                break
        # 跳过jump_step个元素
        index += jump_step
        # print(index)

    return result

# 切分数组
def split_sparql_triples(sparql_query):
    # Extract the part inside the braces
    match = re.search(r'{(.*?)}', sparql_query, re.DOTALL)
    if match:
        inside_braces = match.group(1).strip()
        triples = []
        buffer = ''
        in_quotes = False
        in_angle_brackets = False

        for char in inside_braces:
            if char == '"':
                in_quotes = not in_quotes
            elif char == '<':
                in_angle_brackets = True
            elif char == '>':
                in_angle_brackets = False
            elif char == '.' and not in_quotes and not in_angle_brackets:
                triples.append(buffer.strip())
                buffer = ''
                continue
            buffer += char

        if buffer.strip():
            triples.append(buffer.strip())

        return triples
    else:
        return []

# 查询是否正常
def has_variable_entity(triples):
    for triple in triples:
        # Remove content inside <...> and "..."
        triple_without_brackets = re.sub(r'<.*?>', '', triple)
        triple_without_quotes = re.sub(r'"(.*?)"', '', triple_without_brackets)

        # Check for ? followed by letters or numbers
        match = re.search(r'\?[\w\d]+', triple_without_quotes)
        if not match:
            return False
    # 错误返回False
    return True


def process_questions(questions):
    tra = Train(selected_data)
    return tra.train_start(questions)


if __name__ == '__main__':
    # data = read_json(CreatM.file_path_train_json)
    selected_data = read_json_jump(CreatM.file_path_train_json)
    # 加载问题
    ques_extractor = QUExtractor(CreatM.file_path_ques)
    ques_extractor.extract()
    valid_ques = ques_extractor.get_questions()
    # for i in selected_data:
    #     print(i)
    print(len(selected_data))
    # Split questions into chunks of 100
    num_question = 100
    chunks = [valid_ques[i:i + num_question] for i in range(0, len(valid_ques), num_question)]
    print(chunks)
    # Use ThreadPoolExecutor to process chunks concurrently
    search_word = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(process_questions, chunks)
        for result in results:
            search_word.extend(result)

    write_text(CreatM.file_path_search_word, search_word)
    print("已经完成全部回答！！！")