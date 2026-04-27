# clean_xlsx.py
# =============
# Strips identifying metadata from Excel spreadsheets (.xlsx)
# Uses the openpyxl library

from openpyxl import load_workbook

def clean_xlsx(input_path, output_path):
    """
    Removes author, company, and timestamps from an Excel file.
    """
    try:
        # Open the workbook
        wb = load_workbook(input_path)

        # --- Read original metadata ---
        props = wb.properties
        original = {
            "Creator":      props.creator      or "",
            "Last Modified By": props.lastModifiedBy or "",
            "Title":        props.title        or "",
            "Subject":      props.subject      or "",
            "Description":  props.description  or "",
            "Keywords":     props.keywords     or "",
            "Created":      str(props.created) if props.created else "",
            "Modified":     str(props.modified) if props.modified else "",
        }

        # --- Wipe all identifying fields ---
        props.creator         = "Anonymous"
        props.lastModifiedBy  = ""
        props.title           = ""
        props.subject         = ""
        props.description     = ""
        props.keywords        = ""
        props.created         = None
        props.modified        = None

        # --- Save the cleaned workbook ---
        wb.save(output_path)

        # --- Read back cleaned properties ---
        wb2 = load_workbook(output_path)
        props2 = wb2.properties
        cleaned = {
            "Creator":         props2.creator or "",
            "Last Modified By": props2.lastModifiedBy or "",
        }

        removed = [k for k, v in original.items() if v]

        return {
            "success":  True,
            "original": original,
            "cleaned":  cleaned,
            "removed":  removed
        }

    except Exception as e:
        return {"success": False, "error": str(e)}