# clean_image.py
# ==============
# Strips EXIF metadata from images (.jpg, .jpeg, .png)
# EXIF data can contain GPS location, camera model, and timestamps
# Uses the Pillow library

from PIL import Image
import io

def clean_image(input_path, output_path):
    """
    Removes ALL EXIF metadata from an image by re-saving it
    without any metadata attached.

    How it works:
        EXIF data is stored alongside the image pixels.
        By opening the image and saving just the pixel data
        (without the EXIF container), all metadata is stripped.
    """
    try:
        # Open the image
        img = Image.open(input_path)

        # --- Read original EXIF metadata ---
        original = {}
        exif_data = img._getexif() if hasattr(img, '_getexif') else None

        # EXIF tags use numeric codes — this maps codes to readable names
        from PIL.ExifTags import TAGS
        if exif_data:
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, str(tag_id))
                # Only show the most identifying fields
                if tag_name in ["Make", "Model", "DateTime", "DateTimeOriginal",
                                 "GPSInfo", "Software", "Artist", "Copyright",
                                 "CameraOwnerName", "BodySerialNumber"]:
                    original[tag_name] = str(value)

        # --- Strip metadata by re-saving pixel data only ---
        # Create a new image from just the pixel data
        # This completely drops the EXIF container
        data = list(img.getdata())
        clean_img = Image.new(img.mode, img.size)
        clean_img.putdata(data)

        # Determine format from file extension
        ext = output_path.rsplit(".", 1)[-1].upper()
        fmt = "JPEG" if ext in ["JPG", "JPEG"] else ext

        clean_img.save(output_path, format=fmt)

        return {
            "success":  True,
            "original": original if original else {"Note": "No EXIF data found"},
            "cleaned":  {},
            "removed":  list(original.keys())
        }

    except Exception as e:
        return {"success": False, "error": str(e)}