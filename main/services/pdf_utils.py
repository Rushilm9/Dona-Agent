import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts plain text from all pages of a PDF using PyMuPDF.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: Concatenated text extracted from all pages.
    """
    text = ""

    # Open the PDF file
    with fitz.open(pdf_path) as doc:
        # Loop through each page and extract text
        for page in doc:
            text += page.get_text()

    # Remove leading/trailing whitespace
    return text.strip()
