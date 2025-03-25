from langchain_text_splitters import RecursiveCharacterTextSplitter
from datasets import load_dataset
import os
from langchain.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

def chunk_data():
    # Load all JSON files from a directory
    try:
        dataset = load_dataset("json", data_dir=os.path.join(os.getcwd(),'scraped_data'),split="train")
        docs = [ Document(
                page_content=item['text'],
                metadata={"url": item['url'], "title": item['title']}
            )for item in dataset if "text" in item] 

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        all_splits = text_splitter.split_documents(docs)
        # Initialize the embedding model
        embeddings= HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vector_store = FAISS.from_documents(all_splits, embeddings)
        # Convert documents into FAISS-compatible format
        _ = vector_store.add_documents(documents=all_splits)
        # Save FAISS index
        vector_store.save_local('faiss_index')
        
        return 
    except Exception as e:
        raise Exception(e)


if __name__=="__main__":
    chunk_data()

