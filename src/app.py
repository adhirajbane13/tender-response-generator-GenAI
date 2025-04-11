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

try:
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    st.set_page_config(page_title="Tender Intelligence", layout="wide")
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

    uploaded_file = st.file_uploader("", type=["pdf"])


    # Auto-load demo tender if no file uploaded
    if not uploaded_file:
        demo_path = os.path.join("..","data", "rfps", "rfp-managed-it-servicedocx.pdf")
        if os.path.exists(demo_path):
            with open(demo_path, "rb") as f:
                uploaded_file = f
                st.info("⚙️ No tender uploaded. Using demo tender for demo purposes.")

    if uploaded_file:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            rfp_path = tmp_file.name

        # Extract text
        with pdfplumber.open(rfp_path) as pdf:
            extracted_text = "\n".join([page.extract_text() or "" for page in pdf.pages])

        # Font size debug view
        # if st.checkbox("🪵 Show Font Size Debug View"):
        #     show_font_debug_view(rfp_path)

        # Chunking
        st.markdown("### 📑 Parsed Sections of the Tender", unsafe_allow_html=True)
        st.markdown("<hr style='border: 1px solid #CCC;'>", unsafe_allow_html=True)

        chunks = visual_chunk_pdf(rfp_path)
        for i, (title, content) in enumerate(chunks):
            preview = title if title else content[:40]
            with st.expander(f"📄 {preview} (Section {i+1})"):
                st.markdown(f"<div style='background-color:#f9f9f9;padding:10px;border-radius:8px;'>{content}</div>", unsafe_allow_html=True)


        # Build vector index
        st.subheader("🧠 Semantic Index")
        index, vectors = build_faiss_index(chunks)
        st.success(f"Indexed {len(chunks)} chunks.")

        # Ask a question
        st.subheader("🔎 Ask a Question About the RFP")
        user_query = st.text_input("Type your question:")
        st.markdown("**💡 Try asking:**")
        st.markdown("- What is the tender about?")
        st.markdown("- What is the estimated contract value?")
        st.markdown("- What are the contract dates?")
        st.markdown("- Who is the contracting authority?")
        st.markdown("- What are the eligibility requirements?")


        if user_query:
            top_chunks = search_faiss_index(user_query, index, chunks)

            # LLM prompt
            prompt = build_rag_prompt(top_chunks, user_query)

            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
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
    st.markdown("---")
    st.markdown(
        "Built by **Adhiraj Banerjee**  \n"
        "[GitHub](https://github.com/adhirajbane13) • [LinkedIn](https://www.linkedin.com/in/adhiraj-banerjee) \n"
        "\nEmpowering document intelligence with GenAI."
    )

except Exception as e:
    st.error(f"An error occurred: {e}")