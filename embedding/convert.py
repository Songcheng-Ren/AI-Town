from text2vec import SentenceModel
import numpy as np

def get_embedding(text: str):
    model = SentenceModel(model_name_or_path='./shibing624/text2vec-base-chinese')
    return model.encode(text)

def embedding2str(embedding):
    return ','.join(map(str, embedding))


def str2embedding(embedding_str):
    return np.fromstring(embedding_str, sep=',')


def top5embedding(embeddings):
    pass