from typing import List, Tuple
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar
from unstructured.partition.pdf import partition_pdf
import streamlit as st
import re

# ------------------------------------------
# 1. Extract layout-aware blocks using pdfminer
# ------------------------------------------
def extract_layout_blocks(pdf_path: str) -> Tuple[List[Tuple[float, float, str]], bool]:
    blocks = []
    bold_detected = False
    for page_layout in extract_pages(pdf_path):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                text = element.get_text().strip()
                if not text:
                    continue
                font_sizes = []
                bold_flags = []
                for line in element:
                    for char in line:
                        if isinstance(char, LTChar):
                            font_sizes.append(char.size)
                            is_bold = "bold" in char.fontname.lower()
                            bold_flags.append(is_bold)
                            if is_bold:
                                bold_detected = True
                avg_size = (int(sum(font_sizes) / len(font_sizes)) + 1) if font_sizes else 0
                bold_ratio = sum(bold_flags) / len(bold_flags) if bold_flags else 0
                blocks.append((avg_size, bold_ratio, text))
    return blocks, bold_detected


# ------------------------------------------
# 2. Classify blocks into (title, content) pairs using font size and boldness
# ------------------------------------------
def classify_blocks(blocks: List[Tuple[float, float, str]], bold_supported: bool) -> List[Tuple[str, str]]:
    font_sizes = [size for size, _, _ in blocks]
    threshold = sorted(font_sizes)[int(0.85 * len(font_sizes))] if font_sizes else 12

    chunks = []
    current_title = "Untitled Section"
    current_content = ""
    content_started = False

    def is_subheading(text):
        return bool(re.match(r"^([A-Za-z0-9]+[.)]|\d+\.\d+)", text.strip()))

    for size, bold_ratio, text in blocks:
        if bold_supported:
            is_likely_header = (
                (size >= threshold and bold_ratio >= 0.8 and len(text.split()) < 10)
            )
        else:
            is_likely_header = (size >= threshold and len(text.split()) < 15)

        if is_likely_header:
            if content_started:
                chunks.append((current_title, current_content.strip()))
                current_title = text.strip()
                current_content = ""
                content_started = False
            else:
                if current_title == "Untitled Section":
                    current_title = text.strip()
                elif is_subheading(text):
                    current_title = f"{current_title} -> {text.strip()}"
                else:
                    chunks.append((current_title, "[No content detected after this header.]"))
                    current_title = text.strip()
                    current_content = ""
        else:
            current_content += text + "\n"
            content_started = True

    if current_title:
        content_to_save = current_content.strip()
        if len(content_to_save) < 10:
            content_to_save = "[No content detected after this header.]"
        chunks.append((current_title, content_to_save))

    return chunks


# ------------------------------------------
# 3. Fallback using unstructured
# ------------------------------------------
def unstructured_fallback(pdf_path: str) -> List[Tuple[str, str]]:
    elements = partition_pdf(filename=pdf_path)
    chunks = []
    current_title = "Untitled Section"
    current_content = ""

    for el in elements:
        if el.category == "Title":
            if current_content.strip():
                chunks.append((current_title, current_content.strip()))
            current_title = el.text.strip()
            current_content = ""
        else:
            current_content += el.text + "\n"

    if current_content.strip():
        chunks.append((current_title, current_content.strip()))

    return chunks


# ------------------------------------------
# 4. Combined chunker (best of both worlds)
# ------------------------------------------
def visual_chunk_pdf(pdf_path: str) -> List[Tuple[str, str]]:
    try:
        blocks, bold_supported = extract_layout_blocks(pdf_path)
        if len(blocks) < 5:
            raise ValueError("Too few layout blocks detected.")
        return classify_blocks(blocks, bold_supported)
    except Exception as e:
        print(f"[Fallback] Using unstructured: {e}")
        return unstructured_fallback(pdf_path)


# ------------------------------------------
# 5. Optional Streamlit Debug View
# ------------------------------------------
def show_font_debug_view(pdf_path: str):
    st.markdown("### 🐛 Font Size + Boldness Debug View")
    blocks, _ = extract_layout_blocks(pdf_path)
    for i, (size, bold_ratio, text) in enumerate(blocks):
        preview = text.strip().replace("\n", " ")[:100]
        st.write(f"**[{i+1}] Font Size:** {size:.2f} | Bold: {bold_ratio:.2%} | length: {len(text.split())} -> `{preview}`")
