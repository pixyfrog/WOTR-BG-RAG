import chromadb
from chromadb.utils import embedding_functions
import ollama

# 1. Connect to our local ChromaDB Vector Database (Week 2)
embedding_model = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
chroma_client = chromadb.PersistentClient(path="wotr_vector_db")
collection = chroma_client.get_collection(name="wotr_rules", embedding_function=embedding_model)

def ask_wotr_bot(user_question):
    print(f"\n🤔 Question: {user_question}")
    print("🔍 Searching local database for rule chunks...")
    
    # 2. Query the database for the top 2 closest matching chunks
    db_results = collection.query(
        query_texts=[user_question],
        n_results=2
    )
    
    # Extract the text from the matching chunks
    fetched_chunks = db_results['documents'][0]
    
    # Combine the chunks into a single reference block for the AI
    context_text = "\n\n".join(fetched_chunks)
    
    print("🧠 Rules found! Asking local LLM to synthesize the answer...")
    
    # 3. Create the prompt script for the LLM
    # We strictly instruct the AI to ONLY use the provided rule text
    system_prompt = (
        "You are an expert rule referee for the board game 'War of the Ring'. "
        "Your job is to answer the player's question clearly and concisely. "
        "CRITICAL: Use ONLY the provided 'Game Rule Context' below to answer. "
        "If the context does not contain the answer, say 'I cannot find that in the loaded rules sample.' "
        "Do not invent rules."
    )
    
    user_prompt = f"Game Rule Context:\n{context_text}\n\nPlayer Question: {user_question}"
    
    # 4. Stream the answer back from our local Ollama model
    response = ollama.chat(
        model='qwen2.5:1.5b',
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        options={
            'temperature': 0.0  # <--- ADD THIS LINE! Forces strict adherence to facts.
        }
    )
    
    print("\n🤖 AI Referee Answer:")
    print(response['message']['content'])
    print("=" * 40)

# --- Test the RAG System ---
if __name__ == "__main__":
    # Test Question that exists in our rules sample
    ask_wotr_bot("How many dice can the shadow player allocate to the hunt?")