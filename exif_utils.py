import json
import os
import re
import unicodedata
from io import BytesIO
from PIL import Image, ExifTags


def print_exif_json(image_path: str) -> None:
    """Print EXIF data as JSON for the given image path."""
    analysis = analyze_image(image_path)
    for warning in analysis["warnings"]:
        print(warning)
    print(json.dumps(analysis["exif"], ensure_ascii=False, indent=2))


def analyze_image(image_path: str) -> dict:
    """Return structured analysis for an image path."""
    with Image.open(image_path) as image:
        exif = image.getexif()
        image_info = dict(image.info)
        image_format = (image.format or "").lower()
    return _build_analysis(exif, image_info, image_format, image_path)


def analyze_image_bytes(image_bytes: bytes, filename: str | None = None) -> dict:
    """Return structured analysis for an image provided as bytes."""
    with Image.open(BytesIO(image_bytes)) as image:
        exif = image.getexif()
        image_info = dict(image.info)
        image_format = (image.format or "").lower()
    return _build_analysis(exif, image_info, image_format, filename or "")


def _build_analysis(exif, image_info: dict, image_format: str, source_name: str) -> dict:
    tag_map = ExifTags.TAGS
    exif_data = {}
    if exif:
        for tag_id, value in exif.items():
            tag_name = tag_map.get(tag_id, str(tag_id))
            exif_data[tag_name] = _json_safe_exif_value(value)

    warnings = []
    probable_png = image_format == "png"
    probable_screenshot = _is_probable_screenshot(source_name)

    if probable_png:
        warnings.append("⚠️ Probable retouche detecte : Fichier de type PNG. ⚠️")
    if probable_screenshot:
        warnings.append("⚠️ Probable capture d'ecran (nom de fichier). ⚠️")

    software_value = None
    software_source = None
    software = exif_data.get("Software")
    processing_software = exif_data.get("ProcessingSoftware")
    if isinstance(software, str) and software.strip():
        software_value = software.strip()
        software_source = "Software"
    elif isinstance(processing_software, str) and processing_software.strip():
        software_value = processing_software.strip()
        software_source = "ProcessingSoftware"
    else:
        xmp_tool = _extract_xmp_software(image_info)
        if xmp_tool:
            software_value = xmp_tool.strip()
            software_source = "XMP"

    if software_value:
        warnings.append(
            "⚠️ Info: logiciel de retouche detecte "
            f"({software_source}='{software_value}'). ⚠️"
        )

    return {
        "exif": exif_data,
        "format": image_format or None,
        "probable_screenshot": probable_screenshot,
        "probable_editing_png": probable_png,
        "editing_software": {
            "value": software_value,
            "source": software_source,
        },
        "warnings": warnings,
    }


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


def _is_probable_screenshot(image_path: str) -> bool:
    normalized_path = unicodedata.normalize("NFKC", image_path).casefold()
    filename = unicodedata.normalize("NFKC", os.path.basename(image_path)).casefold()
    keywords = (
        "screen-shot",
        "screenshot",
        "capture d'ecran",
        "capture d’ecran",
        "capture d'écran",
        "capture d’écran",
        "capture ecran",
    )
    return any(keyword in filename or keyword in normalized_path for keyword in keywords)
