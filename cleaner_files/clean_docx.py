# clean_docx.py
# =============
# Strips identifying metadata from Word documents (.docx)

from docx import Document

def clean_docx(input_path, output_path):
    try:
        doc = Document(input_path)
        props = doc.core_properties

        # --- Read original metadata ---
        original = {}
        try: original["Author"]           = props.author or ""
        except: pass
        try: original["Last Modified By"] = props.last_modified_by or ""
        except: pass
        try: original["Company"]          = props.company or ""
        except: pass
        try: original["Title"]            = props.title or ""
        except: pass
        try: original["Subject"]          = props.subject or ""
        except: pass
        try: original["Keywords"]         = props.keywords or ""
        except: pass
        try: original["Created"]          = str(props.created) or ""
        except: pass
        try: original["Modified"]         = str(props.modified) or ""
        except: pass

        # --- Strip identifying fields ---
        try: props.author           = "Anonymous"
        except: pass
        try: props.last_modified_by = ""
        except: pass
        try: props.company          = ""
        except: pass
        try: props.subject          = ""
        except: pass
        try: props.keywords         = ""
        except: pass

        # --- Save cleaned document ---
        doc.save(output_path)

        # --- Read back cleaned metadata ---
        doc2 = Document(output_path)
        props2 = doc2.core_properties
        cleaned = {}
        try: cleaned["Author"]           = props2.author or ""
        except: pass
        try: cleaned["Last Modified By"] = props2.last_modified_by or ""
        except: pass

        removed = [k for k, v in original.items() if v]

        return {
            "success":  True,
            "original": original,
            "cleaned":  cleaned,
            "removed":  removed
        }

    except Exception as e:
        return {"success": False, "error": str(e)}