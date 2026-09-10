# 🏛️ Aurélia

Aurélia is an ultra-premium AI intellectual companion and Second Brain. Built with a focus on sophisticated design and powerful local retrieval, Aurélia allows you to chat naturally with your most important documents, research papers, and books.

## ✨ Features

- **Intelligent RAG (Retrieval-Augmented Generation)**: Upload PDFs, TXTs, or CSVs. Aurélia indexes them locally using FAISS and Sentence Transformers, prioritizing your local knowledge base before answering.
- **Hybrid Intelligence**: 
  - **Online Mode**: Powered by the blazing-fast Groq API for near-instant responses.
  - **Offline Mode**: Automatically falls back to a local Ollama instance (LLaMA 3.2) if you lose internet connection.
- **Web Search Integration**: Uses Tavily to seamlessly search the live internet if your local documents don't contain the answer.
- **Dual-Pane Interface**: A beautifully crafted Streamlit UI featuring a conversational chat pane and a built-in Document Viewer (supporting both PDFs and text files).
- **Premium Aesthetics**: A custom CSS design system featuring frosted glassmorphism, warm golden accents, and classic *Playfair Display* typography.

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- (Optional) [Ollama](https://ollama.com/) installed with the `llama3.2` model for offline mode.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Aurelia.git
   cd Aurelia
   ```

2. **Create a virtual environment and install dependencies:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up Environment Variables:**
   Create a `.env` file in the root directory and add your API keys:
   ```env
   GROQ_API_KEY=your_groq_key_here
   TAVILY_API_KEY=your_tavily_key_here
   ```

### Running the App
```bash
streamlit run ui.py
```

## 🧠 Managing the Knowledge Base
To give Aurélia permanent knowledge before deploying:
1. Place your PDFs or TXT files directly into the `data/` folder.
2. Delete the `faiss_store/` folder (if it exists).
3. Run the app locally. Aurélia will automatically ingest the documents and build a local vector database.
4. Commit the new `faiss_store/` and `data/` folders to GitHub and deploy!
