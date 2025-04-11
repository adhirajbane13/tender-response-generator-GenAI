from fpdf import FPDF

def export_response_to_pdf(question: str, answer: str, context_chunks: list[str], filename: str = "response.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.multi_cell(0, 10, f"Question:\n{question}\n\n", align='L')
    pdf.multi_cell(0, 10, f"Answer:\n{answer}\n\n", align='L')
    
    pdf.multi_cell(0, 10, f"Context Used:\n", align='L')
    for i, chunk in enumerate(context_chunks[:3]):
        pdf.multi_cell(0, 10, f"[Chunk {i+1}]\n{chunk}\n\n", align='L')

    pdf.output(filename)
    return filename
