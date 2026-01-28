import json
from PIL import Image, ExifTags


def print_exif_json(image_path: str) -> None:
    """Print EXIF data as JSON for the given image path."""
    with Image.open(image_path) as image:
        exif = image.getexif()

    if not exif:
        print("{}")
        return

    tag_map = ExifTags.TAGS
    exif_data = {}
    for tag_id, value in exif.items():
        tag_name = tag_map.get(tag_id, str(tag_id))
        exif_data[tag_name] = _json_safe_exif_value(value)

    print(json.dumps(exif_data, ensure_ascii=False, indent=2))


def _json_safe_exif_value(value):
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8")
        except UnicodeDecodeError:
            return value.hex()
    if isinstance(value, tuple):
        return [_json_safe_exif_value(item) for item in value]
    return value
