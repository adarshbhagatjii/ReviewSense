from fastembed import TextEmbedding

model = TextEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def create_embedding(text):
    embedding = list(model.embed([text]))[0]

    return embedding.tolist()