import streamlit as st
import chromadb
from chromadb.utils import embedding_functions
import ollama

# Set up the browser tab properties
st.set_page_config(page_title="WOTR AI Referee", layout="wide")

# 1. Initialize our localized engines (Cached so it loads instantly after the first boot!)
@st.cache_resource
def initialize_database():
    db_path = "wotr_vector_db"
    embedding_model = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    chroma_client = chromadb.PersistentClient(path=db_path)
    collection = chroma_client.get_or_create_collection(
        name="wotr_rules", 
        embedding_function=embedding_model
    )
    return collection

collection = initialize_database()

# 2. Maintain state management inside the browser session memory
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_retrieved_chunks" not in st.session_state:
    st.session_state.last_retrieved_chunks = []

# 3. Create the Graphical Layout Structure
st.title("⚔️ War of the Ring: Local AI Referee Workspace")
st.caption("A private, entirely offline semantic search and rules consultation terminal.")

# Split the browser window into two columns (Main Chat vs Right-Side Inspector)
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("💬 Rules Consultation Chat")
    
    # Display the conversation history elegantly using Streamlit's built-in chat UI bubbles
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User Input Field
    if user_query := st.chat_input("Ask a rule question... (e.g., 'How many dice does the Shadow start with?')"):
        
        # Display user question instantly
        with st.chat_message("user"):
            st.markdown(user_query)
        st.session_state.messages.append({"role": "user", "content": user_query})

        # Run database retrieval
        with st.spinner("Searching vector blocks..."):
            results = collection.query(query_texts=[user_query], n_results=8)
            retrieved_docs = results['documents'][0] if results['documents'] else []
            
            # Save these chunks to the session state so the right-side inspector updates live
            st.session_state.last_retrieved_chunks = retrieved_docs
            
        # Compile Context System String
        context_block = "\n---\n".join(retrieved_docs)
        system_instruction = {
            "role": "system",
            "content": (
                "You are an expert rulebook referee for the board game 'War of the Ring'.\n"
                "Answer the user's question using ONLY the rules context provided below.\n"
                "CRITICAL INSTRUCTION: If the context below does not contain the explicit answer to the question, "
                "say exactly: 'I cannot find that specific rule in the provided context blocks.' Do not guess or extrapolate.\n\n"
                f"=== OFFICIAL RULES CONTEXT ===\n{context_block}\n=============================="
            )
        }

        # Format historical messages for ollama.chat
        api_messages = [system_instruction] + [
            {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
        ]

        # Query Local LLM Engine
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            with st.spinner("Refine processing..."):
                try:
                    response = ollama.chat(
                        model='qwen',
                        messages=api_messages,
                        options={
                            "temperature": 0.1,       # Lowered slightly to tighten precision
                            "num_ctx": 8192,
                            "repeat_penalty": 1.2
                        }
                    )
                    bot_answer = response['message']['content']
                    response_placeholder.markdown(bot_answer)
                    
                    # Save assistant response to state memory
                    st.session_state.messages.append({"role": "assistant", "content": bot_answer})
                    
                except Exception as e:
                    st.error(f"Ollama Connection Error: {e}")
        
        # Rerun to cleanly update the sidebar inspector layouts
        st.rerun()

with col2:
    st.subheader("🔍 Vector Database Inspector")
    st.info("The text blocks displayed below represent the exact ground-truth segments pulled by your search engine.")
    
    if st.session_state.last_retrieved_chunks:
        for idx, chunk in enumerate(st.session_state.last_retrieved_chunks):
            with st.expander(f"📄 Retrieved Data Block #{idx + 1}", expanded=True):
                st.text_area(label=f"Source Context Snippet #{idx+1}", value=chunk, height=180, disabled=True, label_visibility="collapsed")
    else:
        st.write("No active query run yet. Type a question on the left to inspect vector search precision.")