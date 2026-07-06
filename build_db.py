import os
import chromadb
from chromadb.utils import embedding_functions
from chunk_rules import load_and_chunk_rules  # Recycles your Week 1 script!

def create_local_database():
    print("--- 🧠 Initializing AI Embedding Model ---")
    # This sets up a tiny, free, highly efficient open-source embedding model
    # It runs completely offline once downloaded the first time
    embedding_model = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    print("--- 🗄️ Creating Local ChromaDB Directory ---")
    # This creates a folder named 'wotr_vector_db' inside your project directory
    chroma_client = chromadb.PersistentClient(path="wotr_vector_db")
    
    # Create or load a "collection" (like a table in a database)
    collection = chroma_client.get_or_create_collection(
        name="wotr_rules", 
        embedding_function=embedding_model
    )

    # 1. Load and chunk our War of the Ring rules text file
    sample_file = os.path.join("data", "rules_sample.txt")
    chunks = load_and_chunk_rules(sample_file, chunk_size=500, chunk_overlap=100)
    
    if not chunks:
        print("Error: No chunks found to inject into database.")
        return

    print(f"--- 📥 Injecting {len(chunks)} chunks into ChromaDB ---")
    
    # 2. Prepare data for the database
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    # Metadata helps your script track where the data came from
    metadatas = [{"source": "rules_sample.txt"} for _ in range(len(chunks))]

    # 3. Save it! ChromaDB automatically runs the text through the embedding model and stores the numbers
    collection.add(
        documents=chunks,
        ids=ids,
        metadatas=metadatas
    )
    
    print("\n🎉 Success! Database built permanently in the 'wotr_vector_db' folder.")

if __name__ == "__main__":
    create_local_database()