from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import uuid
import os
import requests

# ----------------- НАСТРОЙКИ -----------------
PDF_DIR = "pdfs"
IMG_DIR = "images"
FONT_PATH = "DejaVuSans.ttf"

os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

app = FastAPI()
app.mount("/pdfs", StaticFiles(directory=PDF_DIR), name="pdfs")
app.mount("/images", StaticFiles(directory=IMG_DIR), name="images")

pdfmetrics.registerFont(TTFont("DejaVu", FONT_PATH))


# ----------------- МОДЕЛИ -----------------
class PresentationRequest(BaseModel):
    topic: str


# ----------------- ГЕНЕРАЦИЯ КАРТИНКИ -----------------
def generate_image(prompt: str, filename: str):
    """
    🔴 ВОТ ЗДЕСЬ ПОДКЛЮЧАЕТСЯ API ГЕНЕРАЦИИ КАРТИНОК
    """

    # ======= ПРИМЕР (Stable Diffusion / DALL·E / Midjourney API) =======
    # response = requests.post(
    #     "https://api.image-service.com/generate",
    #     headers={"Authorization": "Bearer YOUR_API_KEY"},
    #     json={"prompt": prompt}
    # )
    # image_bytes = response.content

    # ======= ЗАГЛУШКА (чтобы код работал без API) =======
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (1024, 768), color="white")
    d = ImageDraw.Draw(img)
    d.text((50, 50), prompt, fill=(0, 0, 0))
    img.save(filename)


# ----------------- PDF -----------------
def create_presentation_pdf(topic: str):
    filename = f"{uuid.uuid4()}.pdf"
    filepath = os.path.join(PDF_DIR, filename)

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    slides = [
        f"Введение: {topic}",
        f"Почему это важно: {topic}",
        f"Ключевые идеи: {topic}",
        f"Примеры применения: {topic}",
        f"Выводы и итоги: {topic}",
    ]

    for i, text in enumerate(slides):
        img_path = os.path.join(IMG_DIR, f"{i}.png")
        generate_image(text, img_path)

        c.setFont("DejaVu", 20)
        c.drawString(50, height - 50, text)

        c.drawImage(img_path, 50, 150, width=500, preserveAspectRatio=True)
        c.showPage()

    c.save()
    return filename


# ----------------- API -----------------
@app.post("/generate-presentation")
def generate_presentation(data: PresentationRequest):
    pdf_file = create_presentation_pdf(data.topic)
    return {
        "status": "ok",
        "pdf_url": f"/pdfs/{pdf_file}"
    }
