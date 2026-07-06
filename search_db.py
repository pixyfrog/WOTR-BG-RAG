import chromadb
from chromadb.utils import embedding_functions

# 1. Connect to the exact database we built
embedding_model = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
chroma_client = chromadb.PersistentClient(path="wotr_vector_db")
collection = chroma_client.get_collection(name="wotr_rules", embedding_function=embedding_model)

# 2. Ask a question!
query = "How many dice can the shadow player allocate to the hunt?"
print(f"Searching database for: '{query}'\n")

# 3. Query the database for the top 2 closest matching chunks
results = collection.query(
    query_texts=[query],
    n_results=2
)

# 4. Print what the AI database found
for i, doc in enumerate(results['documents'][0]):
    print(f"=== MATCHING RULE CHUNK {i+1} ===")
    print(doc.strip())
    print("-" * 30 + "\n")