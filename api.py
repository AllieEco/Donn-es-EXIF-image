from fastapi import FastAPI, File, HTTPException, UploadFile

from exif_utils import analyze_image_bytes

app = FastAPI(title="EXIF Analyzer API")


@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)) -> dict:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Fichier non image.")
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Fichier vide.")
    try:
        return analyze_image_bytes(image_bytes, file.filename)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Image invalide: {exc}") from exc
