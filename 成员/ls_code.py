from neo4j import GraphDatabase
import csv


class GraphImporter:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_entity_relationship(self, entity, relationship, value):
        with self.driver.session() as session:
            session.write_transaction(self._create_and_return_relationship, entity, relationship, value)

    @staticmethod
    def _create_and_return_relationship(tx, entity, relationship, value):
        query = (
            "MERGE (e:Entity {name: $entity}) "
            "MERGE (v:Value {name: $value}) "
            "MERGE (e)-[r:RELATIONSHIP {type: $relationship}]->(v) "
            "RETURN e, r, v"
        )
        tx.run(query, entity=entity, relationship=relationship, value=value)


def import_csv(file_path, graph_importer, batch_size=10000):
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        batch = []
        count = 0  # 初始化计数器
        for row in reader:
            entity, relationship, value = row
            batch.append((entity, relationship, value))
            if len(batch) >= batch_size:
                process_batch(batch, graph_importer)
                print(f"Processed \ rows")  # 输出读取的总行数
                end = time.time()
                batch = []
                print(end - start)
        if batch:
            process_batch(batch, graph_importer)


def process_batch(batch, graph_importer):
    for entity, relationship, value in batch:
        graph_importer.create_entity_relationship(entity, relationship, value)


# 创建知识图谱
if __name__ == "__main__":
    graph_importer = GraphImporter('bolt://localhost:7687', "neo4j", "87654321")
    import_csv("triple.csv", graph_importer)
    graph_importer.close()

