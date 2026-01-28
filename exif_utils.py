import json
import re
from PIL import Image, ExifTags


def print_exif_json(image_path: str) -> None:
    """Print EXIF data as JSON for the given image path."""
    with Image.open(image_path) as image:
        exif = image.getexif()
        image_info = dict(image.info)

    if not exif:
        print("{}")
        return

    tag_map = ExifTags.TAGS
    exif_data = {}
    for tag_id, value in exif.items():
        tag_name = tag_map.get(tag_id, str(tag_id))
        exif_data[tag_name] = _json_safe_exif_value(value)

    software = exif_data.get("Software")
    processing_software = exif_data.get("ProcessingSoftware")
    if isinstance(software, str) and software.strip():
        print(f"Info: logiciel de retouche detecte (Software='{software}').")
    elif isinstance(processing_software, str) and processing_software.strip():
        print(
            "Info: logiciel de retouche detecte "
            f"(ProcessingSoftware='{processing_software}')."
        )
    else:
        xmp_tool = _extract_xmp_software(image_info)
        if xmp_tool:
            print(f"Info: logiciel de retouche detecte (XMP='{xmp_tool}').")

    print(json.dumps(exif_data, ensure_ascii=False, indent=2))


def _json_safe_exif_value(value):
    if hasattr(value, "numerator") and hasattr(value, "denominator"):
        try:
            return float(value)
        except Exception:
            return f"{value.numerator}/{value.denominator}"
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8")
        except UnicodeDecodeError:
            return value.hex()
    if isinstance(value, tuple):
        return [_json_safe_exif_value(item) for item in value]
    return value


def _extract_xmp_software(image_info: dict) -> str | None:
    xmp_data = (
        image_info.get("XML:com.adobe.xmp")
        or image_info.get("xmp")
        or image_info.get("XMP")
    )
    if not xmp_data:
        return None
    if isinstance(xmp_data, bytes):
        try:
            xmp_text = xmp_data.decode("utf-8", errors="ignore")
        except Exception:
            return None
    else:
        xmp_text = str(xmp_data)

    for tag in ("xmp:CreatorTool", "tiff:Software", "Software"):
        match = re.search(rf"<{tag}>(.*?)</{tag}>", xmp_text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            if value:
                return value
    return None
