import fitz  # PyMuPDF
from collections import OrderedDict

def extract_section_index(pdf_path):
    doc = fitz.open(pdf_path)
    index = OrderedDict()

    for i in range(len(doc)):
        page = doc[i]
        text = page.get_text()
        lines = text.split('\n')
        for line in lines:
            if line.strip().startswith("Section"):
                parts = line.strip().split(':', 1)
                if len(parts) == 2:
                    title = parts[0].strip()
                    content = parts[1].strip()
                    if title not in index:
                        index[title + ": " + content] = i + 1  # 1-based page number
    return index

def create_index_page(index_dict):
    # Create a new PDF with the index page
    index_doc = fitz.open()
    index_page = index_doc.new_page()
    
    index_page.insert_text((72, 72), "Index", fontsize=16, fontname="helv", fill=(0, 0, 0))
    y = 100
    for title, page_num in index_dict.items():
        line = f"{title} .......... Page {page_num}"
        index_page.insert_text((72, y), line, fontsize=11, fontname="helv", fill=(0, 0, 0))
        y += 15
        if y > 800:
            index_page = index_doc.new_page()
            y = 72
    return index_doc

def add_index_to_pdf(original_pdf_path, output_pdf_path):
    index = extract_section_index(original_pdf_path)
    index_doc = create_index_page(index)

    # Open original PDF and merge
    original_doc = fitz.open(original_pdf_path)
    final_doc = fitz.open()
    final_doc.insert_pdf(index_doc)
    final_doc.insert_pdf(original_doc)

    final_doc.save(output_pdf_path)
    final_doc.close()

# Example usage
input_pdf = "Pakistan_Penal_Code_1860_Structured.pdf"
output_pdf = "Pakistan_Penal_Code_with_Index.pdf"
add_index_to_pdf(input_pdf, output_pdf)
