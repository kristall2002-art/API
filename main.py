from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import uuid
import os
import time

# ------------------ НАСТРОЙКИ ------------------
PDF_DIR = "pdfs"
FONT_PATH = "DejaVuSans.ttf"

os.makedirs(PDF_DIR, exist_ok=True)

app = FastAPI()
app.mount("/pdfs", StaticFiles(directory=PDF_DIR), name="pdfs")

pdfmetrics.registerFont(TTFont("DejaVu", FONT_PATH))

# ------------------ ПАМЯТЬ ЗАДАЧ ------------------
TASKS = {}  # task_id -> {status, pdf_url}

# ------------------ МОДЕЛИ ------------------
class StartRequest(BaseModel):
    topic: str

# ------------------ ВСПОМОГАТЕЛЬНОЕ ------------------
def generate_pdf(task_id: str, topic: str):
    try:
        TASKS[task_id]["status"] = "processing"

        # имитация тяжёлой работы (картинки / GPT / API)
        time.sleep(5)

        filename = f"{task_id}.pdf"
        filepath = os.path.join(PDF_DIR, filename)

        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4

        slides = [
            f"Презентация: {topic}",
            f"Почему это важно",
            f"Ключевые идеи",
            f"Примеры применения",
            f"Выводы",
        ]

        for text in slides:
            c.setFont("DejaVu", 20)
            c.drawString(50, height - 100, text)
            c.showPage()

        c.save()

        TASKS[task_id]["status"] = "done"
        TASKS[task_id]["pdf_url"] = f"/pdfs/{filename}"

    except Exception as e:
        TASKS[task_id]["status"] = "error"
        TASKS[task_id]["error"] = str(e)

# ------------------ API ------------------

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/start-presentation")
def start_presentation(data: StartRequest, bg: BackgroundTasks):
    task_id = str(uuid.uuid4())

    TASKS[task_id] = {
        "status": "queued",
        "pdf_url": None
    }

    bg.add_task(generate_pdf, task_id, data.topic)

    return {
        "task_id": task_id,
        "status": "queued"
    }

@app.get("/status/{task_id}")
def get_status(task_id: str):
    if task_id not in TASKS:
        return {"status": "not_found"}

    return TASKS[task_id]
