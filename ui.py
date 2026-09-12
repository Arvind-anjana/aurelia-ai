import streamlit as st
import os
from pathlib import Path
import base64

# Set project root to the Aurelia directory itself
project_root = Path(__file__).parent

# pyrefly: ignore [missing-import]
from src.search import RAGSearch
# pyrefly: ignore [missing-import]
from src.search import check_internet
# pyrefly: ignore [missing-import]
from src.data_loader import load_all_documents

# ---------------------------------------------
# AESTHETICS: Ivory Minimalist Theme (Custom CSS)
# ---------------------------------------------
def inject_custom_css():
    bg_path = project_root / "assets" / "starry_night_bg.jpg"
    bg_css = ""
    if bg_path.exists():
        with open(bg_path, "rb") as f:
            b64_bg = base64.b64encode(f.read()).decode('utf-8')
        bg_css = f"""
            background-image: 
                linear-gradient(to bottom, rgba(248, 245, 240, 0.2) 0%, rgba(248, 245, 240, 0.75) 100%),
                url("data:image/jpeg;base64,{b64_bg}") !important;
            background-size: cover !important;
            background-attachment: fixed !important;
            background-position: center !important;
        """
    else:
        bg_css = """
            background-image: 
                radial-gradient(circle at 0% 0%, #FFFFFF 0%, transparent 40%),
                radial-gradient(circle at 100% 0%, #FDFBF7 0%, transparent 40%),
                radial-gradient(circle at 100% 100%, rgba(212, 175, 55, 0.08) 0%, transparent 50%),
                radial-gradient(circle at 0% 100%, #F4EFE6 0%, transparent 40%);
        """

    st.markdown("""
        <style>
        /* Base Colors & Backgrounds */
        .stApp {
            background-color: #F8F5F0;
""" + bg_css + """
            color: #333333;
            font-family: 'Inter', sans-serif;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #D4AF37; /* Solid Elegant Golden Color */
            border-right: 1px solid #B8962E;
            border-top-right-radius: 28px;
            border-bottom-right-radius: 28px;
        }
        
        /* Navbar / Header styling */
        [data-testid="stHeader"] {
            background-color: rgba(255, 255, 255, 0.4) !important;
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        /* Sidebar Titles and Text need to be dark for contrast */
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] label {
            color: #111111 !important;
        }
        
        /* Headers / Serif Typography */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Playfair Display', serif !important;
            color: #FFFFFF !important;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }
        
        /* Sticky Titles for Main Columns */
        .sticky-title {
            position: sticky;
            top: 2rem;
            z-index: 999;
            color: #FFFFFF !important;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
            padding: 15px 20px;
            background-color: rgba(15, 20, 35, 0.5);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }

        /* Status Indicator (Subtle) */
        .status-badge-online {
            background-color: #E8F5E9;
            color: #2E7D32;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.8rem;
            border: 1px solid #A5D6A7;
            display: inline-block;
            margin-bottom: 20px;
        }
        
        .status-badge-offline {
            background-color: #FFF3E0;
            color: #E65100;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.8rem;
            border: 1px solid #FFCC80;
            display: inline-block;
            margin-bottom: 20px;
        }

        /* Chat Bubbles (Glassmorphism & Premium feel) */
        [data-testid="stChatMessage"] {
            background-color: rgba(255, 255, 255, 0.6);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(212, 175, 55, 0.15); /* Faint gold border */
            border-radius: 20px;
            padding: 15px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.02), 0 4px 8px rgba(212, 175, 55, 0.04);
            margin-bottom: 20px;
            color: #000000 !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        [data-testid="stChatMessage"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 28px rgba(0,0,0,0.03), 0 6px 12px rgba(212, 175, 55, 0.08);
        }
        
        /* User and Assistant text elements specifically */
        [data-testid="stChatMessage"] * {
            color: #000000 !important;
        }

        /* Chat Input (Search Bar) Styling */
        [data-testid="stChatInput"] {
            background-color: #222222 !important; /* Dark background so white text is visible */
            border-radius: 12px;
        }
        [data-testid="stChatInput"] textarea {
            color: #FFFFFF !important; /* White text */
        }
        [data-testid="stChatInput"] textarea::placeholder {
            color: #BBBBBB !important;
        }
        
        /* Hide the top right action menu/deploy button but KEEP the sidebar toggle */
        [data-testid="stHeaderActionElements"] {
            display: none;
        }

        /* Make standard Streamlit widgets beautifully curved */
        .stButton > button {
            border-radius: 24px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 10px rgba(212, 175, 55, 0.1) !important;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(212, 175, 55, 0.2) !important;
            border-color: #D4AF37 !important;
            color: #D4AF37 !important;
        }

        /* Chat Input (Search Bar) Styling */
        [data-testid="stChatInput"] {
            background-color: #222222 !important; /* Dark background */
            border-radius: 12px !important;
            box-shadow: 0 8px 20px rgba(0,0,0,0.1) !important;
            border: 1px solid rgba(212, 175, 55, 0.4) !important;
        }
        [data-testid="stChatInput"] textarea {
            color: #FFFFFF !important; /* White text */
        }
        [data-testid="stChatInput"] textarea::placeholder {
            color: #BBBBBB !important;
        }
        
        /* File Uploader and Selectbox curves */
        [data-testid="stFileUploader"] > section, [data-testid="stSelectbox"] > div > div {
            border-radius: 16px !important;
        }

        /* Round all images (for the banner) */
        [data-testid="stImage"] img {
            border-radius: 16px !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
        }

        /* --- Split-Pane Independent Scrolling Layout --- */
        
        /* Stop the main page from scrolling unnecessarily */
        [data-testid="stMain"] {
            overflow: hidden !important;
        }

        /* Chat Column (Left) */
        [data-testid="stColumn"]:nth-of-type(1) {
            height: calc(100vh - 8rem) !important;
            overflow-y: auto !important;
            padding-right: 20px;
        }

        /* PDF Viewer Column (Right) */
        [data-testid="stColumn"]:nth-of-type(2) {
            height: calc(100vh - 8rem) !important;
            overflow-y: hidden !important;
            padding: 20px;
            background-color: rgba(15, 20, 35, 0.4);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 24px;
            border: 1px solid rgba(212, 175, 55, 0.2);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------
# CORE LOGIC
# ---------------------------------------------

@st.cache_resource(show_spinner=False)
def get_rag_engine():
    # Cache busted to ensure new methods (like clear) are available
    return RAGSearch(persist_directory=str(project_root / "faiss_store"))

def main():
    st.set_page_config(page_title="Aurélia", page_icon="🏛️", layout="wide")
    inject_custom_css()
    
    # Initialize session state for chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    rag = get_rag_engine()
    
    # Check internet for visual indicator
    is_online = check_internet()

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 12px; padding: 0px 0 20px 0; margin-top: -40px;">
                <svg width="55" height="55" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                    <!-- Center solid leaf -->
                    <path d="M50 20 C 70 40, 65 70, 50 85 C 35 70, 30 40, 50 20 Z" fill="#111111"/>
                    <!-- Left outlined leaf -->
                    <path d="M48 80 C 15 70, 10 40, 25 30 C 35 40, 40 60, 48 80 Z" fill="none" stroke="#111111" stroke-width="6"/>
                    <!-- Right outlined leaf -->
                    <path d="M52 80 C 85 70, 90 40, 75 30 C 65 40, 60 60, 52 80 Z" fill="none" stroke="#111111" stroke-width="6"/>
                    <!-- Bottom stem -->
                    <line x1="50" y1="85" x2="50" y2="95" stroke="#111111" stroke-width="5" stroke-linecap="round"/>
                </svg>
                <h1 style="margin: 0; font-family: 'Playfair Display', serif; font-weight: 500; font-size: 1.9rem; color: #111111 !important; letter-spacing: 2px;">AURÉLIA</h1>
            </div>
        """, unsafe_allow_html=True)
        
        if is_online:
            st.markdown("<div class='status-badge-online'>🟢 Online (Groq)</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='status-badge-offline'>🔴 Offline (Local Ollama)</div>", unsafe_allow_html=True)
            
        st.markdown("### Settings")
        use_web = st.toggle("Enable Tavily Web Search", value=True)
        show_pdf = st.toggle("Show PDF Viewer", value=True)
        
        pdf_width = 50
        if show_pdf:
            pdf_width = st.slider("PDF Window Size (%)", min_value=20, max_value=80, value=50, step=5)
            
        st.markdown("---")
            
        st.markdown("### Knowledge Base")
        
        uploaded_files = st.file_uploader("Upload Documents (PDF, TXT, CSV)", accept_multiple_files=True)
        if st.button("Add to Knowledge Base"):
            if uploaded_files:
                with st.spinner("Processing documents..."):
                    # Save uploaded files to the 'data' directory
                    data_dir = project_root / "data"
                    os.makedirs(data_dir, exist_ok=True)
                    
                    new_docs = []
                    for uploaded_file in uploaded_files:
                        file_path = data_dir / uploaded_file.name
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                            
                        # Load only the newly uploaded file to avoid duplicating the entire knowledge base
                        try:
                            ext = file_path.suffix.lower()
                            if ext == '.pdf':
                                from langchain_community.document_loaders import PyMuPDFLoader
                                new_docs.extend(PyMuPDFLoader(str(file_path)).load())
                            elif ext == '.txt':
                                from langchain_community.document_loaders import TextLoader
                                new_docs.extend(TextLoader(str(file_path)).load())
                            elif ext == '.csv':
                                from langchain_community.document_loaders import CSVLoader
                                new_docs.extend(CSVLoader(str(file_path)).load())
                        except Exception as e:
                            st.error(f"Error reading {uploaded_file.name}: {e}")
                    
                    # Add ONLY the newly uploaded documents to the vector store
                    if new_docs:
                        rag.vectorstore.build_from_documents(new_docs)
                        st.success("Knowledge Base Updated without duplicating old files!")
                    else:
                        st.warning("No readable text found in uploads.")
            else:
                st.warning("Please upload a file first.")

        st.markdown("---")
        if st.button("Clear Knowledge Base"):
            with st.spinner("Clearing knowledge base..."):
                rag.vectorstore.clear()
                
                # Delete physical files in data directory
                data_dir = project_root / "data"
                if data_dir.exists():
                    import shutil
                    shutil.rmtree(data_dir)
                    os.makedirs(data_dir, exist_ok=True)
                    
                st.success("Knowledge Base cleared successfully! All uploaded files deleted.")

    # --- MAIN INTERFACE ---
    if show_pdf:
        chat_col, doc_col = st.columns([100 - pdf_width, pdf_width])
    else:
        chat_col = st.container()

    # --- CHAT COLUMN (LEFT) ---
    with chat_col:
        st.markdown("<h1 class='sticky-title'>Chat with Aurélia</h1>", unsafe_allow_html=True)

        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask Aurélia a question..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate assistant response
            with st.chat_message("assistant"):
                with st.spinner("Searching and thinking..."):
                    try:
                        response, was_online = rag.search_and_summarize(prompt, use_web=use_web)
                        st.markdown(response)
                        
                        # Optional: append context about offline mode if it switched during query
                        if not was_online and is_online:
                             st.caption("*(Generated locally via Ollama due to network drop)*")
                             
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        st.error(f"Error generating response: {e}")
                        # If ollama fails because it's not installed, we can catch that.
                        if "Connection error" in str(e) and not is_online:
                            st.error("Make sure Ollama is running and the llama3.2 model is installed (run `ollama run llama3.2` in terminal).")

    # --- DOCUMENT VIEWER COLUMN (RIGHT) ---
    if show_pdf:
        with doc_col:
            st.markdown("<h1 class='sticky-title'>Document Viewer</h1>", unsafe_allow_html=True)
            
            data_dir = project_root / "data"
            if data_dir.exists():
                # Get list of pdfs and txts
                doc_files = [f.name for f in data_dir.iterdir() if f.suffix.lower() in ['.pdf', '.txt']]
                
                if doc_files:
                    selected_doc = st.selectbox("Select a Document to view", doc_files)
                    doc_path = data_dir / selected_doc
                    
                    if doc_path.suffix.lower() == '.pdf':
                        # Render PDF using streamlit-pdf-viewer to avoid browser blocking
                        # pyrefly: ignore [missing-import]
                        from streamlit_pdf_viewer import pdf_viewer
                        with open(doc_path, "rb") as f:
                            pdf_bytes = f.read()
                        pdf_viewer(pdf_bytes, height=700)
                        
                    elif doc_path.suffix.lower() == '.txt':
                        # Render Text file in a styled scrollable div
                        with open(doc_path, "r", encoding="utf-8", errors="ignore") as f:
                            text_content = f.read()
                        
                        import html
                        escaped_text = html.escape(text_content)
                        display_html = f'<div style="width: 100%; height: 700px; overflow-y: auto; padding: 25px; background-color: #FAFAFA; border: 1px solid rgba(212,175,55,0.2); border-radius: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); font-family: \'Plus Jakarta Sans\', sans-serif; font-size: 14px; line-height: 1.6; white-space: pre-wrap; color: #333333;">{escaped_text}</div>'
                        st.markdown(display_html, unsafe_allow_html=True)
                else:
                    st.info("Upload a PDF or TXT document to view it here.")
            else:
                st.info("Upload a PDF or TXT document to view it here.")

if __name__ == "__main__":
    main()
