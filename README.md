# Video Overlay API

Этот проект предоставляет API для обработки видео с наложением плашки на основе загруженных файлов или видео, скачанных
по URL. Также поддерживается опциональная настройка языка для обработки видео.

## Функции API

1. **Загрузка видео по URL**  
   Загружает видео по предоставленной ссылке (YouTube, Instagram, TikTok) и сохраняет его на сервере.  
   **Endpoint**: `POST /upload-video-url/`  
   **Параметры**:
    - `url`: URL видео (строка).
    - `video_orientation`: Опциональный параметр ориентации видео, принимает значения `portrait/landscape`, по умолчанию
      `portrait`.
    - `best_quality`: Опциональный параметр, позволяет загрузить отдельно видео и аудио более качественного формата и
      объединить их в один файл используя ffmpeg. По умолчанию false, происходит скачивание сразу видео с аудио.

2. **Загрузка локального видео**  
   Позволяет загрузить локальный видеофайл и сохранить его на сервере.  
   **Endpoint**: `POST /upload-video/`  
   **Параметры**:
    - `file`: Локальный видеофайл (формат `mp4, mov`).

3. **Обработка видео (наложение плашки)**  
   Добавляет плашку или элементы на видео и возвращает результат.
   **Endpoint**: `POST /overlay-video/`  
   **Параметры**:
    - `file_name`: Имя загруженного видео в формате UUID.mp4 (строка).
    - `overlay_type`: Опциональный параметр, позволяет выбрать формат наложения. Возможные варианты `ffmpeg/cv2`, по
      умолчанию `ffmpeg`.

   Если обработанное видео уже существует, оно сразу будет отправлено в ответе.

4. **Скачивание видео с добавленной плашкой**
   Позволяет скачать готовое видео с плашкой
   **Endpoint**: `GET /download-video/{file_name}/`
   **Параметры**:
    - `file_name`: Имя скачиваемого видео в формате UUID.mp4 (строка).

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/your-repo/video-overlay-api.git
   cd video-overlay-api/video_overlay_api
   ```

2. Установите poetry - [инструкция по установке](https://python-poetry.org/docs/#installation)


3. Установите зависимости:
   ```bash
   poetry install
   ```

4. Запустите сервер:

   ```bash
   uvicorn api:app --reload
   ```

Теперь сервер доступен по адресу `http://localhost:8000`.

## Пример использования

1. **Загрузка видео по URL**:
   ```bash
   curl -X 'POST' \
   'http://localhost:8000/upload-video-url/' \
   -H 'Content-Type: application/x-www-form-urlencoded' \
   -d 'url=https://www.youtube.com/watch?v=some_video_id'
   ```

2. **Загрузка видео с локального файла**:
   ```bash
   curl -X 'POST' \
   'http://localhost:8000/upload-video/' \
   -H 'Content-Type: multipart/form-data' \
   -F 'file=@your_video.mp4'
   ```

3. **Обработка видео с наложением плашки**:
   ```bash
   curl -X 'POST' \
   'http://localhost:8000/overlay-video/' \
   -H 'Content-Type: application/x-www-form-urlencoded' \
   -d 'file_id=your_file_id&language=en'
   ```

## Структура проекта

- `api.py` — основной файл API, где обрабатываются запросы.
- `video_downloader.py` — файл для загрузки видео с различных платформ.
- `video_overlay.py` — файл для обработки видео с наложением плашки.

## Лицензия

MIT License