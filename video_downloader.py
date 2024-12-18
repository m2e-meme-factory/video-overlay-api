import os
from yt_dlp import YoutubeDL

def download_youtube_video(url, output_path="downloads"):
    try:
        # Создаём папку для загрузки, если её нет
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Настройки yt-dlp для скачивания лучшего комбинированного файла
        ydl_opts = {
            "format": "best",  # Скачиваем лучший комбинированный файл (видео и аудио в одном)
            "outtmpl": f"{output_path}/%(title)s.%(ext)s",  # Шаблон имени файла
            "merge_output_format": None,  # Отключаем слияние через FFmpeg
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"Видео с YouTube успешно скачано в папку: {output_path}")
    except Exception as e:
        print(f"Произошла ошибка при скачивании с YouTube: {e}")

def download_instagram_video(url, output_path="downloads"):
    try:
        # Создаём папку для загрузки, если её нет
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Настройки yt-dlp для скачивания видео с Instagram
        ydl_opts = {
            "format": "best",  # Скачиваем лучший комбинированный файл (видео и аудио)
            "outtmpl": f"{output_path}/%(title)s.%(ext)s",  # Шаблон имени файла
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"Видео с Instagram успешно скачано в папку: {output_path}")
    except Exception as e:
        print(f"Произошла ошибка при скачивании с Instagram: {e}")

def download_tiktok_video(url, output_path="downloads"):
    try:
        # Создаём папку для загрузки, если её нет
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Настройки yt-dlp для скачивания видео с TikTok
        ydl_opts = {
            "format": "best",  # Скачиваем лучший комбинированный файл (видео и аудио)
            "outtmpl": f"{output_path}/%(title)s.%(ext)s",  # Шаблон имени файла
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"Видео с TikTok успешно скачано в папку: {output_path}")
    except Exception as e:
        print(f"Произошла ошибка при скачивании с TikTok: {e}")

def download_video(url, output_path="downloads"):
    """Определяет платформу и скачивает видео с соответствующего сайта"""
    try:
        if "youtube.com" in url or "youtu.be" in url:  # Если ссылка с YouTube
            download_youtube_video(url, output_path)
        elif "instagram.com" in url:  # Если ссылка с Instagram
            download_instagram_video(url, output_path)
        elif "tiktok.com" in url:  # Если ссылка с TikTok
            download_tiktok_video(url, output_path)
        else:
            print("Платформа не поддерживается. Пожалуйста, введите ссылку с YouTube, Instagram или TikTok.")
        return True
    except Exception as e:
        print(f"Произошла ошибка: {e}")

    return False
