import os
from datasets import load_dataset
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

def run_chunking():
    """Load scraped JSON data, chunk it, embed it, and save to FAISS index."""
    try:
        print("Starting data chunking and FAISS indexing...")

        scraped_dir = os.path.join(os.getcwd(), 'scraped_data')
        index_dir = os.path.join(os.getcwd(), 'faiss_index')

        # Load dataset
        dataset = load_dataset("json", data_dir=scraped_dir, split="train")

        # Convert into LangChain Document objects
        docs = [
            Document(
                page_content=item['text'],
                metadata={"url": item['url'], "title": item['title']}
            )
            for item in dataset if "text" in item
        ]

        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        all_splits = text_splitter.split_documents(docs)

        # Embed and create FAISS vector store
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vector_store = FAISS.from_documents(all_splits, embeddings)

        # Save vector index
        vector_store.save_local(index_dir)

        print(f"FAISS index saved at: {index_dir}")

    except Exception as e:
        print(f"Error in run_chunking(): {str(e)}")
        raise

# CLI support
if __name__ == "__main__":
    run_chunking()
