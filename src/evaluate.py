import os
import sys
import pandas as pd
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Add the project root to sys.path so it can find the 'src' module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# pyrefly: ignore [missing-import]
from src.search import RAGSearch

def get_evaluator_llm():
    api = os.getenv("GROQ_API_KEY")
    return ChatGroq(groq_api_key=api, model_name="openai/gpt-oss-20b", temperature=0)

def evaluate_faithfulness(question, context, answer, llm):
    """
    Rigorous Faithfulness Check (Ragas-style):
    1. Extract individual factual statements from the generated answer.
    2. Verify each statement independently against the context.
    3. Return a ratio score out of 5.
    """
    if not answer or len(answer) < 5:
        return 0.0

    # Step 1: Extract statements
    extract_prompt = ChatPromptTemplate.from_template(
        "You are an expert fact-extractor. Given the following ANSWER, extract a list of specific, verifiable factual statements.\n"
        "Return each statement on a new line starting with a dash (-).\n\n"
        "ANSWER:\n{answer}\n\n"
        "STATEMENTS:"
    )
    
    statements_str = (extract_prompt | llm).invoke({"answer": answer}).content.strip()
    statements = [s.strip('- ').strip() for s in statements_str.split('\n') if s.strip()]
    
    if not statements:
        return 0.0
        
    # Step 2: Verify statements against context
    verify_prompt = ChatPromptTemplate.from_template(
        "You are an impartial judge. Given the CONTEXT and a STATEMENT, determine if the statement is supported by the context.\n"
        "Answer 'Yes' if it is supported, or 'No' if it contains information not in the context (hallucination).\n\n"
        "CONTEXT:\n{context}\n\n"
        "STATEMENT:\n{statement}\n\n"
        "Respond ONLY with 'Yes' or 'No'."
    )
    
    supported_count = 0
    print(f"      Extracted {len(statements)} factual statements. Verifying...")
    for stmt in statements:
        try:
            result = (verify_prompt | llm).invoke({"context": context, "statement": stmt}).content.strip().lower()
            if 'yes' in result:
                supported_count += 1
        except:
            pass
            
    # Calculate ratio and scale to 5
    ratio = supported_count / len(statements)
    return round(ratio * 5, 2)

def evaluate_relevance(question, answer, llm):
    prompt = ChatPromptTemplate.from_template(
        "You are an impartial judge. Evaluate how relevant the ANSWER is to the QUESTION.\n\n"
        "QUESTION:\n{question}\n\n"
        "ANSWER:\n{answer}\n\n"
        "Respond ONLY with a score from 1 to 5, where 5 is perfectly relevant and 1 is completely irrelevant. Output only the number."
    )
    chain = prompt | llm
    try:
        score_str = chain.invoke({"question": question, "answer": answer}).content.strip()
        return int(''.join(filter(str.isdigit, score_str))[0])
    except:
        return 0

def run_evaluation():
    print("--- Starting Rigorous LLM-as-a-Judge Evaluation ---")
    
    questions = [
        "Which Apollo mission first landed humans on the Moon?",
        "What was the total cost of the Apollo program?",
        "What did the Voyager spacecraft carry into space to represent Earth?",
        "How long were the Mars rovers Spirit and Opportunity originally designed to last?",
        "When did Voyager 1 launch?"
    ]
    
    rag = RAGSearch()
    
    # Automatically ingest the larger test document
    print("\nIngesting test document 'sample_knowledge.txt' into Vector Store...")
    from langchain_community.document_loaders import TextLoader
    try:
        loader = TextLoader("sample_knowledge.txt")
        docs = loader.load()
        rag.vectorstore.build_from_documents(docs)
        print("Successfully ingested test document!\n")
    except Exception as e:
        print(f"Warning: Could not ingest test document: {e}\n")
        
    eval_llm = get_evaluator_llm()
    
    results = []
    
    print("Generating answers and running rigorous evaluation...\n")
    for q in questions:
        print(f"Question: {q}")
        # Generate Answer
        ans, _ = rag.search_and_summarize(q, use_web=False)
        
        # Get Context
        retrieved = rag.vectorstore.query(q, top_k=5)
        context = "\n".join([doc['metadata'].get('text', '') for doc in retrieved])
        
        # Evaluate
        faithfulness_score = evaluate_faithfulness(q, context, ans, eval_llm)
        relevance_score = evaluate_relevance(q, ans, eval_llm)
        
        print(f"   Faithfulness Score: {faithfulness_score}/5.00")
        print(f"   Relevance Score: {relevance_score}/5")
        print("-" * 50)
        
        results.append({
            "question": q,
            "answer": ans,
            "faithfulness_score": faithfulness_score,
            "relevance_score": relevance_score
        })
        
    df = pd.DataFrame(results)
    df.to_csv("rag_evaluation_results.csv", index=False)
    print("\nResults saved to 'rag_evaluation_results.csv'")

if __name__ == "__main__":
    run_evaluation()
