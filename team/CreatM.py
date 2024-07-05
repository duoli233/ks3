import json

# 训练文件
# 问题文件

#
file_path_train = 'round1_train_and_test/train.txt'
file_path_ques = 'round1_train_and_test/valid_ques.txt'

# 测试数据
# file_path_train = 'train.txt'
# file_path_ques = 'valid_ques.txt'

# 训练数据处理后的json文件
# Path to your JSON file
file_path_train_json = 'data/train.json'
# 最终答案的搜索语句
file_path_search_word = 'data/search.txt'
# 最终答案
file_path_answer = 'data/answer.txt'

# the_triple = ga.load(data_base)
# monitor = ga.monitor(data_base)
# print(monitor)

# 加载训练集
class QAExtractor:
    def __init__(self, filepath):
        self.filepath = filepath
        self.questions = []
        self.queries = []
        self.answers = []

    def extract(self):
        with open(self.filepath, 'r', encoding='utf-8') as file:
            data = file.readlines()

        for i in range(0, len(data), 4):
            question = data[i].split(':', 1)[1].strip()
            query = data[i+1].strip()
            answer = data[i+2].strip()

            self.questions.append(question)
            self.queries.append(query)
            self.answers.append(answer)

    def get_questions(self):
        return self.questions

    def get_queries(self):
        return self.queries

    def get_answers(self):
        return self.answers

    def print_extracted_data(self):
        print("Questions:")
        for q in self.questions:
            print(q)

        print("\nQueries:")
        for q in self.queries:
            print(q)

        print("\nAnswers:")
        for a in self.answers:
            print(a)

# 加载问题
class QUExtractor:
    def __init__(self, filepath):
        self.filepath = filepath
        self.questions = []

    def extract(self):
        with open(self.filepath, 'r', encoding='utf-8') as file:
            data = file.readlines()

        for i in data:
            question = i.split(':', 1)[1].strip()  # Split on the first colon and strip any surrounding whitespace
            self.questions.append(question)

    def get_questions(self):
        return self.questions

    def print_extracted_data(self):
        print("Questions:")
        for q in self.questions:
            print(q)


# 使用示例
if __name__ == "__main__":

    extractor = QAExtractor(file_path_train)
    extractor.extract()

    # 获取训练集单独的列表
    questions = extractor.get_questions()
    queries = extractor.get_queries()
    answers = extractor.get_answers()

    # 构建 JSON 数据结构
    json_data = []

    json_data.append({
        "role": "system",
        "content": "You are a helpful assistant. Now, "
                   "I need you to learn the following sentences and generate Gstore query statements based on their meanings. "
                   "You do not need to answer the question, just provide the SPARQL query."
    })
    for question, query in zip(questions, queries):
        json_data.append({
            "role": "user",
            "content": question
        })
        json_data.append({
            "role": "assistant",
            "content": query
        })

    # 写入 JSON 文件
    with open(file_path_train_json, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

    print("JSON 文件已生成：train.json")



