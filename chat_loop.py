import os
import chromadb
from chromadb.utils import embedding_functions
import ollama

def run_conversational_chat():
    db_path = "wotr_vector_db"
    
    # 1. Connect to our localized vector database
    embedding_model = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    chroma_client = chromadb.PersistentClient(path=db_path)
    collection = chroma_client.get_or_create_collection(
        name="wotr_rules", 
        embedding_function=embedding_model
    )

    print("════════════════════════════════════════════════════════════")
    print("⚔️  WAR OF THE RING AI REFEREE — CONVERSATIONAL MEMORY MODE ⚔️")
    print("   Type your questions below. Type 'exit' or 'quit' to stop. ")
    print("════════════════════════════════════════════════════════════\n")

    # This list will hold our ongoing chat history
    conversation_history = []

    # 2. Enter the continuous execution loop
    while True:
        user_input = input("\n🤓 You: ")
        
        # Check for break keywords
        if user_input.strip().lower() in ['exit', 'quit']:
            print("\n👋 Closing database connection. Safe travels through Middle-earth!")
            break
            
        if not user_input.strip():
            continue

        print("🔍 Searching database (Pulling top 4 matching chunks)...")
        
        # Query the database using the latest input
        results = collection.query(query_texts=[user_input], n_results=4)
        
        # Consolidate text blocks into a ground-truth reference block
        retrieved_documents = results['documents'][0]
        context_block = "\n---\n".join(retrieved_documents)

        # Inject the fresh rules as a system context rule
        system_instruction = {
            "role": "system",
            "content": (
                "You are an expert rulebook referee for the board game 'War of the Ring'.\n"
                "Answer the user's questions using the official rules context provided below.\n"
                "Maintain continuity with previous messages in the chat history.\n"
                "If the context does not contain the answer, rely on the chat history or "
                "state cleanly what is missing.\n\n"
                f"=== CURRENT OFFICIAL RULEBOOK CONTEXT ===\n{context_block}\n=============================="
            )
        }

        # Add the user's new message to our permanent conversation log
        conversation_history.append({"role": "user", "content": user_input})

        # Construct the payload: System Instructions + Full Chat History
        payload = [system_instruction] + conversation_history

        print("🤖 Thinking...")
        try:
            # Using ollama.chat() instead of ollama.generate() to parse the historical array
            response = ollama.chat(
                model='qwen',
                messages=payload,
                options={
                    "temperature": 0.4,       # Unlocks enough fluid logic to prevent looping
                    "repeat_penalty": 1.15     # Actively penalizes the model if it tries to repeat phrases
                }
            )
            
            bot_answer = response['message']['content']
            
            print("\n🧙 Bot Output:")
            print(bot_answer)
            print("\n" + "─"*50)
            
            # Save the bot's response to the conversation history so it remembers what it said!
            conversation_history.append({"role": "assistant", "content": bot_answer})
            
        except Exception as e:
            print(f"\n❌ Error connecting to local Ollama server: {e}")
            print("Make sure Ollama is currently running in your background taskbar!")

if __name__ == "__main__":
    run_conversational_chat()