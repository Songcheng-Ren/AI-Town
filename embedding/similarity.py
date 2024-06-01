import chromadb
chroma_client = chromadb.PersistentClient(path="/python/AI-Town/embedding/data")

collection = chroma_client.get_or_create_collection(name="ai-town", metadata={"hnsw:space": "cosine"})


def addData(player_id, text):
    index = collection.count()
    index = str(index)
    collection.add(
        documents=[text],
        metadatas=[{"source": player_id}],
        ids=[index]
    )
    print("插入向量成功！")
    return index


def getTop(player_id, text, num):
    results = collection.query(
        query_texts=[text],
        n_results=num,
        where={"source": player_id}
    )
    related_memory = ""
    i = 1
    for result in results["documents"][0]:
        related_memory = related_memory + str(i) + "." + result + "\n"
    return related_memory
