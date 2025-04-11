import streamlit as st
import os
import tempfile
import pdfplumber
from openai import OpenAI
from dotenv import load_dotenv
from visual_chunker import visual_chunk_pdf, show_font_debug_view
from vector_store import build_faiss_index, search_faiss_index
from prompts import build_rag_prompt
from pdf_exporter import export_response_to_pdf
import hashlib




try:
    load_dotenv()
    def get_file_hash(file_path):
        with open(file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    st.set_page_config(page_title="Tender Intelligence", layout="wide")
    
    # 📱 Mobile-friendly CSS
    st.markdown("""
        <style>
        /* Global scaling for mobile */
        @media (max-width: 768px) {
            .block-container {
                padding: 1rem !important;
            }
            .css-18e3th9, .css-1d391kg {
                padding: 0rem !important;
            }
            h1, h2, h3, h4 {
                font-size: 1.25rem !important;
            }
            .stButton>button {
                width: 100%;
            }
            .stTextInput>div>div>input {
                font-size: 1rem;
            }
        }
        </style>
    """, unsafe_allow_html=True)

    # ---------------- Sidebar ----------------
    with st.sidebar:
        st.title("🧭 Navigation & Info")

        st.markdown("### ℹ️ About this App")
        st.markdown(
            "This tool helps you extract, understand, and interact with tender documents. "
            "Upload one or more PDF tenders, and ask questions about their contents. "
            "Powered by GPT-4 and FAISS, it delivers smart answers and lets you export results as PDFs."
        )

        st.markdown("#### ⚙️ Model Settings")
        temperature = st.slider("🎛️ Response Creativity", 0.0, 2.0, 0.2, 0.2)

        st.markdown("#### 📝 Instructions")
        st.markdown(
            "- Upload a tender PDF\n"
            "- Ask your question\n"
            "- View relevant answers\n"
            "- Optionally export as PDF"
        )

        st.markdown("#### 🔗 Connect with Me")
        st.markdown(
            """
            <a href="https://github.com/adhirajbane13" target="_blank" style="text-decoration: none;">
                <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg" alt="GitHub" height="20"/> GitHub
            </a><br>
            <a href="https://www.linkedin.com/in/adhiraj-banerjee" target="_blank" style="text-decoration: none;">
                <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/linkedin/linkedin-original.svg" alt="LinkedIn" height="20"/> LinkedIn
            </a>
            """,
            unsafe_allow_html=True
        )

        st.markdown("#### 📬 Feedback")
        st.markdown("For feedback, reach out via LinkedIn.")

        st.markdown("---")
        st.caption("Built using Streamlit and GPT-4.\nEmpowering document intelligence with GenAI.")
        st.caption("© 2025 Adhiraj Banerjee. All rights reserved.")

    # Polished Hero Section
    st.markdown("""
        <style>
        .hero {
            background-color: #EEF2F7;
            padding: 2rem 2rem 1rem 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            border-left: 6px solid #4A90E2;
        }
        .hero h1 {
            font-size: 2.5rem;
            color: #1f3c88;
            font-family: 'Segoe UI', sans-serif;
            margin-bottom: 0.5rem;
        }
        .hero p {
            font-size: 1.1rem;
            color: #333;
            font-family: 'Segoe UI', sans-serif;
        }
        </style>

        <div class="hero">
            <h1>📄 Tender Intelligence Assistant</h1>
            <p>Ask smart questions about your uploaded tender PDFs — and get instant, structured answers with context.</p>
        </div>
    """, unsafe_allow_html=True)


    # File Upload
    st.markdown("""
    <style>
    .upload-box {
        background-color: #ffffff;
        border: 2px dashed #4A90E2;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        font-family: 'Segoe UI', sans-serif;
        margin-bottom: 2rem;
    }
    </style>
    <div class="upload-box">
        <h4>📤 Upload a Tender Document (PDF)</h4>
        <p style='color: #555;'>We will parse it and let you ask intelligent questions based on its content.</p>
    </div>
""", unsafe_allow_html=True)

    uploaded_files = st.file_uploader("Upload one or more tenders", type=["pdf"], accept_multiple_files=True)
    if not uploaded_files:
        st.warning("📂 Please upload at least one tender to begin.")
        st.stop()

    # Create dropdown to select which file to process
    file_names = [f.name for f in uploaded_files]
    selected_name = st.selectbox("Choose a tender to explore", file_names)

    # Get the actual file object by matching name
    selected_file = next((f for f in uploaded_files if f.name == selected_name), None)

    # Safety check
    if selected_file is None:
        st.error("❌ Could not load the selected file.")
        st.stop()

    # Auto-load demo tender if no file uploaded
    if not selected_file:
        demo_path = os.path.join("..","data", "rfps", "rfp-managed-it-servicedocx.pdf")
        if os.path.exists(demo_path):
            with open(demo_path, "rb") as f:
                uploaded_file = f
                st.info("⚙️ No tender uploaded. Using demo tender for demo purposes.")

    if selected_file:
        # Save uploaded file temporarily
        st.markdown(f"📁 **Selected File:** `{selected_file.name}`")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(selected_file.read())
            rfp_path = tmp_file.name

        # Extract text
        with pdfplumber.open(rfp_path) as pdf:
            extracted_text = "\n".join([page.extract_text() or "" for page in pdf.pages])

        # Font size debug view
        # if st.checkbox("🪵 Show Font Size Debug View"):
        #     show_font_debug_view(rfp_path)



        file_hash = get_file_hash(rfp_path)

        @st.cache_data(show_spinner="📑 Chunking tender document...")
        def cached_chunker(file_hash, pdf_path):
            return visual_chunk_pdf(pdf_path)

        @st.cache_resource(show_spinner="📦 Building semantic index...")
        def cached_index(chunks):
            return build_faiss_index(chunks)


        if "file_cache" not in st.session_state:
            st.session_state.file_cache = {}

        if file_hash not in st.session_state.file_cache:
            with st.spinner("🔍 Processing tender..."):
                chunks = cached_chunker(file_hash,rfp_path)
                index, vectors = cached_index(chunks)
                st.session_state.file_cache[file_hash] = {
                    "chunks": chunks,
                    "index": index,
                    "vectors": vectors,
                    "name": selected_name
                }
        else:
            chunks = st.session_state.file_cache[file_hash]["chunks"]
            index = st.session_state.file_cache[file_hash]["index"]
            # vectors = st.session_state.file_cache[file_hash]["vectors"]
            # selected_name = st.session_state.file_cache[file_hash]["name"]
        
        # Chunking
        st.markdown("### 📑 Parsed Sections of the Tender", unsafe_allow_html=True)
        st.markdown("<hr style='border: 1px solid #CCC;'>", unsafe_allow_html=True)

        for i, (title, content) in enumerate(chunks):
            preview = title if title else content[:40]
            with st.expander(f"📄 {preview} (Section {i+1})"):
                st.markdown(f"<div style='background-color:#f9f9f9;padding:10px;border-radius:8px;'>{content}</div>", unsafe_allow_html=True)


        # Build vector index
        st.subheader("🧠 Semantic Index")
        st.markdown("We are building a semantic index of the document using OpenAI embeddings and FAISS.")

        #index, vectors = cached_index(chunks)
        st.success(f"Indexed {len(chunks)} chunks.")


        # Ask a question
        st.subheader("🔎 Ask a Question About the RFP")
        suggested_questions = [
        "What is the tender about?",
        "What is the estimated contract value?",
        "What are the contract dates?",
        "Who is the contracting authority?",
        "What are the eligibility requirements?"
        ]
        selected_q = st.selectbox("💡 Choose a suggested question:", suggested_questions)
        custom_q = st.text_input("Or ask your own:")

        user_query = custom_q if custom_q else selected_q


        if user_query:
            with st.spinner("🔎 Searching the semantic index..."):
                top_chunks = search_faiss_index(user_query, index, chunks)

            # LLM prompt
            prompt = build_rag_prompt(top_chunks, user_query)

            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature= temperature,
                )
                final_answer = response.choices[0].message.content

            # Display answer
            st.markdown("### 🧠 Assistant Response")

            st.markdown(f"""
                <div style='
                    background-color: #f0f8ff;
                    border-left: 6px solid #4A90E2;
                    padding: 1rem;
                    border-radius: 8px;
                    margin-bottom: 1rem;
                    font-size: 1rem;
                    line-height: 1.6;
                '>
            {final_answer}</div>
            """, unsafe_allow_html=True)
            # st.markdown(final_answer, unsafe_allow_html=True)
            # st.markdown("</div>", unsafe_allow_html=True)


            # st.code(final_answer, language="markdown")
            # st.markdown("<small><em>Tip: Right click or tap and hold to copy the text above.</em></small>", unsafe_allow_html=True)

            highlight_term = user_query.lower().strip()
            st.markdown("### 🔍 Most Relevant Sections (Used for Answer)")
            for i, (title, content) in enumerate(top_chunks):
                clean_title = title.strip() if title else f"Chunk {i+1}"
                with st.expander(f"📄 {clean_title}"):
                    highlighted = content
                    if highlight_term in content.lower():
                        highlighted = content.replace(
                            highlight_term,
                            f"<mark style='background-color: #ffeaa7'>{highlight_term}</mark>"
                        )
                    st.markdown(f"""
                        <div style='
                            background-color: #f9f9f9;
                            padding: 0.75rem;
                            border-radius: 6px;
                            font-size: 0.95rem;
                            line-height: 1.5;
                        '>{highlighted.strip()}</div>
                    """, unsafe_allow_html=True)




            # Export
            st.markdown("### 📝 Export")
            if st.button("📤 Download Answer as PDF"):
                filename = export_response_to_pdf(user_query, final_answer, top_chunks)
                with open(filename, "rb") as f:
                    st.download_button(
                        label="Download PDF",
                        data=f,
                        file_name=filename,
                        mime="application/pdf"
                    )

except Exception as e:
    st.error(f"An error occurred: {e}")