import os
from contextlib import asynccontextmanager
import logging
from typing import Literal
from uuid import uuid4

import aiofiles
import filetype
from asyncer import asyncify
from fastapi import FastAPI, Form, HTTPException, Request, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from constants import (
    ACCEPTED_VIDEO_CONTENT_TYPES,
    ACCEPTED_VIDEO_EXTENSIONS,
    DOWNLOADS_PATH,
    MAX_VIDEO_SIZE,
    OVERLAYS_PATH,
    ORIGINS,
    SupportedOverlayLanguage,
)
from exeptions import (
    BadRequestException,
    BaseApiException,
    FfmpegOverlayError,
    NotFoundException,
    UnsupportedPlatformError,
)
from video_downloader import download_video
from video_overlay import overlay_by_type
from utils import create_video_folders, get_size_in_mb, logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(level=logging.INFO)
    create_video_folders()
    yield


app = FastAPI()


@app.exception_handler(BaseApiException)
async def api_exception_handler(request: Request, exc: BaseApiException):
    return JSONResponse(content={'error': exc.detail}, status_code=exc.status_code)


app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,  # Разрешённые источники
    allow_credentials=True,
    allow_methods=['*'],  # Разрешаем все HTTP методы (GET, POST, PUT, DELETE и т.д.)
    allow_headers=['*'],  # Разрешаем все заголовки
)


@app.post('/upload-video-url/')
async def upload_video_url(
    url: str = Form(...),
    video_orientation: Literal['portrait', 'landscape'] = Form('portrait'),
    best_quality: bool = Form(False),
) -> JSONResponse:
    """
    Загружает видео с указанного URL и сохраняет его с уникальным UUID.
    """
    try:
        thread_download = asyncify(download_video)
        file_name = await thread_download(url=url, best_quality=best_quality, video_orientation=video_orientation)
        return {'file_name': file_name}
    except UnsupportedPlatformError as e:
        raise BadRequestException(f'Не удалось загрузить видео: {e}')
    except Exception:
        raise BadRequestException('Не удалось загрузить видео')


@app.post('/upload-video/')
async def upload_video(file: UploadFile) -> JSONResponse:
    """
    Загружает локальный файл, сохраняет его в папку `downloads`.
    """
    file_name = f'{str(uuid4())}.mp4'
    file_path = os.path.join(DOWNLOADS_PATH, file_name)
    # проверяем соответсвует ли загружаемое видео разрешенным форматам
    file_info = filetype.guess(file.file)
    if file_info is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail='Не удалось определить тип файла',
        )

    detected_extension = file_info.extension.lower()
    if (
        file.content_type not in ACCEPTED_VIDEO_CONTENT_TYPES
        or detected_extension not in ACCEPTED_VIDEO_EXTENSIONS
    ):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f'Неподдерживаемый тип файла - {detected_extension}',
        )

    # загружаем видео, проверяя соответствует ли оно допустимому размеру
    real_file_size = 0
    try:
        async with aiofiles.open(file_path, 'wb') as output_file:
            while content := await file.read(1024 * 1024):
                real_file_size += len(content)
                if real_file_size > MAX_VIDEO_SIZE:
                    max_size_mb = get_size_in_mb(MAX_VIDEO_SIZE)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f'Размер видео превышает допустимый {max_size_mb}Mb'
                    )
                await output_file.write(content)
    except IOError:
        logger.exception('Внутренняя ошика загрузки видео')
        raise BadRequestException('Не удалось загрузить видео')
    finally:
        await file.close()

    return {'file_name': file_name}


@app.post('/overlay-video/')
async def overlay_video_endpoint(
    file_name: str = Form(...),
    language: SupportedOverlayLanguage = Form(SupportedOverlayLanguage.EN),
    overlay_type: Literal['ffmpeg', 'cv2'] = Form('ffmpeg'),
) -> JSONResponse:
    """
    Выполняет наложение видео.
    """
    input_file = os.path.join(DOWNLOADS_PATH, file_name)
    output_file = os.path.join(OVERLAYS_PATH, f'overlay_{file_name}')

    if not os.path.exists(input_file):
        raise NotFoundException(f'Файл {file_name} не найден')

    if os.path.exists(output_file):
        return {'file_name': f'overlay_{file_name}'}

    # Выполнение overlay_video в отдельном потоке (cv2) или в подпроцессе (ffmpeg)
    try:
        await overlay_by_type(input_file, output_file, language=language, overlay_type=overlay_type)
    except FfmpegOverlayError:
        logger.exception('Внутренняя ошика обработки видео')
        raise BadRequestException(f'Ошибка обработки видео')
    except Exception as e:
        raise BadRequestException(f'Ошибка обработки видео: {str(e)}')

    return {'file_name': f'overlay_{file_name}'}


@app.get('/download-video/{file_name}')
async def download_video_endpoint(file_name: str) -> FileResponse:
    """
    Скачивает видео по имени файла из папки overlays.
    """
    file_path = os.path.join(OVERLAYS_PATH, file_name)
    if not os.path.exists(file_path):
        raise NotFoundException(f'Файл {file_name} не найден')

    # Возвращаем файл для скачивания
    return FileResponse(
        file_path,
        media_type='video/mp4',
        headers={'Content-Disposition': f'attachment; filename={file_name}'},
    )
