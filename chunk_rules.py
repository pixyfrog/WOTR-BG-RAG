import os

def load_and_chunk_rules(file_path, chunk_size=400, chunk_overlap=100):
    # 1. Read the text file
    if not os.path.exists(file_path):
        print(f"Error: Could not find the file at {file_path}")
        return []
        
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"--- Successfully loaded rulebook sample ({len(text)} characters) ---")
    
    # 2. Naive chunking algorithm (Splitting by characters with overlap)
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        # Move the cursor forward by chunk_size minus the overlap
        start += (chunk_size - chunk_overlap)
        
    return chunks

# --- Main Execution ---
if __name__ == "__main__":
    # Define the path to our data file
    sample_file = os.path.join("data", "rules_sample.txt")
    
    # Run the chunker
    all_chunks = load_and_chunk_rules(sample_file, chunk_size=500, chunk_overlap=100)
    
    # Print the results to see how it looks
    print(f"Generated {len(all_chunks)} text chunks for the AI database.\n")
    
    for i, chunk in enumerate(all_chunks[:3]): # Show just the first 3 chunks as a preview
        print(f"=== CHUNK {i+1} ===")
        print(chunk.strip())
        print("-" * 30 + "\n")