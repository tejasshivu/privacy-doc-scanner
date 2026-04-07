import os
from pypdf import PdfReader, PdfWriter

IDENTIFYING_FIELDS = [
    "/Author",
    "/Creator",
    "/Producer",
    "/CreationDate",
    "/ModDate",
    "/Keywords",
    "/Subject",
    "/Company",
    "/Manager",
    "/Title",
]


def read_pdf_metadata(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        metadata = reader.metadata
        if metadata is None:
            return {}
        return {key: str(value) for key, value in metadata.items()}
    except Exception as e:
        return {"error": str(e)}


def clean_pdf_metadata(input_path, output_path):
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

        removed_fields = [
            key for key in original_metadata
            if key not in cleaned_metadata
        ]

        return {
            "success":  True,
            "original": original_metadata,
            "cleaned":  cleaned_metadata,
            "removed":  removed_fields
        }

    except FileNotFoundError:
        return {
            "success": False,
            "error":   f"File not found: {input_path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error":   str(e)
        }