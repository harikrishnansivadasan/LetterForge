import re
import string
import logging

def load_text(input_text):
    """
    Loads and cleans input text:
    - strips whitespace
    - Removes extra blank lines
    - Removes non-printable/unwanted characters
    - Removes multiple spaces and newlines
    """
    try:
        if not input_text:
            return ""

        """strip whitespace"""
        text = input_text.strip()

        """Remove non-printable characters"""
        printable = set(string.printable)
        text = "".join(filter(lambda x: x in printable, text))

        """Replace multiple spaces with single space"""
        text = re.sub(r"[ \t]+", " ", text)

        """Replace multiple newlines with a single newline"""
        text = re.sub(r"\n+", "\n", text)

        """Remove leading/trailing spaces on each line"""
        text = "\n".join(line.strip() for line in text.split("\n"))

        """Remove empty lines"""
        text = "\n".join(line for line in text.split("\n") if line.strip())

        return text
    
    except Exception as e:
        logging.error(f"Error loading text: {e}")
        return ""
    
