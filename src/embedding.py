from typing import List , Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer 
# pyrefly: ignore [missing-import]
from src.data_loader import load_all_documents 

class EmbeddingPipeline:
    def __init__(self, model_name: str="all-MiniLM-L6-v2", chunk_size:int=1000, chunk_overlap:int=200):
        
        self.chunk_size=chunk_size
        self.chunk_overlap=chunk_overlap
        self.model=SentenceTransformer(model_name)
        print(f"loaded embedding model : {model_name}")


    def chunk_documents(self,docs:List[Any]) -> List[Any]:
        """Chunk the documents for better processing """

        text_splitter=RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", " "]
        )

        # chunks documents 
        print(f"chunking {len(docs)} documents")
        chunked_documents=text_splitter.split_documents(docs)
        print(f"created {len(chunked_documents)} chunks")

        return chunked_documents

    def embedd_chunks(self,docs:List[Any]) -> List[Any]:
        """Embedding the documents """

        #extract text from documents 
        texts=[doc.page_content for doc in docs]
        # embedding 
        print(f"embedding {len(docs)} chunks ...")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        print(f"embeddings shape : {embeddings.shape}")
        return embeddings

        

        