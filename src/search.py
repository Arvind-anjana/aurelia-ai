import os
import requests
from dotenv import load_dotenv
load_dotenv()
# pyrefly: ignore [missing-import]
from src.vectorstore import FaissVectorStore
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.tools.tavily_search import TavilySearchResults
# pyrefly: ignore [missing-import]
from src.guardrails import InputGuardrail

def check_internet():
    try:
        requests.get("https://1.1.1.1", timeout=1)
        return True
    except (requests.ConnectionError, requests.Timeout):
        return False

class RAGSearch:
    def __init__(self,persist_directory: str= "faiss_store", data_directory: str= "data", embedding_model:str="all-MiniLM-L6-v2"):
        self.memory = MemorySaver()
        self.vectorstore = FaissVectorStore(persist_directory, embedding_model)
        self.persist_dir= persist_directory
        self.data_dir = data_directory
        ## load or build vector store      
                 
        faiss_path =  os.path.join(self.persist_dir, "faiss.index")
        meta_path =  os.path.join(self.persist_dir, "metadata.pkl")

        if not (os.path.exists(faiss_path) and os.path.exists(meta_path)):
            print("vector store not found , building from documents")
            # pyrefly: ignore [missing-import]
            from src.data_loader import load_all_documents
            if os.path.exists(self.data_dir):
                docs= load_all_documents(self.data_dir)
                self.vectorstore.build_from_documents(docs)
            else:
                self.vectorstore.build_from_documents([])
        else:
            print("loading existing vector store")
            self.vectorstore.load()

        api=os.getenv("GROQ_API_KEY")
        llm_model="openai/gpt-oss-20b" # Restored original working model string
        self.llm_online = ChatGroq(groq_api_key=api , model_name= llm_model)
        self.llm_offline = ChatOllama(model="llama3.2") 

        # Initialize Tools
        @tool
        def search_local_documents(query: str) -> str:
            """Use this tool to search the user's local documents for information. ONLY use this when you need to answer questions based on the user's uploaded files."""
            print(f"Agent is searching local documents for: {query}")
            retrieved_results = self.vectorstore.query(query, top_k=5)
            if not retrieved_results:
                return "No documents found in the local knowledge base."
            return "\n\n".join([f"Metadata: {doc['metadata']} \nContent: {doc['metadata'].get('text', '')}"  for  doc in retrieved_results])
            
        self.local_tool = search_local_documents
        
        self.tavily_tool = None
        if os.getenv("TAVILY_API_KEY"):
            self.tavily_tool = TavilySearchResults(max_results=3)

        self.system_prompt = "You are Aurélia, an intelligent and helpful Second Brain assistant. **CRITICAL INSTRUCTION**: You MUST prioritize the user's uploaded local documents over everything else! Always attempt to answer the question using the local document search tool first. "
        if self.tavily_tool:
            self.system_prompt += "Only use the Tavily web search tool if the local documents explicitly lack the necessary information. "
        self.system_prompt += "If the local context provides the answer, DO NOT search the web. If you don't need tools, answer from your general knowledge."

        print(f"groq llm and local ollama initialised with Agent capabilities")

    def search_and_summarize(self,query:str ,top_k:int =5, use_web:bool = True, thread_id:str = "default")-> str:
        is_online = check_internet()
        
        # --- INPUT GUARDRAIL CHECK ---
        guardrail = InputGuardrail(is_online=is_online)
        if not guardrail.check_query(query):
            return "I'm sorry, but I cannot fulfill that request. Please ask a question relevant to your uploaded documents.", is_online
        
        tools = [self.local_tool]
        
        if is_online:
            llm = self.llm_online
            if self.tavily_tool and use_web:
                tools.append(self.tavily_tool)
        else:
            llm = self.llm_offline
            
        print(f"Using {'Online (Groq)' if is_online else 'Offline (Ollama)'} model with tools: {[t.name for t in tools]}")
        
        try:
            # Create agent
            agent = create_react_agent(llm, tools, prompt=self.system_prompt, checkpointer=self.memory)
            config = {"configurable": {"thread_id": thread_id}}
            response = agent.invoke({"messages": [("user", query)]}, config=config)
            return response["messages"][-1].content, is_online
        except Exception as e:
            # Fallback if tool calling fails (common with older local Ollama models)
            print(f"Agent execution failed: {e}. Falling back to standard generation.")
            fallback_prompt = f"Answer this question comprehensively: {query}"
            res = llm.invoke(fallback_prompt)
            return res.content, is_online

if __name__ == "__main__":
    print("Testing Aurelia Agent...")
    rag = RAGSearch()
    print("\n--- Testing Agent Online/Offline ---")
    res, online = rag.search_and_summarize("What is the weather in New York today?")
    print(f"\nResponse (Online={online}):\n{res}")
