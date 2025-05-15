from pyresparser import ResumeParser
import spacy
import nltk

nltk.download("stopwords")


def parse_resume(file_path):

    nlp = spacy.load("en_core_web_sm")

    """
    Parses a resume file and extracts relevant information.

    Args:
        file_path (str): The path to the resume file.

    Returns:
        dict: A dictionary containing the parsed information.
    """
    try:
        data = ResumeParser(file_path).get_extracted_data()
        return data
    except Exception as e:
        print(f"Error parsing resume: {e}")
        return {}
