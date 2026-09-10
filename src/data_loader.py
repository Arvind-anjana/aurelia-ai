from typing import List, Any
from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader,TextLoader , CSVLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders.excel import UnstructuredExcelLoader
from langchain_community.document_loaders import JSONLoader

def load_all_documents(data_dir:str)->List[Any]:
    """ load all supported files and convert them to langchain docuent 
    supported :PDf, csv , word , json , excel
    """
    data_path=Path(data_dir).resolve()
    documents=[]


    #Pdf files 

    pdf_files= list(data_path.glob("**/*.pdf"))
    print(f"\nfound {len(pdf_files)} pdf files.")

    for pdf_file in pdf_files :
        try:
            loader = PyMuPDFLoader(str(pdf_file))
            docs = loader.load()
            print(f"loaded {len(docs)} documents")
            documents.extend(docs)
        except Exception as e:
            print(f"error in loading documents : {e}")
    
    # text files

    text_files= list(data_path.glob("**/*.txt"))
    print(f"\nfound {len(text_files)} text files.")

    for text_file in text_files :
        try:
            loader =TextLoader(str(text_file))
            docs = loader.load()
            print(f"loaded {len(docs)} documents")
            documents.extend(docs)
        except Exception as e:
            print(f"error in loading documents : {e}")
    
    # csv files

    csv_files = list(data_path.glob("**/*.csv"))

    print(f"\nfound {len(csv_files)} csv files.")

    for csv_file in csv_files:
        try:
            loader=CSVLoader(str(csv_file))
            docs=loader.load()
            print(f"loaded {len(docs)} csv files")
            documents.extend(docs)
        except Exception as e:
            print(f"error in loading csv : {e}")
    return documents

    

            
            

