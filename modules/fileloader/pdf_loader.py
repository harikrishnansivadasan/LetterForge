import pymupdf
import logging
import docx2txt


def load_pdf(uploaded_file):
    """
    Load a PDF file and extract text from each page.

    Args:
        file_path (str): The path to the PDF file.

    Returns:
        list: A list of strings, each representing the text of a page.
    """
    try:
        # Open the PDF file
        pdf_document = pymupdf.open(stream=uploaded_file.read(), filetype="pdf")

        # Extract text from each page
        text_pages = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text = page.get_text()
            text_pages += text

        # Close the PDF document
        pdf_document.close()
        return text_pages
    except Exception as e:
        logging.error(f"Error loading PDF: {e}")
        return ""
