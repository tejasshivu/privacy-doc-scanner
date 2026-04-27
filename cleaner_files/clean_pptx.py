# clean_pptx.py
# =============
# Strips identifying metadata from PowerPoint files (.pptx)

from pptx import Presentation

def clean_pptx(input_path, output_path):
    try:
        prs = Presentation(input_path)
        props = prs.core_properties

        # --- Read original metadata ---
        original = {}
        try: original["Author"]           = props.author or ""
        except: pass
        try: original["Last Modified By"] = props.last_modified_by or ""
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
        try: props.title            = ""
        except: pass
        try: props.subject          = ""
        except: pass
        try: props.keywords         = ""
        except: pass

        # --- Save cleaned file ---
        prs.save(output_path)

        # --- Read back cleaned metadata ---
        prs2 = Presentation(output_path)
        props2 = prs2.core_properties
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