
import asyncio
import os

from video_overlay import overlay_video
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, Form
from uuid import uuid4
import os
from video_downloader import download_video
from video_overlay import overlay_video
from fastapi.responses import FileResponse


# file = "aa295ce8-b4b5-49eb-9037-9277d98b01a8"

# DOWNLOADS_FOLDER = "downloads"
# OVERLAYS_FOLDER = "overlays"

# input_file = os.path.join(DOWNLOADS_FOLDER, f"{file}.mp4")
# output_file = os.path.join(OVERLAYS_FOLDER, f"{file}_overlayed.mp4")

# overlay_video(input_file, output_file)


DOWNLOADS_FOLDER = "downloads"
OVERLAYS_FOLDER = "overlays"

async def upload_video_url(url: str):
    """
    Загружает видео с указанного URL и сохраняет его с уникальным UUID.
    """
    # file_id = str(uuid4())  # Генерируем уникальный ID
    # output_file = os.path.join(DOWNLOADS_FOLDER, f"{file_id}.mp4")
    filename = download_video(url, DOWNLOADS_FOLDER)
    
    # Переименовываем файл в UUID
    # downloaded_file = next((f for f in os.listdir(DOWNLOADS_FOLDER) if not f.startswith(file_id)), None)
    if filename:
        # os.rename(os.path.join(DOWNLOADS_FOLDER, filename), output_file)
        return {"file_id": filename}
    else:
        return {"error": "Не удалось скачать видео"}
    
async def main ():
    res = await upload_video_url("https://www.youtube.com/shorts/BqfyU0-PdhE")

    print("res")
    print(res)

    await overlay_video(os.path.join(DOWNLOADS_FOLDER, res["file_id"]), os.path.join(OVERLAYS_FOLDER, f"overlay_{res['file_id']}"))

asyncio.run(main())