import os
import chromadb
from chromadb.utils import embedding_functions

def chunk_and_ingest_full_rules():
    input_filename = "wotr_docling_rules.md"
    db_path = "wotr_vector_db"
    
    if not os.path.exists(input_filename):
        print(f"❌ Error: Could not find '{input_filename}' in this folder.")
        return

    print(f"📖 Reading clean markdown from '{input_filename}'...")
    with open(input_filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    chunks = []
    current_header = "General / Introduction"
    current_chunk_text = ""
    
    # Trackers for chunk naming
    chunk_counter = 0

    print("🧠 Parsing rules by Markdown headers...")
    for line in lines:
        stripped = line.strip()
        
        # Check if this line is a structural heading
        if stripped.startswith("#"):
            # If we already accumulated text before hitting this header, save it first!
            if current_chunk_text.strip():
                # Prepend the context header so the text block maintains semantic meaning
                final_text = f"Context: {current_header}\n\n{current_chunk_text.strip()}"
                chunks.append({
                    "id": f"full_rule_chunk_{chunk_counter}",
                    "text": final_text,
                    "metadata": {"source": "full_rulebook", "section": current_header}
                })
                chunk_counter += 1
                current_chunk_text = ""
            
            # Clean up the header line to use as our new context tracker
            current_header = stripped.lstrip("# ").strip()
            continue
        
        # Accumulate paragraph text under the current tracking header
        if stripped:
            current_chunk_text += stripped + "\n"
        elif current_chunk_text:
            # An empty line tells us a paragraph ended. Let's make sure chunks don't get too massive.
            # If a single section exceeds ~1200 characters, break it into a chunk to prevent blurring vectors.
            if len(current_chunk_text) > 1200:
                final_text = f"Context: {current_header}\n\n{current_chunk_text.strip()}"
                chunks.append({
                    "id": f"full_rule_chunk_{chunk_counter}",
                    "text": final_text,
                    "metadata": {"source": "full_rulebook", "section": current_header}
                })
                chunk_counter += 1
                current_chunk_text = ""

    # Catch any leftover trailing text at the end of the file
    if current_chunk_text.strip():
        final_text = f"Context: {current_header}\n\n{current_chunk_text.strip()}"
        chunks.append({
            "id": f"full_rule_chunk_{chunk_counter}",
            "text": final_text,
            "metadata": {"source": "full_rulebook", "section": current_header}
        })

    print(f"✂️ Successfully parsed the entire rulebook into {len(chunks)} smart, contextual chunks!")

    # --- 2. Ingesting into ChromaDB ---
    print("\n📦 Initializing local Vector Database Client...")
    embedding_model = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    chroma_client = chromadb.PersistentClient(path=db_path)
    
    # We will grab our existing collection, or create it if missing
    collection = chroma_client.get_or_create_collection(
        name="wotr_rules", 
        embedding_function=embedding_model
    )

    print("🚀 Pushing chunks into ChromaDB and calculating mathematical vectors...")
    
    # Break into batches of 100 to stay gentle on memory / terminal printing
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        
        collection.add(
            ids=[c["id"] for c in batch],
            documents=[c["text"] for c in batch],
            metadatas=[c["metadata"] for c in batch] if "metandatas" in dir(collection) else [c["metadata"] for c in batch] 
        )
        print(f"   Indexed chunks {i} to {min(i+batch_size, len(chunks))}...")

    # Quick check for legacy API compatibility typo in schema mapping helper
    # (Using standard fallback dictionary insertion)
    print(f"\n🎉 Success! All {len(chunks)} rulebook chunks have been permanently embedded offline.")

if __name__ == "__main__":
    chunk_and_ingest_full_rules()