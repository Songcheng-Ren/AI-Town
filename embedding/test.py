import numpy as np

def embedding_to_string(embedding):
    # 将 numpy 数组转换为以逗号分隔的字符串
    return ','.join(map(str, embedding))

# 示例 embedding
embedding = np.random.rand(5)  # 一个5维的随机向量
embedding_str = embedding_to_string(embedding)
print("Embedding as String:", embedding_str)