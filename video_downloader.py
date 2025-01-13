import os
from yt_dlp import YoutubeDL
from uuid import uuid4

def download_youtube_video(url, output_path="downloads"):
    try:
        # Создаём папку для загрузки, если её нет
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        filename= f"{uuid4()}.mp4"
        # Настройки yt-dlp для скачивания лучшего комбинированного файла
        ydl_opts = {
            "format": "best",  # Скачиваем лучший комбинированный файл (видео и аудио в одном)
            "outtmpl": f"{output_path}/{filename}",  # Шаблон имени файла
            "merge_output_format": None,  # Отключаем слияние через FFmpeg
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"Видео с YouTube успешно скачано в папку: {output_path}")
        return filename
    except Exception as e:
        print(f"Произошла ошибка при скачивании с YouTube: {e}")

def download_instagram_video(url, output_path="downloads"):
    try:
        # Создаём папку для загрузки, если её нет
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        filename= f"{uuid4()}.mp4"
        # Настройки yt-dlp для скачивания видео с Instagram
        ydl_opts = {
            "format": "best",  # Скачиваем лучший комбинированный файл (видео и аудио)
            "outtmpl": f"{output_path}/{filename}",  # Шаблон имени файла
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"Видео с Instagram успешно скачано в папку: {output_path}")
        return filename
    except Exception as e:
        print(f"Произошла ошибка при скачивании с Instagram: {e}")

def download_tiktok_video(url, output_path="downloads"):
    try:
        # Создаём папку для загрузки, если её нет
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        filename= f"{uuid4()}.mp4"

        # Настройки yt-dlp для скачивания видео с TikTok
        ydl_opts = {
            "format": "best",  # Скачиваем лучший комбинированный файл (видео и аудио)
            "outtmpl": f"{output_path}/{filename}",  # Шаблон имени файла
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"Видео с TikTok успешно скачано в папку: {output_path}")
        return filename
    except Exception as e:
        print(f"Произошла ошибка при скачивании с TikTok: {e}")

def download_video(url, output_path="downloads"):
    """Определяет платформу и скачивает видео с соответствующего сайта"""
    try:
        if "youtube.com" in url or "youtu.be" in url:  # Если ссылка с YouTube
            file_name = download_youtube_video(url, output_path)
        elif "instagram.com" in url:  # Если ссылка с Instagram
            file_name = download_instagram_video(url, output_path)
        elif "tiktok.com" in url:  # Если ссылка с TikTok
            file_name = download_tiktok_video(url, output_path)
        else:
            print("Платформа не поддерживается. Пожалуйста, введите ссылку с YouTube, Instagram или TikTok.")
        
        print("file_name")
        print(file_name)
        
        # file_id = str(uuid4())
        # os.rename(output_path + "/" + file_name, file_id + ".mp4")
        

        return file_name
    except Exception as e:
        print(f"Произошла ошибка: {e}")

    return False
