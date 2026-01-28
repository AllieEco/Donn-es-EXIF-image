# EXIF Analyzer API

A small Python service that analyzes image metadata to surface potential
tampering signals for expense receipts and other documents. It extracts EXIF
data, flags common editing traces, and returns a structured JSON response.

## Features

- Extracts EXIF metadata from uploaded images
- Detects common editing indicators (EXIF/XMP software tags)
- Flags PNG uploads as a potential edit signal
- Flags probable screenshots based on filename patterns
- JSON response designed for downstream fraud/risk scoring

## Requirements

- Python 3.10+
- `pip` package manager

## Installation

```bash
pip install fastapi uvicorn pillow
```

## Run the API

```bash
uvicorn api:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## Usage

### Analyze an image

**Endpoint**

```
POST /analyze
```

**Request**

`multipart/form-data` with a `file` field containing the image.

**cURL**

```bash
curl -F "file=@C:\path\to\image.png" http://127.0.0.1:8000/analyze
```

**Python**

```python
import requests

with open(r"C:\path\to\image.png", "rb") as f:
    files = {"file": ("image.png", f, "image/png")}
    resp = requests.post("http://127.0.0.1:8000/analyze", files=files)

print(resp.json())
```

### Response shape

```json
{
  "exif": { "Software": "Canva", "DateTime": "2026:01:28 14:28:34" },
  "format": "png",
  "probable_screenshot": true,
  "probable_editing_png": true,
  "editing_software": {
    "value": "Canva",
    "source": "XMP"
  },
  "warnings": [
    "⚠️ Probable retouche detecte : Fichier de type PNG. ⚠️",
    "⚠️ Probable capture d'ecran (nom de fichier). ⚠️",
    "⚠️ Info: logiciel de retouche detecte (XMP='Canva'). ⚠️"
  ]
}
```

## Notes

- Not all images carry EXIF metadata (e.g., many screenshots).
- Detection signals are heuristics and should be combined with other checks.
