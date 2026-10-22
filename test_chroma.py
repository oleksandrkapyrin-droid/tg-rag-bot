import chromadb


client = chromadb.Client()
collection = client.create_collection(name='my_docs')


collection.add(
    documents=['The cat sits on the table', 'The dog barks in the yard', 'Python is a programming language'],
    ids=["1", "2", "3"]
)           

results = collection.query(
    query_texts=['What is a programming language?'],
    n_results=1
    )

print(results)