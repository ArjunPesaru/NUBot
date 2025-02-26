import streamlit as st
import faiss
import pickle
import numpy as np
import ollama
from langchain_huggingface import HuggingFaceEmbeddings  # Updated import
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# File paths
FAISS_INDEX_PATH = "/Users/arjunpesaru/Desktop/S22/s22 updated/NUBot/vector_index.faiss"
METADATA_PATH = "/Users/arjunpesaru/Desktop/S22/s22 updated/NUBot/metadata.pkl"

# Initialize chatbot class
class RAGChatbot:
    def __init__(self, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize chatbot with FAISS index and embeddings"""
        logger.info("Initializing RAGChatbot...")
        self.embedding_model = embedding_model
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        self.vector_store = None
        self.metadata = {}
        self._load_index()

    def _load_index(self):
        """Load FAISS index and metadata"""
        logger.info("Loading FAISS index and metadata...")
        if not Path(FAISS_INDEX_PATH).exists():
            logger.error(f"FAISS index file not found at {FAISS_INDEX_PATH}")
            return
        if not Path(METADATA_PATH).exists():
            logger.error(f"Metadata file not found at {METADATA_PATH}")
            return

        try:
            self.vector_store = faiss.read_index(FAISS_INDEX_PATH)
            logger.info("FAISS index loaded successfully.")
            with open(METADATA_PATH, "rb") as f:
                self.metadata = pickle.load(f)
            logger.info("Metadata loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading FAISS index or metadata: {e}")

    def retrieve_documents(self, query: str, top_k: int = 3):
        """Retrieve relevant documents based on query"""
        logger.info("Retrieving relevant documents...")
        query_embedding = self.embeddings.embed_query(query)
        if self.vector_store:
            try:
                distances, indices = self.vector_store.search(np.array([query_embedding]), top_k)
                retrieved_texts = [
                    self.metadata["documents"][idx] for idx in indices[0] if 0 <= idx < len(self.metadata["documents"])
                ]
                return "\n\n".join(retrieved_texts) if retrieved_texts else "No relevant documents found."
            except Exception as e:
                logger.error(f"Error retrieving documents: {e}")
                return "No relevant information found."
        else:
            logger.error("FAISS index is not loaded.")
            return "No relevant information found."

    def generate_response(self, context: str, query: str):
        """Generate response using Ollama"""
        logger.info("Generating response using Ollama...")
        prompt = f"""
        You are an expert assistant providing accurate information based on the given context. 
        Answer concisely and accurately.
        
        Context:
        {context}
        
        Question: {query}
        Response:
        """
        try:
            response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
            return response['message']['content'].strip()
        except Exception as e:
            logger.error(f"Error generating response with Ollama: {e}")
            return "I encountered an error while generating a response."

    def query(self, user_query: str):
        """Process user query"""
        retrieved_context = self.retrieve_documents(user_query)
        if not retrieved_context:
            return "I'm sorry, but I couldn't find relevant information. Please try rephrasing."
        return self.generate_response(retrieved_context, user_query)


# Initialize chatbot
chatbot = RAGChatbot()

# Streamlit UI
st.set_page_config(page_title="NUBot", page_icon="🤖", layout="wide")

# Sidebar
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/6/6d/Northeastern_Wordmark.png", width=250)
st.sidebar.title("NUBot")
st.sidebar.markdown("**A chatbot for Khoury College FAQs.**")
st.sidebar.markdown("---")


# Main UI
st.title("🤖 NUBot - Northeastern University Chatbot")
st.write("Ask me anything about **Northeastern University!**")

# Custom Chat History Styling
st.markdown(
    """
    <style>
    .user-message {
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    .bot-message {
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    .chat-container {
        max-width: 700px;
        margin: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ✅ Fix: Initialize chat history before using it
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat history
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for sender, message in st.session_state["messages"]:
    if sender == "You":
        st.markdown(f'<div class="user-message"><b>🧑‍💻 {sender}:</b> {message}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-message"><b>🤖 {sender}:</b> {message}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# User input
user_input = st.text_input("Type your question below:", key="input", placeholder="E.g., What are the degree programs?")

# Process user input
if st.button("Ask"):
    if user_input:
        response = chatbot.query(user_input)
        
        # Append to chat history
        st.session_state["messages"].append(("You", user_input))
        st.session_state["messages"].append(("NUBot", response))

        # Rerun Streamlit app to update chat display
        st.experimental_rerun()

# Footer
st.markdown("---")
st.markdown("🤖 **NUBot - Built with FAISS & Ollama**")

