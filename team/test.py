import re


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


def has_variable_entity(triples):
    for triple in triples:
        # Remove content inside <...> and "..."
        triple_without_brackets = re.sub(r'<.*?>', '', triple)
        triple_without_quotes = re.sub(r'"(.*?)"', '', triple_without_brackets)

        # Check for ? followed by letters or numbers
        match = re.search(r'\?[\w\d]+', triple_without_quotes)
        if match:
            return True
    return False


# Example usage
sparql_query = 'SELECT (COUNT(?x) AS ?count) WHERE {?x <代码> "10056" .?x <学位授权类别> <硕士点> .}'
triples = split_sparql_triples(sparql_query)
for triple in triples:
    print(triple)

print("Checking for variable entities...")
has_variable = has_variable_entity(triples)
print(f"Contains variable entities: {has_variable}")

