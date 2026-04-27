# cleaner.py
# ==========
# Main cleaning engine — routes each file type to the right cleaner

import os
from pypdf import PdfReader, PdfWriter

# Import our individual file type cleaners
from cleaner_files.clean_docx  import clean_docx
from cleaner_files.clean_xlsx  import clean_xlsx
from cleaner_files.clean_pptx  import clean_pptx
from cleaner_files.clean_image import clean_image


def read_pdf_metadata(pdf_path):
    """Reads metadata from a PDF file and returns it as a dictionary."""
    try:
        reader = PdfReader(pdf_path)
        metadata = reader.metadata
        if metadata is None:
            return {}
        return {key: str(value) for key, value in metadata.items()}
    except Exception as e:
        return {"error": str(e)}


def clean_pdf_metadata(input_path, output_path):
    """Strips all metadata from a PDF file."""
    try:
        reader = PdfReader(input_path)
        original_metadata = read_pdf_metadata(input_path)

        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        writer.add_metadata({})

        with open(output_path, "wb") as output_file:
            writer.write(output_file)

        cleaned_metadata = read_pdf_metadata(output_path)
        removed_fields = [k for k in original_metadata if k not in cleaned_metadata]

        return {
            "success":  True,
            "original": original_metadata,
            "cleaned":  cleaned_metadata,
            "removed":  removed_fields
        }

    except FileNotFoundError:
        return {"success": False, "error": f"File not found: {input_path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def clean_file(input_path, output_path):
    """
    Master cleaning function — detects file type and calls
    the right cleaner automatically.

    Args:
        input_path  : path to the uploaded file
        output_path : path where the cleaned file should be saved

    Returns:
        A result dict with success, original, cleaned, removed keys
    """
    # Get the file extension (lowercased)
    ext = input_path.rsplit(".", 1)[-1].lower()

    # Route to the correct cleaner based on file type
    if ext == "pdf":
        return clean_pdf_metadata(input_path, output_path)

    elif ext == "docx":
        return clean_docx(input_path, output_path)

    elif ext == "xlsx":
        return clean_xlsx(input_path, output_path)

    elif ext == "pptx":
        return clean_pptx(input_path, output_path)

    elif ext in ["jpg", "jpeg", "png"]:
        return clean_image(input_path, output_path)

    else:
        return {
            "success": False,
            "error":   f"Unsupported file type: .{ext}"
        }