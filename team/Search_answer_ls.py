from Gstore import GstoreConnector
import re
import CreatM
import Train
import time
import json

# Gstore数据库配置
ip = "localhost"
port = 20024
username = "root"
password = "123456"
data_base = "pkubase"
ga = GstoreConnector(ip, port, username, password)


# 加载数据库
# the_triple = ga.load(data_base)

class Search:
    def __init__(self):
        self.search_value = []

    def search(self, queries):

        # 生成搜索值
        search_value = []
        count = 0
        maxcount = 100
        for message in queries:
            print(message)
            re_value = ga.query(data_base, "json", message)
            data_dict = json.loads(re_value)
            # 未查询到数据
            if data_dict['StatusCode'] == 1005:
                search_value.append([])
                continue
            value = data_dict["results"]["bindings"]
            # 未查询到数据
            if value == []:
                search_value.append([])
                continue
            count += 1
            match = re.search(r'\?(\w+)', message).group(1)
            values = [item[match]['value'] for item in value]
            print(values)
            search_value.append(values)
            if count >= maxcount:
                time.sleep(5)
                count = 0
                continue
        return search_value


def write_answer(filepath, value):
    with open(filepath, 'w', encoding='utf-8') as file:
        for item in value:
            if item == []:
                file.write("<>")
            else:
                for i in item:
                    file.write("<" + i + ">" + '\t')
            file.write('\n')


if __name__ == '__main__':
    queries = Train.read_text(CreatM.file_path_search_word)
    value = Search().search(queries)
    write_answer(CreatM.file_path_answer, value)
    print('搜素答案完毕')
