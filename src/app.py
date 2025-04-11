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

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Tender Intelligence", layout="wide")
st.title("📄 Tender Intelligence Assistant")

# File Upload
uploaded_file = st.file_uploader("Upload a tender PDF", type=["pdf"])

# Auto-load demo tender if no file uploaded
if not uploaded_file:
    demo_path = os.path.join("data", "rfps", "rfp-managed-it-servicedocx.pdf")
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
    st.markdown("## 📑 Parsed Tender Sections")
    st.markdown("---")

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
        st.markdown("### 🧠 Answer")
        #st.write(final_answer)

        st.code(final_answer, language="markdown")
        st.markdown("<small><em>Tip: Right click or tap and hold to copy the text above.</em></small>", unsafe_allow_html=True)

        st.markdown("### 🔍 Most Relevant Sections (Used for Answer)")
        for i, (title, content) in enumerate(top_chunks):
            clean_title = title.strip() if title else f"Chunk {i+1}"
            with st.expander(f"📄 {clean_title}"):
                # Highlight matching phrase if present
                highlight_term = user_query.lower().strip()
                highlighted = content
                if highlight_term in content.lower():
                    highlighted = content.replace(
                        highlight_term,
                        f"<mark>{highlight_term}</mark>"
                    )
                st.markdown(f"<div style='background-color:#f9f9f9;padding:10px;border-radius:8px;'>{content}</div>", unsafe_allow_html=True)



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