import os
import pickle
from dotenv import load_dotenv
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# === CONFIG ===
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

PDF_PATH = "Pakistan_Penal_Code_with_Index.pdf"
VECTOR_DIR = "vectorstore"
INDEX_NAME = "index"

def load_and_chunk_pdf(pdf_path):
    print(f"[🔍] Loading and chunking PDF: {pdf_path}")
    loader = PyMuPDFLoader(pdf_path)
    documents = loader.load()

    # Add consistent metadata
    for i, doc in enumerate(documents):
        doc.metadata["source"] = pdf_path
        doc.metadata["page"] = doc.metadata.get("page", i + 1)

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)
    print(f"[📄] Total chunks created: {len(chunks)}")
    return chunks

def embed_and_save(chunks, save_dir, index_name="index"):
    print("[🧠] Embedding chunks using OpenAI...")
    embeddings = OpenAIEmbeddings()
    db = FAISS.from_documents(chunks, embeddings)

    # Save vector index
    db.save_local(save_dir, index_name=index_name)
    print(f"[✔] Vectorstore saved to '{save_dir}/{index_name}.faiss'")

    # Optionally save chunks for inspection
    with open(os.path.join(save_dir, "chunks.pkl"), "wb") as f:
        pickle.dump(chunks, f)
    print(f"[🧾] Chunks saved to '{save_dir}/chunks.pkl'")

if __name__ == "__main__":
    chunks = load_and_chunk_pdf(PDF_PATH)
    os.makedirs(VECTOR_DIR, exist_ok=True)
    embed_and_save(chunks, VECTOR_DIR, index_name=INDEX_NAME)
