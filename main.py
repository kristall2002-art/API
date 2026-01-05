from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import uuid
import os

app = FastAPI()

PDF_DIR = "pdfs"
os.makedirs(PDF_DIR, exist_ok=True)

class PdfRequest(BaseModel):
    text: str

@app.get("/")
def home():
    return {"message": "Привет! Сервер работает 🚀"}

@app.post("/generate-pdf")
def generate_pdf(data: PdfRequest):
    filename = f"{uuid.uuid4()}.pdf"
    filepath = os.path.join(PDF_DIR, filename)

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica", 14)
    c.drawString(50, height - 50, data.text)

    c.save()

    return {
        "status": "ok",
        "pdf_url": f"/pdfs/{filename}"
    }

