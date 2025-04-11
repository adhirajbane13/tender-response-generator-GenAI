# Tender Intelligence Assistant

**Instantly understand complex tender/RFP PDFs with AI-powered question answering and semantic document insights.**

This tool allows businesses, procurement teams, and consultants to upload tender documents (PDFs), ask natural language questions, and get structured, intelligent answers instantly — with supporting context extracted from the document itself.

---

## Live Demo

**Try it out on Streamlit Cloud** 
[Tender Intelligence Assistant (Streamlit App)](https://adhirajbane-rfp-response-generator-genai.streamlit.app/)

**Watch the Demo Video**  
[YouTube - AI-Powered Tender Intelligence Assistant](https://www.youtube.com/watch?v=7oWn1RbKPYs)

---

## Real-world Business Problem Solved

Responding to tenders is time-consuming and requires navigating long, jargon-filled PDFs to find key information. This tool solves that by:

- Letting you **ask smart questions** like “Who is the contracting authority?” or “What is this tender about?”
- Automatically showing **supporting evidence** from relevant sections of the tender
- Helping **teams collaborate faster**, make informed decisions, and prepare better responses

---

### Key Features

- Upload and toggle between **multiple tender PDFs**
- **Natural language Q&A** powered by GPT-4
- Context highlighting to show **where the answer came from**
- Uses **OpenAI embeddings + FAISS** for fast and accurate semantic search
- Export answers as a PDF
- Mobile-friendly layout with responsive styling
- Smart caching to avoid reprocessing already-uploaded tenders
- **Adjustable Answer Style (Temperature Control)**  
  Control how *precise* or *creative* the assistant should be:
  - **Lower temperature (e.g., 0.2):** Confident, factual, and grounded answers like “The document does not contain this information.”
  - **Higher temperature (e.g., 0.7+):** More human-like intuition — deeper guesses or inferred insights even if details are scattered.  
    > *Example: “The document does not contain specific dates for the contract to start and end. However, the initial contract is stated to last for 36 months, with the option to extend it an additional 24 months upon mutual agreement…”*

---

Absolutely — let’s expand each of these to give a clearer, more business-friendly picture of how they power your Tender Intelligence Assistant, while still keeping it engaging and digestible for a wider audience:

---

### Technology Behind the Scenes

#### **OpenAI Embeddings (text-embedding-3-large)**
This model plays a crucial role in "understanding" the tender document. It breaks the document into smaller sections (or chunks) and transforms each chunk into a **semantic vector** — a mathematical representation of the *meaning* behind the text.  
Unlike traditional keyword search, this allows the assistant to grasp **concepts**, **topics**, and **context**, even when the user’s question is worded differently from the original tender phrasing.

*For example, even if a document mentions “termination clauses” and the user asks “what happens if the contract ends early?”, embeddings help the system recognize this is the same idea or rather technically similar.*

---

#### **FAISS (Facebook AI Similarity Search)**
Once the document is semantically embedded, FAISS comes into action as the **search engine**. It performs fast, intelligent retrieval of the **most relevant chunks** for any given question — not by matching exact words, but by calculating how "close" the meanings are.

This enables:
- **Lightning-fast answers**, even across long documents
- **Pinpoint accuracy**, surfacing only the parts of the tender that actually matter
- A smarter system that feels more like asking a human expert than reading a PDF

---

#### **Bringing it Together: Retrieval-Augmented Generation (RAG)**
With embeddings powering understanding and FAISS powering relevance, the assistant uses a **RAG pipeline** to generate responses. It:
1. Retrieves the best-matching chunks of the tender
2. Sends them to **GPT-4**, which crafts a natural, helpful answer based *only* on that context

And for even more flexibility, users can tune the **temperature slider** to adjust:
- *Low temperature (0.2)* -> “Just the facts, please”
- *High temperature (0.7+)* -> “Think like a human analyst — even if the answer isn't obvious”

---

## Project Structure

```bash
tender-response-generator-GenAI/
│
├── src/
│   ├── app.py                # Main Streamlit app
│   ├── visual_chunker.py     # Font-size/bold-based PDF chunking (with fallback)
│   ├── vector_store.py       # FAISS index builder and search logic
│   ├── pdf_exporter.py       # Export Q&A + context into styled PDF
│   ├── prompts.py            # RAG prompt builder
│   └── document_parser.py    # (Optional) general parsing logic
│
├── data/
│   ├── rfps/                 # Example/demo tender PDFs
│   └── past_responses/       # [Optional] for indexed proposals
│
├── fonts/                    # Contains Unicode-safe fonts (e.g., DejaVuSans.ttf)
├── exports/                  # Auto-generated answer PDFs
├── requirements.txt          # Project dependencies
└── README.md                 # Project overview
```

---

## Setup & Usage

### Installation

```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_key_here
```

### Run the App

```bash
streamlit run src/app.py
```

---

## Dependencies

Main packages used:

- `streamlit`
- `openai`
- `pdfplumber`
- `pdfminer.six`
- `fpdf`
- `faiss-cpu`
- `unstructured[pdf]`
- `python-dotenv`

---

## Challenges Solved

Handling diverse PDF layouts with varying header structures  
Extracting logical sections using font-size + bold detection fallback  
Preventing slowdowns with **smart caching** for repeat uploads  
Supporting **multiple tender file uploads** with toggling  
Exporting AI responses to a **clean, downloadable PDF**  
Making the app **mobile-friendly** and **easy to demo**

---

## Author

Built by **Adhiraj Banerjee**  
[LinkedIn](https://www.linkedin.com/in/adhiraj-banerjee) • [GitHub](https://github.com/adhirajbane13)

© 2025 Adhiraj Banerjee. All rights reserved.
