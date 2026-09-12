from torch.library import impl
from importlib import metadata
import os 
import faiss
import pickle
import numpy as np
from typing import List , Any
from sentence_transformers import SentenceTransformer
# pyrefly: ignore [missing-import]
from src.embedding import EmbeddingPipeline

class FaissVectorStore:
    def __init__(self,persist_directory: str= "faiss_store", embedding_model:str="all-MiniLM-L6-v2", chunk_size= 1000, chunk_overlap= 200):
        self.persist_dir= persist_directory
        os.makedirs(self.persist_dir, exist_ok=True)

        self.index= None 
        self.metadata =[]
        self.embedding_model = embedding_model
        self.model = SentenceTransformer(embedding_model)

        self.chunk_size = chunk_size
        self.chunk_overlap =chunk_overlap

        print(f"loaded embedding model: {self.model}")
    
    def build_from_documents(self, documents:List[Any]):
        print(f"building vector store from {len(documents)} raw documents")

        if not documents:
            print("No documents found! Initializing empty vector store.")
            dim = self.model.get_sentence_embedding_dimension()
            if self.index is None:
                self.index = faiss.IndexFlatL2(dim)
            self.save()
            return

        e= EmbeddingPipeline(model_name=self.embedding_model,
         chunk_size=self.chunk_size,
         chunk_overlap=self.chunk_overlap)

        chunks = e.chunk_documents(documents)
        embeddings = e.embedd_chunks(chunks)
        metadatas= [{"text":chunk.page_content} for chunk in chunks]
        self.add_embeddings(np.array(embeddings).astype('float32'), metadatas)

        self.save()
        print(f"--------------- vector store built and saved to {self.persist_dir}")
    
    def add_embeddings(self, embeddings:np.ndarray, metadatas:List[dict]):
        dim= embeddings.shape[1]

        if self.index is None:
            self.index=faiss.IndexFlatL2(dim)
        self.index.add(embeddings)
        if metadatas:
            self.metadata.extend(metadatas)
        print(f"added {len(embeddings)} embeddings. total vectors: {embeddings.shape[0]}")
        
    def save(self):

        faiss_path =  os.path.join(self.persist_dir, "faiss.index")
        faiss.write_index(self.index, faiss_path)

        meta_path =  os.path.join(self.persist_dir, "metadata.pkl")
        with open(meta_path, "wb") as f:
            pickle.dump(self.metadata, f)
        print(f"saved faiss index and metadata store to {self.persist_dir}")

    def load(self):

        faiss_path =  os.path.join(self.persist_dir, "faiss.index")
        meta_path =  os.path.join(self.persist_dir, "metadata.pkl")

        self.index = faiss.read_index(faiss_path)
        with open(meta_path, "rb") as f:
            self.metadata = pickle.load(f)
        print(f"loaded faiss index and metadata from {self.persist_dir}")

    def search(self ,query_embedding:np.ndarray ,top_k:int = 5):
        D,I= self.index.search(np.array([query_embedding]),top_k)
        results=[]
        for idx ,dist in zip(I[0],D[0]):
            if idx == -1:
                continue
            meta= self.metadata[idx] if idx <len(self.metadata) else None
            results.append({
                "index":idx,
                "distance":dist,
                "metadata":meta,
            })
        return results

    def query(self,queryT: str, top_k:int = 5):
        print(f"querying vector store for :{queryT}  with top k:{top_k}")
        query_emb= self.model.encode(queryT).astype('float32')
        return self.search(query_emb,top_k=top_k)

    def clear(self):
        self.index = None
        self.metadata = []
        faiss_path = os.path.join(self.persist_dir, "faiss.index")
        meta_path = os.path.join(self.persist_dir, "metadata.pkl")
        if os.path.exists(faiss_path):
            os.remove(faiss_path)
        if os.path.exists(meta_path):
            os.remove(meta_path)
        print(f"Cleared faiss index and metadata from {self.persist_dir}")