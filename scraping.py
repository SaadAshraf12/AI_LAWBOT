import requests
from bs4 import BeautifulSoup
from fpdf import FPDF

# Target URL
url = "https://www.pakistani.org/pakistan/legislation/1860/actXLVof1860.html"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

# Fetch the content
response = requests.get(url, headers=headers)
response.raise_for_status()
soup = BeautifulSoup(response.content, 'html.parser')

# Extract all <td valign="top"> blocks
td_elements = soup.find_all("td", valign="top")

# Prepare PDF
pdf = FPDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.set_font("Arial", size=12)

# Optional: add cover page
pdf.set_font("Arial", 'B', 16)
pdf.multi_cell(0, 10, "Pakistan Penal Code, 1860", align='C')
pdf.ln(10)
pdf.set_font("Arial", '', 12)

# Process each <td>
for i, td in enumerate(td_elements, 1):
    raw_text = td.get_text(separator=" ", strip=True)
    raw_text = raw_text.encode('latin-1', errors='replace').decode('latin-1')
    
    # Extract bold title if exists
    title = ""
    bold_tag = td.find("b")
    if bold_tag:
        title = bold_tag.get_text(strip=True)
        title = title.encode('latin-1', errors='replace').decode('latin-1')
        # Add numbered title
        section_heading = f"Section {i}: {title}"
        pdf.set_font("Arial", 'B', 12)
        pdf.multi_cell(0, 10, section_heading)
        raw_text = raw_text.replace(title, '').strip()

    # Add body text with indentation
    if raw_text:
        pdf.set_font("Arial", '', 12)
        paragraphs = raw_text.split('\n')
        for para in paragraphs:
            para = para.strip()
            if para:
                pdf.multi_cell(0, 8, "    " + para)
        pdf.ln(4)

# Save the structured file
output_file = "Pakistan_Penal_Code_1860_Structured.pdf"
pdf.output(output_file)

print(f"✅ Structured PDF saved as {output_file}")
