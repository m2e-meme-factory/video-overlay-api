from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, Form
from uuid import uuid4
import os
from video_downloader import download_video
from video_overlay import overlay_video
from fastapi.responses import StreamingResponse

app = FastAPI()

# Разрешаем запросы с вашего фронтенда
origins = [
    "http://localhost:3050",  # Адрес вашего React приложения
    "http://127.0.0.1:3050",  # Для удобства тестирования на 127.0.0.1
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Разрешённые источники
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все HTTP методы (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"],  # Разрешаем все заголовки
)

# Папки для хранения видео
DOWNLOADS_FOLDER = "downloads"
OVERLAYS_FOLDER = "overlays"

os.makedirs(DOWNLOADS_FOLDER, exist_ok=True)
os.makedirs(OVERLAYS_FOLDER, exist_ok=True)

@app.post("/upload-video-url/")
async def upload_video_url(url: str = Form(...)):
    """
    Загружает видео с указанного URL и сохраняет его с уникальным UUID.
    """
    file_id = str(uuid4())  # Генерируем уникальный ID
    output_file = os.path.join(DOWNLOADS_FOLDER, f"{file_id}.mp4")
    download_video(url, DOWNLOADS_FOLDER)
    
    # Переименовываем файл в UUID
    downloaded_file = next((f for f in os.listdir(DOWNLOADS_FOLDER) if not f.startswith(file_id)), None)
    if downloaded_file:
        os.rename(os.path.join(DOWNLOADS_FOLDER, downloaded_file), output_file)
        return {"file_id": file_id}
    else:
        return {"error": "Не удалось скачать видео"}

@app.post("/upload-video/")
async def upload_video(file: UploadFile):
    """
    Загружает локальный файл, сохраняет его в папку `downloads`.
    """
    file_id = str(uuid4())
    file_path = os.path.join(DOWNLOADS_FOLDER, f"{file_id}.mp4")
    
    # Сохраняем файл
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    return {"file_id": file_id}

@app.post("/overlay-video/")
async def overlay_video_endpoint(file_id: str = Form(...)):
    """
    Обрабатывает видео (наложение `foreground`) и сохраняет результат.
    """
    input_file = os.path.join(DOWNLOADS_FOLDER, f"{file_id}.mp4")
    output_file = os.path.join(OVERLAYS_FOLDER, f"{file_id}_overlayed.mp4")
    
    if os.path.exists(output_file):
        print("send existing")
        return StreamingResponse(open(output_file, "rb"), media_type="video/mp4", headers={"Content-Disposition": f"attachment; filename={file_id}_overlayed.mp4"})
    
    print("process video")
    if not os.path.exists(input_file):
        return {"error": "Файл с таким file_id не найден"}
    
    # Вызываем функцию overlay_video из video_overlay.py
    success = overlay_video(input_file, output_file)
    
    if success:
        # Возвращаем файл как часть ответа, чтобы инициировать его скачивание
        return StreamingResponse(open(output_file, "rb"), media_type="video/mp4", headers={"Content-Disposition": f"attachment; filename={file_id}_overlayed.mp4"})
    else:
        return {"error": "Ошибка обработки видео"}
