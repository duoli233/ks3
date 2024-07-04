from Gstore import GstoreConnector
import re
import CreatM
import Train
import time


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
        query_pattern = re.compile(r'^select \?\w+ where \{ .* \}', re.IGNORECASE)
        # 生成搜索值
        search_value = []
        count = 0
        maxcount = 200
        for message in queries:
            print(message)
            # 符合要求，直接退出循环
            if query_pattern.match(message.strip()):
                triples = Train.split_sparql_triples(message)
                # 查询语句不为空
                if triples != []:
                    # 里面实体符合规则
                    if Train.has_variable_entity(triples):
                        re_value = ga.query(data_base, "json", message)
                        count += 1
                        matches = re.findall(r'"value":"(.*?)"', re_value)
                        print(matches)
                        search_value.append(matches)
                        if count >= maxcount:
                            time.sleep(3)
                            count = 0
                        continue
            search_value.append(" ")
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
    for i in queries:
        print(i)
    value = Search().search(queries)
    write_answer(CreatM.file_path_answer, value)
