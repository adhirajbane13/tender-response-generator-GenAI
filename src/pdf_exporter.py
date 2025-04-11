from fpdf import FPDF
import os

def export_response_to_pdf(question: str, answer: str, context_chunks: list[str], filename: str = "response.pdf"):
    pdf = FPDF()
    pdf.add_page()
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "fonts", "arial.ttf"))
    pdf.add_font('Arial', '', font_path, uni=True)
    pdf.set_font("Arial", size=12)

    pdf.multi_cell(0, 10, f"Question:\n{question}\n\n", align='L')
    pdf.multi_cell(0, 10, f"Answer:\n{answer}\n\n", align='L')
    
    pdf.multi_cell(0, 10, f"Context Used:\n", align='L')
    for i, (title, content) in enumerate(context_chunks):
        section_title = f"\n---\nSection {i+1}: {title}\n"
        pdf.multi_cell(0, 10, section_title, align='L')
        pdf.multi_cell(0, 10, content, align='L')

    pdf.output(filename)
    return filename