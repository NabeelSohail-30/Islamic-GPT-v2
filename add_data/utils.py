import os
from docx import Document
import re


def save_uploaded_file(file):
    """Saves the uploaded file to the 'uploads' directory."""
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    file_path = os.path.join('uploads', file.name)
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return file_path


def extract_headings_and_chunks(doc_path):
    """Extracts headings and chunks from the .docx file, cleans them, and returns the chunks."""

    doc = Document(doc_path)
    chunks = []
    current_heading = None
    current_chunk = []

    heading_font_sizes = {
        'Heading 1': 26,
        'Heading 2': 20,
    }

    for para in doc.paragraphs:
        if is_heading(para, heading_font_sizes):
            if current_heading:
                chunks.append(f'{current_heading}\n\n{
                              " ".join(current_chunk)}')
            current_heading = para.text
            current_chunk = []
        else:
            current_chunk.append(para.text)

    if current_heading:
        chunks.append(f'{current_heading}\n\n{" ".join(current_chunk)}')

    cleaned_chunks = []

    for chunk in chunks:
        cleaned_chunk = remove_references(chunk)
        cleaned_chunks.append(cleaned_chunk)

    return cleaned_chunks


def is_heading(paragraph, heading_font_sizes):
    """Determine if the paragraph is a heading."""
    style_name = paragraph.style.name
    if "Heading" in style_name:
        return True
    font_size = get_font_size(paragraph)
    return font_size in heading_font_sizes.values()


def get_font_size(paragraph):
    """Extract the font size from the paragraph."""
    if paragraph.runs:
        font_size = paragraph.runs[0].font.size
        if font_size:
            return font_size.pt
    return None


def remove_references(text):
    """Removes numbers surrounded by parentheses from the text."""
    return re.sub(r'\(\d+\)', '', text)
